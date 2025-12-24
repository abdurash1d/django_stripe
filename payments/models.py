from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Item(models.Model):
    CURRENCY_CHOICES = [
        ('usd', 'USD'),
        ('eur', 'EUR'),
    ]

    name = models.CharField(max_length=255, help_text="Item name")
    description = models.TextField(help_text="Item description")
    price = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Price in smallest currency unit (cents for USD/EUR)"
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='usd',
        help_text="Currency for the item"
    )

    def __str__(self):
        return f"{self.name} ({self.currency.upper()} {self.price/100:.2f})"

    def get_price_in_dollars(self):
        """Return price in dollar format for display"""
        return f"{self.currency.upper()} {self.price / 100:.2f}"


class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    name = models.CharField(max_length=255, help_text="Discount name")
    description = models.TextField(blank=True, help_text="Discount description")
    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percent',
        help_text="Type of discount"
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Discount value (percentage or fixed amount)"
    )
    currency = models.CharField(
        max_length=3,
        choices=Item.CURRENCY_CHOICES,
        default='usd',
        help_text="Currency for fixed amount discounts"
    )

    def __str__(self):
        if self.discount_type == 'percent':
            return f"{self.name} ({self.value}%)"
        else:
            return f"{self.name} ({self.currency.upper()} {self.value})"


class Tax(models.Model):
    TAX_TYPE_CHOICES = [
        ('percent', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    name = models.CharField(max_length=255, help_text="Tax name")
    description = models.TextField(blank=True, help_text="Tax description")
    tax_type = models.CharField(
        max_length=10,
        choices=TAX_TYPE_CHOICES,
        default='percent',
        help_text="Type of tax"
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Tax value (percentage or fixed amount)"
    )
    currency = models.CharField(
        max_length=3,
        choices=Item.CURRENCY_CHOICES,
        default='usd',
        help_text="Currency for fixed amount taxes"
    )

    def __str__(self):
        if self.tax_type == 'percent':
            return f"{self.name} ({self.value}%)"
        else:
            return f"{self.currency.upper()} {self.value}"


class Order(models.Model):
    items = models.ManyToManyField(Item, related_name='orders', help_text="Items in this order")
    discount = models.ForeignKey(
        Discount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Discount applied to this order"
    )
    tax = models.ForeignKey(
        Tax,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Tax applied to this order"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.items.count()} items"

    def get_total_price(self):
        """Calculate total price of all items in cents"""
        total = sum(item.price for item in self.items.all())

        # Apply discount
        if self.discount:
            if self.discount.discount_type == 'percent':
                total = total * (1 - self.discount.value / 100)
            else:
                total = max(0, total - int(self.discount.value * 100))  # Convert to cents

        # Apply tax
        if self.tax:
            if self.tax.tax_type == 'percent':
                total = total * (1 + self.tax.value / 100)
            else:
                total = total + int(self.tax.value * 100)  # Convert to cents

        return int(total)

    def get_currency(self):
        """Get the currency of the order (assuming all items have same currency)"""
        if self.items.exists():
            return self.items.first().currency
        return 'usd'

    def get_display_total(self):
        """Return formatted total price"""
        currency = self.get_currency()
        total_cents = self.get_total_price()
        return f"{currency.upper()} {total_cents / 100:.2f}"
