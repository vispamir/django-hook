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