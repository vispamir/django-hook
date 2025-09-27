from typing import Callable, Dict, List, Tuple, Any


class HookRegistry:
    """
    Registry for storing and managing django_hook
    """

    def __init__(self) -> None:
        self._hooks: Dict[str, List[Tuple[str, Callable[..., Any]]]] = {}

    def register(self, hook_name: str, hook_func: Callable[..., Any], app_name: str) -> None:
        """
        Register a new hook

        Args:
            hook_name: Name of the hook
            hook_func: Hook function
            app_name: Application name
        """
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []

        # Check for duplicate registration
        for existing_app, existing_func in self._hooks[hook_name]:
            if existing_app == app_name and existing_func == hook_func:
                return

        self._hooks[hook_name].append((app_name, hook_func))

    def get_hooks(self, hook_name: str) -> List[Tuple[str, Callable[..., Any]]]:
        """
        Get all implementers of a hook

        Returns:
            List of tuples containing (app_name, hook_function)
        """
        return self._hooks.get(hook_name, [])

    def get_all_hooks(self) -> Dict[str, List[Tuple[str, Callable[..., Any]]]]:
        """
        Get all registered django_hook

        Returns:
            Dictionary of all django_hook
        """
        return self._hooks.copy()

    def clear(self) -> None:
        """Clear all django_hook"""
        self._hooks.clear()


# Global registry instance
hook_registry = HookRegistry()
