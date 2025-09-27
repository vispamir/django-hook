from .core import HookSystem
from .decorators import register_hook, hook
from .registry import hook_registry

__version__ = "1.0.0"
__all__ = ["HookSystem", "register_hook", "hook", "hook_registry"]
