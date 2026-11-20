import os
import sys
import types
import unittest
from unittest.mock import patch

class CloudAITests(unittest.TestCase):
    def test_secrets_preferred_over_environment(self):
        fake = types.ModuleType("streamlit")
        fake.secrets = {"GEMINI_API_KEY": "secret-value", "GEMINI_MODEL": "gemini-3.1-flash-lite"}
        with patch.dict(sys.modules, {"streamlit": fake}), patch.dict(os.environ, {"GEMINI_API_KEY": "env-value"}):
            sys.modules.pop("utils.cloud_ai", None)
            from utils.cloud_ai import gemini_settings
            self.assertEqual(gemini_settings(), ("secret-value", "gemini-3.1-flash-lite", True))
        sys.modules.pop("utils.cloud_ai", None)

    def test_missing_secrets_uses_environment(self):
        fake = types.ModuleType("streamlit")
        fake.secrets = {}
        with patch.dict(sys.modules, {"streamlit": fake}), patch.dict(os.environ, {"GEMINI_API_KEY": "env-value"}):
            sys.modules.pop("utils.cloud_ai", None)
            from utils.cloud_ai import gemini_settings
            self.assertEqual(gemini_settings()[0], "env-value")
        sys.modules.pop("utils.cloud_ai", None)

    def test_error_classification_no_secret_leak(self):
        from agents.advisors import _safe_provider_error
        error = RuntimeError("API key=secret-value")
        self.assertNotIn("secret-value", _safe_provider_error(error))
