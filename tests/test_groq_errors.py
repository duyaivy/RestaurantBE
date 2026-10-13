"""Groq permanent errors fail fast; transient failures can recover."""
import unittest
from unittest.mock import Mock, patch

import requests

from restaurantBE.chatbot.rag.llm import GroqLLMBackend


def response(status, body):
    result = Mock(status_code=status)
    result.json.return_value = body
    if status >= 400:
        result.raise_for_status.side_effect = requests.HTTPError(response=result)
    return result


class GroqErrorTests(unittest.TestCase):
    def setUp(self):
        self.backend = GroqLLMBackend("test-secret", "configured-model", 0.2, 800)
        self.success = response(200, {"choices": [{"message": {"content": ' {"answer":"OK"} '}}]})

    @patch("time.sleep")
    @patch("requests.post")
    def test_permanent_errors_do_not_retry(self, post, sleep):
        for status in (400, 401, 403, 404, 422):
            with self.subTest(status=status):
                post.reset_mock()
                post.return_value = response(status, {
                    "error": {"code": "model_not_found", "message": "No access to configured-model"}
                })
                with self.assertRaisesRegex(RuntimeError, f"Groq HTTP {status}.*model_not_found"):
                    self.backend.generate([], "Return json")
                self.assertEqual(post.call_count, 1)
                sleep.assert_not_called()

    @patch("time.sleep")
    @patch("requests.post")
    def test_transient_errors_retry_then_succeed(self, post, sleep):
        for failure in (
            response(429, {}), response(503, {}), response(504, {}),
            requests.Timeout(), requests.ConnectionError(),
        ):
            with self.subTest(failure=failure):
                post.reset_mock()
                sleep.reset_mock()
                post.side_effect = [failure, self.success]
                self.assertEqual(self.backend.generate([], "Return json"), '{"answer":"OK"}')
                self.assertEqual(post.call_count, 2)
                sleep.assert_called_once_with(2.0)

    @patch("requests.post")
    def test_error_redacts_key(self, post):
        post.return_value = response(404, {"error": {"message": "Bad test-secret"}})
        with self.assertRaises(RuntimeError) as caught:
            self.backend.generate([], "Return json")
        self.assertNotIn("test-secret", str(caught.exception))
        self.assertIn("[REDACTED]", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
