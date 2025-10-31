"""
Tests for the zonk_main module.
Focuses on game initialization and execution flow.
"""

import pytest
from project.assignment_4.zonk_main import main


def test_main_function_exists():
    """Test that main function exists and is callable."""
    # This is a simple test to verify the main function exists
    assert callable(main)


def test_main_module_importable():
    """Test that the main module can be imported without errors."""
    # This test verifies there are no syntax errors in the main module
    try:
        import project.assignment_4.zonk_main

        assert hasattr(project.assignment_4.zonk_main, "main")
    except ImportError as e:
        pytest.fail(f"Failed to import zonk_main: {e}")


def test_main_function_runs_without_crash():
    """Test that main function can be called without crashing."""
    try:
        main()
    except SystemExit:
        # Game called exit(), which is acceptable
        pass
    except Exception as e:
        # Any other exception means there's a problem
        pytest.fail(f"main() crashed with exception: {e}")
