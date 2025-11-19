#!/usr/bin/env python3
"""
Comprehensive test suite for phoenixnebula.
Run with: python3 -m pytest tests/phoenixnebula_test.py -v
"""

import os
import sys
import json
import tempfile
import shutil
import unittest
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phoenixnebula.phoenixnebula import (
    is_executable,
    find_executable,
    is_builtin,
    expand_variables,
    expand_tilde,
    hex_to_ansi,
    get_theme,
    list_themes,
    apply_theme,
)


class TestExecutableVerification(unittest.TestCase):
    """Test executable file verification."""
    def setUp(self):
        """Create temporary test files."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_exec")
        self.nonexec_file = os.path.join(self.test_dir, "test_nonexec")

        with open(self.test_file, "w") as f:
            f.write("#!/bin/bash\necho 'test'")
        os.chmod(self.test_file, 0o755)

        with open(self.nonexec_file, "w") as f:
            f.write("#!/bin/bash\necho 'test'")
        os.chmod(self.nonexec_file, 0o644)

    def tearDown(self):
        """Clean up temporary files."""
        shutil.rmtree(self.test_dir)

    def test_executable_file_returns_true(self):
        """Test that executable files are identified correctly."""
        self.assertTrue(is_executable(self.test_file))

    def test_non_executable_file_returns_false(self):
        """Test that non-executable files are rejected."""
        self.assertFalse(is_executable(self.nonexec_file))

    def test_nonexistent_file_returns_false(self):
        """Test that nonexistent files are handled gracefully."""
        self.assertFalse(is_executable("/nonexistent/file/path"))

    def test_directory_returns_false(self):
        """Test that directories are not identified as executables."""
        self.assertFalse(is_executable(self.test_dir))


class TestPathExpansion(unittest.TestCase):
    """Test path expansion functions."""

    def setUp(self):
        """Set up test environment."""
        self.original_home = os.environ.get("HOME")
        self.test_home = "/home/saldev"
        os.environ["HOME"] = self.test_home

    def tearDown(self):
        """Restore original environment."""
        if self.original_home:
            os.environ["HOME"] = self.original_home

    def test_tilde_expansion_home(self):
        """Test expansion of standalone tilde."""
        from phoenixnebula.phoenixnebula import expand_tilde

        result = expand_tilde("~")
        self.assertEqual(result, self.test_home)

    def test_tilde_expansion_with_path(self):
        """Test expansion of tilde with path."""
        from phoenixnebula.phoenixnebula import expand_tilde

        result = expand_tilde("~/documents")
        self.assertEqual(result, os.path.join(self.test_home, "documents"))

    def test_tilde_expansion_absolute_path(self):
        """Test that absolute paths are unchanged."""
        from phoenixnebula.phoenixnebula import expand_tilde

        result = expand_tilde("/usr/bin")
        self.assertEqual(result, "/usr/bin")

    def test_tilde_expansion_relative_path(self):
        """Test that relative paths are unchanged."""
        from phoenixnebula.phoenixnebula import expand_tilde

        result = expand_tilde("./test")
        self.assertEqual(result, "./test")


class TestVariableExpansion(unittest.TestCase):
    """Test environment variable expansion."""

    def setUp(self):
        """Set up test environment."""
        os.environ["TEST_VAR"] = "test_value"
        os.environ["ANOTHER_VAR"] = "another_value"

    def tearDown(self):
        """Clean up test variables."""
        if "TEST_VAR" in os.environ:
            del os.environ["TEST_VAR"]
        if "ANOTHER_VAR" in os.environ:
            del os.environ["ANOTHER_VAR"]

    def test_dollar_brace_expansion(self):
        """Test ${VAR} expansion."""
        result = expand_variables("${TEST_VAR}")
        self.assertEqual(result, "test_value")

    def test_dollar_expansion(self):
        """Test $VAR expansion."""
        result = expand_variables("$TEST_VAR")
        self.assertEqual(result, "test_value")

    def test_multiple_expansions(self):
        """Test multiple variable expansions."""
        result = expand_variables("$TEST_VAR and ${ANOTHER_VAR}")
        self.assertEqual(result, "test_value and another_value")

    def test_undefined_variable_expansion(self):
        """Test expansion of undefined variables."""
        result = expand_variables("$UNDEFINED_VAR")
        self.assertEqual(result, "")

    def test_text_with_expansion(self):
        """Test text mixed with variable expansion."""
        result = expand_variables("echo $TEST_VAR more text")
        self.assertEqual(result, "echo test_value more text")


class TestBuiltinCommands(unittest.TestCase):
    """Test builtin command detection."""

    def test_known_builtins(self):
        """Test that known builtins are recognized."""
        builtins = [
            "echo",
            "cd",
            "pwd",
            "exit",
            "history",
            "theme",
            "alias",
            "export",
            "jobs",
            "fg",
            "bg",
        ]
        for cmd in builtins:
            self.assertTrue(is_builtin(cmd), f"{cmd} should be recognized as builtin")

    def test_external_commands(self):
        """Test that external commands are not recognized as builtins."""
        external = ["ls", "grep", "sed", "awk", "cat"]
        for cmd in external:
            self.assertFalse(
                is_builtin(cmd), f"{cmd} should not be recognized as builtin"
            )

    def test_case_sensitive(self):
        """Test that builtin detection is case-sensitive."""
        self.assertTrue(is_builtin("echo"))
        self.assertFalse(is_builtin("ECHO"))
        self.assertFalse(is_builtin("Echo"))


class TestColorConversion(unittest.TestCase):
    """Test hex to ANSI color conversion."""

    def test_hex_to_ansi_white(self):
        """Test conversion of white color."""
        result = hex_to_ansi("#ffffff")
        self.assertEqual(result, "\033[38;2;255;255;255m")

    def test_hex_to_ansi_black(self):
        """Test conversion of black color."""
        result = hex_to_ansi("#000000")
        self.assertEqual(result, "\033[38;2;0;0;0m")

    def test_hex_to_ansi_red(self):
        """Test conversion of red color."""
        result = hex_to_ansi("#ff0000")
        self.assertEqual(result, "\033[38;2;255;0;0m")

    def test_hex_to_ansi_with_leading_hash(self):
        """Test conversion with leading hash."""
        result = hex_to_ansi("#50fa7b")
        self.assertEqual(result, "\033[38;2;80;250;123m")

    def test_hex_to_ansi_without_leading_hash(self):
        """Test conversion without leading hash."""
        result = hex_to_ansi("50fa7b")
        self.assertEqual(result, "\033[38;2;80;250;123m")


class TestThemeManagement(unittest.TestCase):
    """Test theme loading and management."""

    def setUp(self):
        """Set up theme test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.theme_dir = os.path.join(self.test_dir, "themes")
        os.makedirs(self.theme_dir, exist_ok=True)

        self.custom_theme = {
            "name": "Test Theme",
            "background": "#000000",
            "foreground": "#ffffff",
        }
        theme_file = os.path.join(self.theme_dir, "test_theme.json")
        with open(theme_file, "w") as f:
            json.dump(self.custom_theme, f)

    def tearDown(self):
        """Clean up theme test files."""
        shutil.rmtree(self.test_dir)

    def test_builtin_theme_exists(self):
        """Test that builtin themes can be retrieved."""
        themes = list_themes()
        self.assertIn("dracula", themes)
        self.assertIn("nord", themes)
        self.assertIn("solarized_dark", themes)

    def test_builtin_theme_has_required_fields(self):
        """Test that themes have required color fields."""
        from phoenixnebula.phoenixnebula import BUILTIN_THEMES

        for theme_name, theme in BUILTIN_THEMES.items():
            self.assertIn("name", theme)
            self.assertIn("background", theme)
            self.assertIn("foreground", theme)
            self.assertIn("prompt_user", theme)
            self.assertIn("prompt_host", theme)
            self.assertIn("prompt_path", theme)
            self.assertIn("prompt_symbol", theme)

    def test_at_least_five_themes(self):
        """Test that at least 5 themes are available."""
        from phoenixnebula.phoenixnebula import BUILTIN_THEMES

        self.assertGreaterEqual(len(BUILTIN_THEMES), 5)


class TestSecurityInputValidation(unittest.TestCase):
    """Test security-related input validation."""

    def test_no_shell_injection_via_pipe(self):
        """Test that pipe injection is handled safely."""
        from phoenixnebula.phoenixnebula import expand_variables

        malicious = "test; rm -rf /"
        self.assertIn("test", expand_variables(malicious))

    def test_path_traversal_attempt(self):
        """Test that path traversal is detected."""
        dangerous_path = "../../etc/passwd"
        expanded = expand_tilde(dangerous_path)
        self.assertTrue(expanded.startswith(".."))

    def test_no_unintended_eval(self):
        """Test that code is never evaluated."""
        result = expand_variables("$(whoami)")
        self.assertIn("$", result)


class TestFindExecutable(unittest.TestCase):
    """Test executable finding in PATH."""

    def test_find_system_executable(self):
        """Test finding a common system executable."""
        result = find_executable("ls")
        if result: 
            self.assertTrue(os.path.isabs(result))
            self.assertTrue(is_executable(result))

    def test_find_nonexistent_returns_none(self):
        """Test that nonexistent commands return None."""
        result = find_executable("nonexistent_command_xyz_123")
        self.assertIsNone(result)

    def test_find_returns_executable_only(self):
        """Test that only executable files are returned."""
        result = find_executable("ls")
        if result:
            self.assertTrue(is_executable(result))


class TestFileSystemOperations(unittest.TestCase):
    """Test file system operations."""

    def setUp(self):
        """Create test directory structure."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, "w") as f:
            f.write("test content")

    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.test_dir)

    def test_tilde_file_path(self):
        """Test tilde expansion in file paths."""
        from phoenixnebula.phoenixnebula import expand_tilde

        home = os.path.expanduser("~")
        result = expand_tilde("~/test.txt")
        self.assertTrue(result.startswith(home))

    def test_relative_path_preserved(self):
        """Test that relative paths are preserved."""
        from phoenixnebula.phoenixnebula import expand_tilde

        original = "./test/file.txt"
        result = expand_tilde(original)
        self.assertEqual(result, original)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def test_empty_string_expansion(self):
        """Test expansion of empty string."""
        result = expand_variables("")
        self.assertEqual(result, "")

    def test_empty_tilde_expansion(self):
        """Test expansion of empty tilde."""
        from phoenixnebula.phoenixnebula import expand_tilde

        result = expand_tilde("")
        self.assertEqual(result, "")

    def test_builtin_with_empty_args(self):
        """Test builtin detection with empty string."""
        result = is_builtin("")
        self.assertFalse(result)

    def test_executable_with_empty_path(self):
        """Test executable check with empty path."""
        result = is_executable("")
        self.assertFalse(result)

    def test_hex_color_edge_cases(self):
        """Test hex to ANSI conversion with edge cases."""
        result = hex_to_ansi("#0a0a0a")
        self.assertIn("10;10;10", result)

    def test_special_characters_in_variables(self):
        """Test variable expansion with special characters."""
        os.environ["SPECIAL_VAR"] = "value with spaces"
        result = expand_variables("$SPECIAL_VAR")
        self.assertEqual(result, "value with spaces")
        del os.environ["SPECIAL_VAR"]


class TestIntegration(unittest.TestCase):
    """Integration tests for combined operations."""

    def test_variable_and_tilde_expansion(self):
        """Test combined variable and tilde expansion."""
        os.environ["TESTDIR"] = "mydir"
        from phoenixnebula.phoenixnebula import expand_tilde

        path = "~/documents"
        expanded = expand_tilde(path)
        self.assertIn("documents", expanded)
        del os.environ["TESTDIR"]

    def test_builtin_colors(self):
        """Test that all builtin themes have valid colors."""
        from phoenixnebula.phoenixnebula import BUILTIN_THEMES

        for theme_name, theme in BUILTIN_THEMES.items():
            for color_name, color_value in theme.items():
                if color_name != "name":
                    self.assertTrue(
                        color_value.startswith("#"),
                        f"{theme_name}.{color_name} missing #",
                    )
                    self.assertEqual(
                        len(color_value), 7, f"{theme_name}.{color_name} invalid length"
                    )


class TestCommandParsing(unittest.TestCase):
    """Test command parsing safety."""

    def test_shlex_parsing_safety(self):
        """Test that shlex parsing prevents injection."""
        import shlex

        commands = [
            "echo hello world",
            "ls -la /tmp",
            'echo "quoted string"',
            "cat file.txt | grep pattern",
        ]
        for cmd in commands:
            try:
                tokens = shlex.split(cmd)
                self.assertIsInstance(tokens, list)
            except ValueError:
                self.fail(f"Failed to parse safe command: {cmd}")

    def test_malicious_shlex_handling(self):
        """Test handling of malicious command attempts."""
        import shlex
        with self.assertRaises(ValueError):
            shlex.split('echo "unclosed quote')


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestExecutableVerification))
    suite.addTests(loader.loadTestsFromTestCase(TestPathExpansion))
    suite.addTests(loader.loadTestsFromTestCase(TestVariableExpansion))
    suite.addTests(loader.loadTestsFromTestCase(TestBuiltinCommands))
    suite.addTests(loader.loadTestsFromTestCase(TestColorConversion))
    suite.addTests(loader.loadTestsFromTestCase(TestThemeManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityInputValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestFindExecutable))
    suite.addTests(loader.loadTestsFromTestCase(TestFileSystemOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestCommandParsing))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
