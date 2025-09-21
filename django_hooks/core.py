from typing import Any, Callable, Dict, List, Optional, Type
from django.apps import apps
from .registry import hook_registry


class HookSystem:
    """
    Hook management system for Django
    """

    @classmethod
    def invoke(cls, hook_name: str, *args, **kwargs) -> List[Any]:
        """
        Invoke a hook and aggregate results from all implementers

        Args:
            hook_name: Name of the hook
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            List of results from all implementers
        """
        results = []

        for app_name, hook_func in hook_registry.get_hooks(hook_name):
            try:
                result = hook_func(*args, **kwargs)
                results.append(result)
            except Exception as e:
                # Log error but continue executing other django_hooks
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error executing hook {hook_name} in app {app_name}: {e}")

        return results

    @classmethod
    def invoke_aggregate(cls, hook_name: str, aggregator: Callable, *args, **kwargs) -> Any:
        """
        Invoke hook and aggregate results with custom aggregator function

        Args:
            hook_name: Name of the hook
            aggregator: Aggregator function
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Aggregated result
        """
        results = cls.invoke(hook_name, *args, **kwargs)
        return aggregator(results)

    @classmethod
    def get_hook_implementations(cls, hook_name: str) -> List[tuple]:
        """
        Get all implementers of a hook

        Returns:
            List of tuples containing (app_name, hook_function)
        """
        return hook_registry.get_hooks(hook_name)

    @classmethod
    def register_hook(cls, hook_name: str, hook_func: Callable, app_name: Optional[str] = None):
        """
        Manually register a hook

        Args:
            hook_name: Name of the hook
            hook_func: Hook function
            app_name: App name (optional)
        """
        if app_name is None:
            # Use module name if app name not provided
            app_name = hook_func.__module__.split('.')[0]

        hook_registry.register(hook_name, hook_func, app_name)