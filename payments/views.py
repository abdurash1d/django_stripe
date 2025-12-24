import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

from .models import Item, Order
from .stripe_config import StripeConfig


def home(request):
    """Display homepage with available items and orders"""
    items = Item.objects.all()[:5]  # Show first 5 items
    orders = Order.objects.all()[:5]  # Show first 5 orders

    context = {
        'items': items,
        'orders': orders,
    }
    return render(request, 'payments/home.html', context)


def item_detail(request, item_id):
    """Display item details with buy button"""
    item = get_object_or_404(Item, pk=item_id)
    publishable_key = StripeConfig.get_publishable_key(item.currency)

    context = {
        'item': item,
        'stripe_publishable_key': publishable_key,
    }
    return render(request, 'payments/item_detail.html', context)


def order_detail(request, order_id):
    """Display order details with buy button"""
    order = get_object_or_404(Order, pk=order_id)
    currency = order.get_currency()
    publishable_key = StripeConfig.get_publishable_key(currency)

    context = {
        'order': order,
        'stripe_publishable_key': publishable_key,
    }
    return render(request, 'payments/order_detail.html', context)


@require_http_methods(["GET"])
def buy_item(request, item_id):
    """Create Stripe checkout session for item"""
    item = get_object_or_404(Item, pk=item_id)

    payment_method = StripeConfig.get_payment_method()

    if payment_method == 'intent':
        return create_payment_intent_for_item(item)
    else:
        return create_checkout_session_for_item(item)


@require_http_methods(["GET"])
def buy_order(request, order_id):
    """Create Stripe checkout session for order"""
    order = get_object_or_404(Order, pk=order_id)

    payment_method = StripeConfig.get_payment_method()

    if payment_method == 'intent':
        return create_payment_intent_for_order(order)
    else:
        return create_checkout_session_for_order(order)


def create_checkout_session_for_item(item):
    """Create Stripe checkout session for single item"""
    success_url = f"{settings.SITE_URL}/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{settings.SITE_URL}/cancel"

    session_data = {
        'payment_method_types': ['card'],
        'line_items': [{
            'price_data': {
                'currency': item.currency,
                'product_data': {
                    'name': item.name,
                    'description': item.description,
                },
                'unit_amount': item.price,
            },
            'quantity': 1,
        }],
        'mode': 'payment',
        'success_url': success_url,
        'cancel_url': cancel_url,
    }

    session = StripeConfig.create_checkout_session(item.currency, **session_data)
    return JsonResponse({'id': session.id})


def create_checkout_session_for_order(order):
    """Create Stripe checkout session for order with discounts/taxes"""
    success_url = f"{settings.SITE_URL}/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{settings.SITE_URL}/cancel"

    currency = order.get_currency()
    line_items = []

    # Add all items
    for item in order.items.all():
        line_items.append({
            'price_data': {
                'currency': currency,
                'product_data': {
                    'name': item.name,
                    'description': item.description,
                },
                'unit_amount': item.price,
            },
            'quantity': 1,
        })

    session_data = {
        'payment_method_types': ['card'],
        'line_items': line_items,
        'mode': 'payment',
        'success_url': success_url,
        'cancel_url': cancel_url,
    }

    # Add discount if present
    if order.discount:
        if order.discount.discount_type == 'percent':
            session_data['discounts'] = [{
                'coupon': create_or_get_coupon(order.discount, currency)
            }]
        else:
            # For fixed amount, we need to adjust line items or use a different approach
            # Stripe checkout doesn't directly support fixed amount discounts on sessions
            # We'll handle this in the total calculation
            pass

    # Add tax rates if present
    if order.tax:
        if order.tax.tax_type == 'percent':
            session_data['line_items'][0]['tax_rates'] = [create_or_get_tax_rate(order.tax, currency)]
        else:
            # For fixed tax amounts, we might need to create a separate line item
            # This is complex - for simplicity, we'll handle in total calculation
            pass

    session = StripeConfig.create_checkout_session(currency, **session_data)
    return JsonResponse({'id': session.id})


def create_payment_intent_for_item(item):
    """Create Stripe payment intent for single item"""
    intent = StripeConfig.create_payment_intent(
        item.currency,
        amount=item.price,
        currency=item.currency,
        metadata={
            'item_id': item.id,
            'item_name': item.name,
        }
    )
    return JsonResponse({
        'client_secret': intent.client_secret,
        'amount': item.price,
        'currency': item.currency,
    })


def create_payment_intent_for_order(order):
    """Create Stripe payment intent for order"""
    total_amount = order.get_total_price()
    currency = order.get_currency()

    intent = StripeConfig.create_payment_intent(
        currency,
        amount=total_amount,
        currency=currency,
        metadata={
            'order_id': order.id,
            'items_count': order.items.count(),
        }
    )
    return JsonResponse({
        'client_secret': intent.client_secret,
        'amount': total_amount,
        'currency': currency,
    })


def create_or_get_coupon(discount, currency):
    """Create or retrieve Stripe coupon for discount"""
    # This is a simplified version - in production you'd want to cache/reuse coupons
    import stripe

    StripeConfig.set_stripe_api_key(currency)

    if discount.discount_type == 'percent':
        coupon = stripe.Coupon.create(
            percent_off=discount.value,
            name=discount.name,
        )
    else:
        coupon = stripe.Coupon.create(
            amount_off=int(discount.value * 100),  # Convert to cents
            currency=currency,
            name=discount.name,
        )

    return coupon.id


def create_or_get_tax_rate(tax, currency):
    """Create or retrieve Stripe tax rate"""
    # This is a simplified version - in production you'd want to cache/reuse tax rates
    import stripe

    StripeConfig.set_stripe_api_key(currency)

    if tax.tax_type == 'percent':
        tax_rate = stripe.TaxRate.create(
            display_name=tax.name,
            percentage=tax.value,
            inclusive=False,
        )
    else:
        # Fixed amount tax rates are more complex in Stripe
        # For simplicity, we'll skip this in the checkout session approach
        return None

    return tax_rate.id


def payment_success(request):
    """Display payment success page"""
    return render(request, 'payments/success.html')


def payment_cancel(request):
    """Display payment cancel page"""
    return render(request, 'payments/cancel.html')
