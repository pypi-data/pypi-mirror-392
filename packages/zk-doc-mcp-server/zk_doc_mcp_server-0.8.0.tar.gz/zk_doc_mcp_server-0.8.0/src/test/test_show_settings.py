"""Test cases for show_settings MCP tool."""

import os
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

try:
    from src.zk_doc_mcp.server import show_settings_impl
    HAS_SHOW_SETTINGS = True
except ImportError:
    HAS_SHOW_SETTINGS = False


class TestShowSettings(unittest.TestCase):
    """Test the show_settings tool."""

    @unittest.skipIf(not HAS_SHOW_SETTINGS, "show_settings not available")
    def test_basic_response_structure(self):
        """Test that show_settings returns correct response structure."""
        result = show_settings_impl()

        self.assertIn("settings", result)
        self.assertIn("summary", result)
        self.assertIsInstance(result["settings"], list)
        self.assertIsInstance(result["summary"], dict)

    @unittest.skipIf(not HAS_SHOW_SETTINGS, "show_settings not available")
    def test_settings_have_required_fields(self):
        """Test that each setting has all required fields."""
        result = show_settings_impl()

        required_fields = ["key", "description", "default_value", "current_value", "type"]

        for setting in result["settings"]:
            for field in required_fields:
                self.assertIn(field, setting, f"Setting {setting.get('key')} missing field: {field}")

    @unittest.skipIf(not HAS_SHOW_SETTINGS, "show_settings not available")
    def test_summary_has_required_fields(self):
        """Test that summary has all required fields."""
        result = show_settings_impl()

        required_summary_fields = ["total_settings", "configured_settings", "default_settings"]

        for field in required_summary_fields:
            self.assertIn(field, result["summary"], f"Summary missing field: {field}")

    @unittest.skipIf(not HAS_SHOW_SETTINGS, "show_settings not available")
    def test_enum_settings_have_enum_values(self):
        """Test that enum type settings include enum_values field."""
        result = show_settings_impl()

        # ZK_DOC_CLONE_METHOD should be an enum
        clone_method = next((s for s in result["settings"] if s["key"] == "ZK_DOC_CLONE_METHOD"), None)
        self.assertIsNotNone(clone_method)
        self.assertEqual(clone_method["type"], "enum")
        self.assertIn("enum_values", clone_method)
        self.assertIn("https", clone_method["enum_values"])
        self.assertIn("ssh", clone_method["enum_values"])

    @unittest.skipIf(not HAS_SHOW_SETTINGS, "show_settings not available")
    @patch.dict(os.environ, {"ZK_DOC_SRC_DIR": "/custom/path"})
    def test_configured_settings_count(self):
        """Test that configured settings are counted correctly."""
        result = show_settings_impl()

        # With ZK_DOC_SRC_DIR set to custom value, it should be configured
        summary = result["summary"]
        self.assertGreaterEqual(summary["configured_settings"], 1,
                               "Expected at least one configured setting")

    @unittest.skipIf(not HAS_SHOW_SETTINGS, "show_settings not available")
    def test_summary_counts_total_settings(self):
        """Test that summary counts total settings correctly."""
        result = show_settings_impl()

        summary = result["summary"]
        total_from_summary = summary["total_settings"]
        total_from_list = len(result["settings"])

        self.assertEqual(total_from_summary, total_from_list,
                        "Total settings in summary should match actual settings count")

    @unittest.skipIf(not HAS_SHOW_SETTINGS, "show_settings not available")
    def test_summary_configured_plus_default_equals_total(self):
        """Test that configured + default settings equals total."""
        result = show_settings_impl()

        summary = result["summary"]
        total = summary["total_settings"]
        configured = summary["configured_settings"]
        default = summary["default_settings"]

        self.assertEqual(configured + default, total,
                        "configured_settings + default_settings should equal total_settings")

    @unittest.skipIf(not HAS_SHOW_SETTINGS, "show_settings not available")
    def test_boolean_settings_format(self):
        """Test that boolean settings display as lowercase true/false."""
        result = show_settings_impl()

        bool_settings = [s for s in result["settings"] if s["type"] == "boolean"]
        self.assertGreater(len(bool_settings), 0, "Expected some boolean settings")

        for setting in bool_settings:
            # Values should be lowercase "true" or "false" strings
            self.assertIn(setting["default_value"].lower(), ["true", "false"],
                         f"Expected true/false for {setting['key']}, got {setting['default_value']}")

    @unittest.skipIf(not HAS_SHOW_SETTINGS, "show_settings not available")
    def test_all_expected_settings_present(self):
        """Test that all expected settings are in response."""
        result = show_settings_impl()

        expected_keys = [
            "ZK_DOC_SRC_DIR",
            "ZK_DOC_VECTOR_DB_DIR",
            "ZK_DOC_FORCE_REINDEX",
            "ZK_DOC_USE_GIT",
            "ZK_DOC_CLONE_METHOD",
            "ZK_DOC_REPO_URL",
            "ZK_DOC_GIT_BRANCH"
        ]

        actual_keys = [s["key"] for s in result["settings"]]

        for expected_key in expected_keys:
            self.assertIn(expected_key, actual_keys,
                         f"Expected setting {expected_key} not found in response")

    @unittest.skipIf(not HAS_SHOW_SETTINGS, "show_settings not available")
    def test_setting_descriptions_not_empty(self):
        """Test that all settings have non-empty descriptions."""
        result = show_settings_impl()

        for setting in result["settings"]:
            self.assertGreater(len(setting["description"]), 0,
                             f"Setting {setting['key']} has empty description")

    @unittest.skipIf(not HAS_SHOW_SETTINGS, "show_settings not available")
    def test_environment_variables_override_defaults(self):
        """Test that environment variables override default values."""
        with patch.dict(os.environ, {"ZK_DOC_CLONE_METHOD": "ssh"}):
            result = show_settings_impl()

            clone_method = next((s for s in result["settings"] if s["key"] == "ZK_DOC_CLONE_METHOD"), None)
            self.assertIsNotNone(clone_method)
            self.assertEqual(clone_method["current_value"], "ssh",
                           "Environment variable should override default value")

    @unittest.skipIf(not HAS_SHOW_SETTINGS, "show_settings not available")
    def test_response_is_serializable_json(self):
        """Test that response is JSON serializable."""
        import json

        result = show_settings_impl()

        # Should not raise an exception
        json_str = json.dumps(result)
        self.assertIsInstance(json_str, str)

        # Should be able to deserialize it back
        deserialized = json.loads(json_str)
        self.assertEqual(deserialized["summary"]["total_settings"],
                        result["summary"]["total_settings"])

    @unittest.skipIf(not HAS_SHOW_SETTINGS, "show_settings not available")
    def test_settings_type_field_valid(self):
        """Test that all settings have valid type values."""
        result = show_settings_impl()

        valid_types = ["string", "boolean", "integer", "enum"]

        for setting in result["settings"]:
            self.assertIn(setting["type"], valid_types,
                         f"Setting {setting['key']} has invalid type: {setting['type']}")

    @unittest.skipIf(not HAS_SHOW_SETTINGS, "show_settings not available")
    def test_src_dir_setting_exists(self):
        """Test that ZK_DOC_SRC_DIR setting exists and has correct properties."""
        result = show_settings_impl()

        src_dir = next((s for s in result["settings"] if s["key"] == "ZK_DOC_SRC_DIR"), None)
        self.assertIsNotNone(src_dir, "ZK_DOC_SRC_DIR setting not found")
        self.assertEqual(src_dir["type"], "string")
        self.assertIn("repo", src_dir["default_value"])

    @unittest.skipIf(not HAS_SHOW_SETTINGS, "show_settings not available")
    def test_vector_db_dir_setting_exists(self):
        """Test that ZK_DOC_VECTOR_DB_DIR setting exists and has correct properties."""
        result = show_settings_impl()

        vector_db = next((s for s in result["settings"] if s["key"] == "ZK_DOC_VECTOR_DB_DIR"), None)
        self.assertIsNotNone(vector_db, "ZK_DOC_VECTOR_DB_DIR setting not found")
        self.assertEqual(vector_db["type"], "string")
        self.assertIn("chroma_db", vector_db["default_value"])

    @unittest.skipIf(not HAS_SHOW_SETTINGS, "show_settings not available")
    def test_use_git_default_is_true(self):
        """Test that ZK_DOC_USE_GIT default is true."""
        result = show_settings_impl()

        use_git = next((s for s in result["settings"] if s["key"] == "ZK_DOC_USE_GIT"), None)
        self.assertIsNotNone(use_git)
        self.assertEqual(use_git["default_value"], "true",
                        "ZK_DOC_USE_GIT should default to true")


if __name__ == '__main__':
    unittest.main()
