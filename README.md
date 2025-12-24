# Django Stripe Payments

A Django application that integrates with Stripe for payment processing, supporting both individual items and orders with discounts and taxes.

## Features

- ✅ Django models for Items, Orders, Discounts, and Taxes
- ✅ Stripe Checkout Sessions and Payment Intents
- ✅ Multi-currency support (USD and EUR)
- ✅ Order management with multiple items
- ✅ Discount and tax application
- ✅ Django Admin integration
- ✅ Docker support
- ✅ Environment variable configuration
- ✅ Production-ready setup

## Tech Stack

- **Backend**: Django 6.0
- **Payments**: Stripe API (Test Mode)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Deployment**: Docker + Gunicorn
- **Environment**: python-decouple

## Quick Start

### Local Development (without Docker)

1. **Clone and setup**:
   ```bash
   git clone <your-repo-url>
   cd django_stripe
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your Stripe keys
   ```

3. **Database setup**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Run server**:
   ```bash
   python manage.py runserver
   ```

5. **Access**:
   - App: http://localhost:8000
   - Admin: http://localhost:8000/admin

### Docker Setup

1. **Build and run**:
   ```bash
   docker-compose up --build
   ```

2. **Access**:
   - App: http://localhost:8000
   - Admin: http://localhost:8000/admin

## Environment Variables

Create a `.env` file with the following variables:

```env
# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
SITE_URL=http://localhost:8000

# Stripe API Keys for USD
STRIPE_PUBLISHABLE_KEY_USD=pk_test_your_usd_publishable_key_here
STRIPE_SECRET_KEY_USD=sk_test_your_usd_secret_key_here

# Stripe API Keys for EUR
STRIPE_PUBLISHABLE_KEY_EUR=pk_test_your_eur_publishable_key_here
STRIPE_SECRET_KEY_EUR=sk_test_your_eur_secret_key_here

# Payment method: 'session' or 'intent'
PAYMENT_METHOD=session
```

## Stripe Test Setup

1. **Create Stripe account**: https://stripe.com
2. **Get API keys** from Stripe Dashboard > Developers > API keys
3. **Use test keys** (they start with `pk_test_` and `sk_test_`)
4. **Test cards**:
   - Success: `4242 4242 4242 4242`
   - Declined: `4000 0000 0000 0002`
   - Requires authentication: `4000 0025 0000 3155`

## API Endpoints

### Items
- `GET /item/{id}/` - View item details and buy button
- `GET /buy/{id}/` - Create Stripe session for item purchase

### Orders
- `GET /order/{id}/` - View order details and buy button
- `GET /buy/order/{id}/` - Create Stripe session for order purchase

### Status Pages
- `GET /success/` - Payment success page
- `GET /cancel/` - Payment cancelled page

### Examples

**View Item 1**:
```bash
curl http://localhost:8000/item/1
```

**Buy Item 1**:
```bash
curl http://localhost:8000/buy/1
# Returns: {"id": "cs_test_..."}
```

## Admin Panel

Access Django Admin at `/admin/` with superuser credentials.

### Create Test Data

1. **Create Items**:
   - Go to Admin > Payments > Items
   - Add items with different currencies (USD/EUR)

2. **Create Orders**:
   - Go to Admin > Payments > Orders
   - Add multiple items to an order
   - Optionally attach discounts and taxes

3. **Create Discounts/Taxes**:
   - Support both percentage and fixed amount
   - Currency-specific for fixed amounts

## Deployment

### Production Setup

1. **Environment**:
   - Set `DEBUG=False`
   - Use strong `SECRET_KEY`
   - Configure `ALLOWED_HOSTS`
   - Set `SITE_URL` to your domain

2. **Database**:
   - Switch to PostgreSQL in production
   - Update `DATABASES` in settings.py

3. **Static Files**:
   ```bash
   python manage.py collectstatic
   ```

4. **Gunicorn**:
   ```bash
   gunicorn stripe_payments.wsgi:application --bind 0.0.0.0:8000
   ```

### Docker Production

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  web:
    build: .
    environment:
      - DEBUG=False
      - SECRET_KEY=your-production-secret
      - SITE_URL=https://yourdomain.com
      # ... other env vars
```

## Project Structure

```
django_stripe/
├── payments/                 # Main app
│   ├── models.py            # Item, Order, Discount, Tax models
│   ├── views.py             # API endpoints
│   ├── urls.py              # URL patterns
│   ├── admin.py             # Admin configuration
│   ├── stripe_config.py     # Stripe multi-currency config
│   └── templates/           # HTML templates
├── stripe_payments/         # Django project
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL config
│   └── wsgi.py              # WSGI application
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker image
├── docker-compose.yml      # Docker services
├── .env.example           # Environment template
└── README.md              # This file
```

## Testing

1. **Create test items** in Admin
2. **Visit item pages** and click "Buy Now"
3. **Use Stripe test cards** for payment
4. **Verify success/cancel** redirects

## Multi-Currency Support

- **USD and EUR** supported
- **Separate Stripe keypairs** for each currency
- **Automatic key selection** based on item/order currency
- **Currency-specific discounts/taxes**

## Payment Methods

### Checkout Session (Default)
- Redirects to hosted Stripe checkout
- Supports line items, discounts, taxes
- Better for complex orders

### Payment Intent
- Custom payment form integration
- More control over UI/UX
- Requires additional frontend work

Switch with `PAYMENT_METHOD` environment variable.

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## License

This project is for educational purposes. See Stripe's terms of service for commercial use.

## Support

- Django Docs: https://docs.djangoproject.com/
- Stripe Docs: https://stripe.com/docs
- Stripe Testing: https://stripe.com/docs/testing

---

**Demo URL**: [Your deployed app URL here]
**Admin Credentials**: username: `admin`, password: `admin123`
