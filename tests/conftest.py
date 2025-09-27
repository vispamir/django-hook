import pytest
import django
from django.conf import settings

def pytest_configure():
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django_hook',
            ],
            SECRET_KEY='test-secret-key-for-django-hook',
            USE_TZ=True,
            TIME_ZONE='UTC',
        )
        django.setup()


@pytest.fixture(autouse=True)
def reset_hook_registry():
    """Reset hook registry before each test"""
    from django_hook.registry import hook_registry
    # Store original state
    original_hooks = hook_registry._hooks.copy()
    
    # Clear for test
    hook_registry.clear()
    
    yield
    
    # Restore original state
    hook_registry._hooks = original_hooks