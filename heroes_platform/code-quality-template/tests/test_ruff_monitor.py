"""
Tests for Ruff Monitor functionality
"""

from pathlib import Path

from scripts.ruff_monitor import RuffMonitor


class TestRuffMonitor:
    """Test cases for RuffMonitor class"""

    def test_init(self):
        """Test RuffMonitor initialization"""
        monitor = RuffMonitor()
        assert isinstance(monitor.workspace_root, Path)
        assert monitor.workspace_root.exists()

    def test_init_with_custom_path(self):
        """Test RuffMonitor initialization with custom path"""
        custom_path = "."
        monitor = RuffMonitor(custom_path)
        assert monitor.workspace_root == Path(custom_path).resolve()

    def test_check_ruff_installed(self):
        """Test ruff installation check"""
        monitor = RuffMonitor()
        result = monitor.check_ruff_installed()
        assert isinstance(result, bool)

    def test_get_problems_empty(self):
        """Test getting problems when none exist"""
        monitor = RuffMonitor()
        problems = monitor.get_problems()
        assert isinstance(problems, list)

    def test_apply_auto_fixes(self):
        """Test applying auto fixes"""
        monitor = RuffMonitor()
        result = monitor.apply_auto_fixes()
        assert isinstance(result, bool)

    def test_run_monitoring_cycle(self):
        """Test running monitoring cycle"""
        monitor = RuffMonitor()
        result = monitor.run_monitoring_cycle()
        assert isinstance(result, bool)


def test_main_function():
    """Test main function execution"""
    # This test verifies that main function can be called without errors
    from scripts.ruff_monitor import main

    # Main function should not raise exceptions when ruff is available
    try:
        main()
    except SystemExit:
        # SystemExit is expected if ruff is not installed
        pass
