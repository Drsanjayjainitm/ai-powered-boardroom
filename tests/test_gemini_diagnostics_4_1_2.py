import unittest
from utils.gemini_diagnostics import classify_error, check_gemini_connection

class TestDiagnostics(unittest.TestCase):
    def test_status_attr(self):
        e = Exception("secret-value")
        e.status_code = 404
        self.assertIn("HTTP 404", classify_error(e))
        self.assertNotIn("secret", classify_error(e))

    def test_status_from_message(self):
        self.assertIn("HTTP 429", classify_error(Exception("429 RESOURCE_EXHAUSTED; sensitive text")))

    def test_unknown_safe(self):
        self.assertNotIn("PRIVATE", classify_error(Exception("PRIVATE")))

    def test_no_key(self):
        self.assertFalse(check_gemini_connection("", "gemini-3.1-flash-lite")[0])

    def test_invalid_model(self):
        self.assertFalse(check_gemini_connection("test", "bad model name")[0])

if __name__ == "__main__":
    unittest.main()
