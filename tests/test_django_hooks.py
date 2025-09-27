import os
import tempfile
from django.test import TestCase
from django.apps import apps
from unittest.mock import patch, MagicMock

# Import the hook system components
from django_hook.core import HookSystem
from django_hook.registry import HookRegistry, hook_registry
from django_hook.decorators import hook, register_hook
from django_hook.utils import (
    aggregate_sum,
    aggregate_list,
    aggregate_dict,
    aggregate_first_non_none,
    aggregate_all,
)


class TestHookRegistry(TestCase):
    def setUp(self):
        # Create a fresh registry for each test
        self.registry = HookRegistry()

    def test_register_and_get_hooks(self):
        """Test registering and retrieving django_hook"""

        def mock_hook_func():
            return "test_result"

        # Register a hook
        self.registry.register("test_hook", mock_hook_func, "test_app")

        # Retrieve the hook
        hooks = self.registry.get_hooks("test_hook")

        self.assertEqual(len(hooks), 1)
        self.assertEqual(hooks[0][0], "test_app")
        self.assertEqual(hooks[0][1], mock_hook_func)

    def test_duplicate_registration(self):
        """Test that duplicate registrations are ignored"""

        def mock_hook_func():
            return "test_result"

        # Register the same hook twice
        self.registry.register("test_hook", mock_hook_func, "test_app")
        self.registry.register("test_hook", mock_hook_func, "test_app")

        # Should only have one registration
        hooks = self.registry.get_hooks("test_hook")
        self.assertEqual(len(hooks), 1)

    def test_get_nonexistent_hook(self):
        """Test retrieving a hook that doesn't exist"""
        hooks = self.registry.get_hooks("nonexistent_hook")
        self.assertEqual(len(hooks), 0)

    def test_clear_registry(self):
        """Test clearing the registry"""

        def mock_hook_func():
            return "test_result"

        self.registry.register("test_hook", mock_hook_func, "test_app")
        self.registry.clear()

        hooks = self.registry.get_hooks("test_hook")
        self.assertEqual(len(hooks), 0)


class TestHookDecorators(TestCase):
    def test_hook_decorator_with_name(self):
        """Test @hook decorator with explicit name"""

        @hook("custom_hook_name")
        def test_function():
            return "decorated"

        # Check if the function was registered
        hooks = hook_registry.get_hooks("custom_hook_name")
        self.assertEqual(len(hooks), 1)
        self.assertEqual(hooks[0][1], test_function)

    def test_hook_decorator_without_name(self):
        """Test @hook decorator using function name"""

        @hook()
        def test_function():
            return "decorated"

        # Check if the function was registered
        hooks = hook_registry.get_hooks("test_function")
        self.assertEqual(len(hooks), 1)
        self.assertEqual(hooks[0][1], test_function)

    def test_register_hook_decorator(self):
        """Test @register_hook decorator"""

        @register_hook("manual_hook", "test_app")
        def test_function():
            return "manual"

        # Check if the function was registered
        hooks = hook_registry.get_hooks("manual_hook")
        self.assertEqual(len(hooks), 1)
        self.assertEqual(hooks[0][0], "test_app")
        self.assertEqual(hooks[0][1], test_function)


class TestHookSystem(TestCase):
    def setUp(self):
        # Clear the registry before each test
        hook_registry.clear()

    def test_invoke_no_hooks(self):
        """Test invoking a hook with no implementations"""
        results = HookSystem.invoke("nonexistent_hook")
        self.assertEqual(results, [])

    def test_invoke_single_hook(self):
        """Test invoking a single hook implementation"""

        def test_hook(arg1):
            return f"processed_{arg1}"

        hook_registry.register("test_hook", test_hook, "test_app")

        results = HookSystem.invoke("test_hook", "value")
        self.assertEqual(results, ["processed_value"])

    def test_invoke_multiple_hooks(self):
        """Test invoking multiple hook implementations"""

        def hook1(arg1):
            return f"hook1_{arg1}"

        def hook2(arg1):
            return f"hook2_{arg1}"

        hook_registry.register("test_hook", hook1, "app1")
        hook_registry.register("test_hook", hook2, "app2")

        results = HookSystem.invoke("test_hook", "value")
        self.assertEqual(len(results), 2)
        self.assertIn("hook1_value", results)
        self.assertIn("hook2_value", results)

    def test_invoke_with_exception(self):
        """Test that exceptions in django_hook don't stop other django_hook"""

        def failing_hook():
            raise ValueError("Intentional error")

        def working_hook():
            return "success"

        hook_registry.register("test_hook", failing_hook, "failing_app")
        hook_registry.register("test_hook", working_hook, "working_app")

        # Should still get results from working django_hook
        with self.assertLogs(level="ERROR") as log:
            results = HookSystem.invoke("test_hook")
            self.assertEqual(results, ["success"])
            self.assertTrue(
                any("Intentional error" in message for message in log.output)
            )

    def test_invoke_aggregate(self):
        """Test invoking django_hook with aggregation"""

        def hook1():
            return 1

        def hook2():
            return 2

        hook_registry.register("test_hook", hook1, "app1")
        hook_registry.register("test_hook", hook2, "app2")

        result = HookSystem.invoke_aggregate("test_hook", aggregate_sum)
        self.assertEqual(result, 3)

    def test_get_hook_implementations(self):
        """Test retrieving hook implementations"""

        def test_hook():
            return "test"

        hook_registry.register("test_hook", test_hook, "test_app")

        implementations = HookSystem.get_hook_implementations("test_hook")
        self.assertEqual(len(implementations), 1)
        self.assertEqual(implementations[0][0], "test_app")
        self.assertEqual(implementations[0][1], test_hook)

    def test_register_hook_manual(self):
        """Test manual hook registration"""

        def test_hook():
            return "manual"

        HookSystem.register_hook("manual_hook", test_hook, "test_app")

        hooks = hook_registry.get_hooks("manual_hook")
        self.assertEqual(len(hooks), 1)
        self.assertEqual(hooks[0][1], test_hook)


class TestAggregators(TestCase):
    def test_aggregate_sum(self):
        """Test sum aggregator"""
        results = [1, 2, 3, 4]
        self.assertEqual(aggregate_sum(results), 10)

    def test_aggregate_list(self):
        """Test list aggregator"""
        results = [[1, 2], [3, 4], 5]
        self.assertEqual(aggregate_list(results), [1, 2, 3, 4, 5])

    def test_aggregate_dict(self):
        """Test dictionary aggregator"""
        results = [{"a": 1}, {"b": 2}, {"a": 3, "c": 4}]
        self.assertEqual(aggregate_dict(results), {"a": 3, "b": 2, "c": 4})

    def test_aggregate_first_non_none(self):
        """Test first non-None aggregator"""
        results = [None, False, "value", "other"]
        self.assertEqual(aggregate_first_non_none(results), False)

        results = [None, None, None]
        self.assertIsNone(aggregate_first_non_none(results))

    def test_aggregate_all(self):
        """Test all results aggregator"""
        results = [1, "two", {"three": 3}]
        self.assertEqual(aggregate_all(results), results)


class TestIntegration(TestCase):
    """Integration tests with Django app loading"""

    def setUp(self):
        hook_registry.clear()

    def test_hook_decorator_integration(self):
        """Test that the @hook decorator works in a simulated app environment"""

        # Simulate an app module
        with tempfile.TemporaryDirectory() as temp_dir:
            app_dir = os.path.join(temp_dir, "test_app")
            os.makedirs(app_dir)

            # Create a django_hook.py file
            hooks_content = """
from django_hook import hook

@hook('app_hook')
def app_specific_hook(value):
    return f"app_processed_{value}"

@hook()
def another_hook():
    return "another_result"
"""
            with open(os.path.join(app_dir, "django_hook.py"), "w") as f:
                f.write(hooks_content)

            # Add to Python path and import
            import sys

            sys.path.insert(0, temp_dir)

            try:
                # Import the module (this should trigger the decorators)
                from test_app.hooks import app_specific_hook, another_hook

                # Check if django_hook were registered
                app_hooks = hook_registry.get_hooks("app_hook")
                another_hooks = hook_registry.get_hooks("another_hook")

                self.assertEqual(len(app_hooks), 1)
                self.assertEqual(len(another_hooks), 1)
                self.assertEqual(app_hooks[0][1], app_specific_hook)
                self.assertEqual(another_hooks[0][1], another_hook)

            finally:
                # Clean up
                sys.path.remove(temp_dir)
                if "test_app" in sys.modules:
                    del sys.modules["test_app"]

    @patch("django_hook.core.hook_registry")
    def test_hook_system_with_mock_registry(self, mock_registry):
        """Test HookSystem with a mocked registry"""
        mock_hook = MagicMock(return_value="mock_result")
        mock_registry.get_hooks.return_value = [("test_app", mock_hook)]

        results = HookSystem.invoke("test_hook", "arg1", kwarg1="value1")

        # Verify the hook was called with correct arguments
        mock_hook.assert_called_once_with("arg1", kwarg1="value1")

        # Verify the results
        self.assertEqual(results, ["mock_result"])

        # Verify registry was queried
        mock_registry.get_hooks.assert_called_once_with("test_hook")


# Test runner
if __name__ == "__main__":
    import django
    from django.conf import settings

    # Configure Django settings if not already configured
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            INSTALLED_APPS=[
                "django_hook",
            ],
            USE_TZ=True,
        )

    django.setup()

    # Run the tests
    import unittest

    unittest.main()
