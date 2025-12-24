import stripe
from decouple import config


class StripeConfig:
    """Configuration class for Stripe settings with multi-currency support"""

    # Stripe keys for different currencies
    KEYS = {
        'usd': {
            'publishable': config('STRIPE_PUBLISHABLE_KEY_USD', default='pk_test_default_usd'),
            'secret': config('STRIPE_SECRET_KEY_USD', default='sk_test_default_usd'),
        },
        'eur': {
            'publishable': config('STRIPE_PUBLISHABLE_KEY_EUR', default='pk_test_default_eur'),
            'secret': config('STRIPE_SECRET_KEY_EUR', default='sk_test_default_eur'),
        }
    }

    @classmethod
    def get_publishable_key(cls, currency='usd'):
        """Get publishable key for specific currency"""
        return cls.KEYS.get(currency.lower(), cls.KEYS['usd'])['publishable']

    @classmethod
    def get_secret_key(cls, currency='usd'):
        """Get secret key for specific currency"""
        return cls.KEYS.get(currency.lower(), cls.KEYS['usd'])['secret']

    @classmethod
    def set_stripe_api_key(cls, currency='usd'):
        """Set the global Stripe API key for specific currency"""
        stripe.api_key = cls.get_secret_key(currency)

    @classmethod
    def get_payment_method(cls):
        """Get payment method configuration (session or intent)"""
        return config('PAYMENT_METHOD', default='session').lower()

    @classmethod
    def create_checkout_session(cls, currency='usd', **kwargs):
        """Create checkout session with proper currency API key"""
        cls.set_stripe_api_key(currency)
        return stripe.checkout.Session.create(**kwargs)

    @classmethod
    def create_payment_intent(cls, currency='usd', **kwargs):
        """Create payment intent with proper currency API key"""
        cls.set_stripe_api_key(currency)
        return stripe.PaymentIntent.create(**kwargs)
