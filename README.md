# Django Hook Package

A powerful and flexible hook system for Django that allows applications to implement and invoke hooks, with results aggregation.

## Features

- **Modular**: Each app can define its own hooks
- **Error-resistant**: Errors in one hook don't stop other hooks from executing
- **Flexible**: Supports different types of result aggregation
- **Simple**: Clean and understandable API
- **Well-documented**: Complete comments and type hints

## Installation

1. Add `django_hook` to your Django project
2. Add to `INSTALLED_APPS` in your `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'django_hook',
    # your other apps
]
```

## Usage

### Defining Hooks

In your app, create a `hooks.py` file and define hooks using the `@hook` decorator:

```python
# app1/django_hook.py
from django_hook import hook

@hook('user_created')
def handle_user_created(user):
    # Send welcome email
    print(f"Welcome email sent to {user.email}")
    return {"status": "email_sent"}

@hook('user_created')
def log_user_creation(user):
    # Log user creation
    print(f"User {user.username} created")
    return {"status": "logged"}
```

### Invoking Hooks

Invoke hooks from anywhere in your code:

```python
from django_hook import HookSystem
from django_hook.utils import aggregate_dict

def create_user_view(request):
    # Create user logic here
    user = create_user(request.POST)
    
    # Invoke hook and get all results
    results = HookSystem.invoke('user_created', user)
    print(results)  # [{'status': 'email_sent'}, {'status': 'logged'}]
    
    # Or with aggregation
    aggregated = HookSystem.invoke_aggregate(
        'user_created', 
        aggregate_dict, 
        user
    )
    print(aggregated)  # Merged dictionary
```

### Available Aggregators

The package includes several built-in aggregators:

- `aggregate_sum()` - Sums numerical results
- `aggregate_list()` - Flattens list results
- `aggregate_dict()` - Merges dictionary results
- `aggregate_first_non_none()` - Returns first non-None result
- `aggregate_all()` - Returns all results as a list

## API Reference

### HookSystem Class

- `HookSystem.invoke(hook_name, *args, **kwargs)` - Invoke a hook
- `HookSystem.invoke_aggregate(hook_name, aggregator, *args, **kwargs)` - Invoke with custom aggregation
- `HookSystem.get_hook_implementations(hook_name)` - Get all hook implementations
- `HookSystem.register_hook(hook_name, hook_func, app_name)` - Manually register a hook

### Decorators

- `@hook(hook_name)` - Decorator to register functions as hooks
- `@register_hook(hook_name, app_name)` - Alternative registration decorator

## Example Use Cases

1. **User lifecycle events** (user_created, user_updated, user_deleted)
2. **Content moderation** (before_publish, after_publish)
3. **Notification systems** (send_notification)
4. **Data validation** (validate_data)
5. **Search index updates** (update_search_index)

## Error Handling

The hook system is designed to be fault-tolerant. If one hook implementation fails, the error is logged but other hooks continue to execute.

## OOP sample

Implement multiple payment methods

### Implement Stripe payment method

```python
# payment_app/stripe/hooks.py
from django_hooks import hook

@hook('payment_method')
class StripePaymentMethod:
    """Stripe payment gateway implementation"""

    def __init__(self):
        self.name = "stripe"
        self.supported_currencies = ['USD', 'EUR', 'GBP']

    def start(self, amount, currency, **kwargs):
        """Start payment process"""
        print(f"Starting Stripe payment: {amount} {currency}")
        return {
            'status': 'started',
            'gateway': 'stripe',
            'payment_id': f"stripe_{kwargs.get('order_id', 'unknown')}",
            'next_action': 'redirect_to_stripe'
        }

    def verify(self, payment_id, **kwargs):
        """Verify payment"""
        print(f"Verifying Stripe payment: {payment_id}")
        return {
            'status': 'verified',
            'gateway': 'stripe',
            'payment_id': payment_id,
            'verified_at': '2024-01-01 10:00:00'
        }

    def refund(self, payment_id, amount, **kwargs):
        """Process refund"""
        print(f"Processing Stripe refund: {payment_id} - {amount}")
        return {
            'status': 'refunded',
            'gateway': 'stripe',
            'refund_id': f"refund_{payment_id}"
        }

    def get_supported_methods(self):
        """Get supported payment methods"""
        return ['card', 'apple_pay', 'google_pay']
```

### Implement PayPal payment method

```python
# payment_app/paypal/hooks.py
from django_hooks import hook

@hook('payment_method')
class PayPalPaymentMethod:
    """PayPal payment gateway implementation"""

    def __init__(self):
        self.name = "paypal"
        self.supported_currencies = ['USD', 'EUR', 'AUD', 'CAD']

    def start(self, amount, currency, **kwargs):
        """Start payment process"""
        print(f"Starting PayPal payment: {amount} {currency}")
        return {
            'status': 'started',
            'gateway': 'paypal',
            'payment_id': f"paypal_{kwargs.get('order_id', 'unknown')}",
            'next_action': 'redirect_to_paypal'
        }

    def verify(self, payment_id, **kwargs):
        """Verify payment"""
        print(f"Verifying PayPal payment: {payment_id}")
        return {
            'status': 'verified',
            'gateway': 'paypal',
            'payment_id': payment_id,
            'verified_at': '2024-01-01 10:00:00'
        }

    def cancel(self, payment_id, **kwargs):
        """Cancel pending payment"""
        print(f"Canceling PayPal payment: {payment_id}")
        return {
            'status': 'cancelled',
            'gateway': 'paypal',
            'payment_id': payment_id
        }
```

### Invoke payment methods

```python
# payment_app/services/payment_service.py
from django_hooks import HookSystem
from django_hooks.utils import aggregate_dict, aggregate_list

class PaymentService:

    @staticmethod
    def get_available_payment_methods(currency='USD'):
        """Get all available payment methods for a currency"""
        methods = []

        for app_name, payment_class in HookSystem.invoke('payment_method'):
            instance = payment_class()
            if currency in instance.supported_currencies:
                methods.append({
                    'name': instance.name,
                    'gateway': instance.name,
                    'supported_currencies': instance.supported_currencies,
                    'supported_methods': getattr(instance, 'get_supported_methods', lambda: [])()
                })

        return methods

    @staticmethod
    def start_payment(method_name, amount, currency, **kwargs):
        try:
            method = self.get_available_payment_methods()[method_name]
        except KeyError:
            raise ValueError(f"Method {method_name} not found")

        """Start payment with specific gateway"""
        response = method.start(amount, currency)

        if response:
            return response
        else:
            raise ValueError(f"Payment gateway '{method_name}' not found or not supported")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - feel free to use this package in your commercial projects.

## Support

If you have any questions or issues, please create an issue in the GitHub repository.