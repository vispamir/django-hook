from typing import Callable, Optional
from django.apps import apps
from .registry import hook_registry


def hook(hook_name: Optional[str] = None):
    """
    Decorator for registering functions as django_hooks

    Usage:
        @hook('my_custom_hook')
        def my_hook_function(arg1, arg2):
            return something
    """

    def decorator(func: Callable):
        nonlocal hook_name
        if hook_name is None:
            hook_name = func.__name__

        # Extract app name from function module
        app_name = func.__module__.split('.')[0]

        hook_registry.register(hook_name, func, app_name)
        return func

    return decorator


def register_hook(hook_name: str, app_name: Optional[str] = None):
    """
    Helper function for manual hook registration
    """

    def decorator(func: Callable):
        nonlocal app_name
        if app_name is None:
            app_name = func.__module__.split('.')[0]

        hook_registry.register(hook_name, func, app_name)
        return func

    return decorator