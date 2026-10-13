"""Regression checks for production host validation; no database/API required."""
import os
import tempfile
import unittest
from unittest.mock import patch

os.environ["DJANGO_SETTINGS_MODULE"] = "restaurantBE.settings.production"
os.environ["ALLOWED_HOSTS"] = " api.example.com , ,localhost "
os.environ["RENDER_EXTERNAL_HOSTNAME"] = " restaurant-host-test.onrender.com "
os.environ["ENV"] = "prod"

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.core.exceptions import DisallowedHost  # noqa: E402
from django.db import OperationalError  # noqa: E402
from django.test import Client, RequestFactory, override_settings  # noqa: E402

from restaurantBE.health import _check_chroma_storage  # noqa: E402


class RenderHostTests(unittest.TestCase):
    def setUp(self):
        cursor_patch = patch("restaurantBE.health.connection.cursor")
        self.cursor = cursor_patch.start()
        self.addCleanup(cursor_patch.stop)
        self.cursor.return_value.__enter__.return_value.fetchone.return_value = (1,)
        redis_patch = patch("restaurantBE.health.Redis.from_url")
        self.redis = redis_patch.start()
        self.addCleanup(redis_patch.stop)
        storage_patch = patch("restaurantBE.health._check_chroma_storage")
        self.storage = storage_patch.start()
        self.addCleanup(storage_patch.stop)

    def test_normalizes_configured_hosts(self):
        self.assertIn("api.example.com", settings.ALLOWED_HOSTS)
        self.assertNotIn("", settings.ALLOWED_HOSTS)
        self.assertNotIn("*", settings.ALLOWED_HOSTS)

    def test_health_accepts_render_custom_and_local_hosts(self):
        for host in (
            "restaurant-host-test.onrender.com",
            "api.example.com",
            "localhost:10000",
            "127.0.0.1:10000",
        ):
            with self.subTest(host=host):
                response = Client().get("/health/", HTTP_HOST=host)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), {
                    "status": "ok", "db": "ok", "redis": "ok", "chroma_storage": "ok",
                })
        self.cursor.return_value.__enter__.return_value.execute.assert_called_with("SELECT 1")

    def test_unknown_host_is_still_rejected(self):
        request = RequestFactory().get("/health/", HTTP_HOST="untrusted.example.net")
        with self.assertRaises(DisallowedHost):
            request.get_host()

    def test_dependency_failure_returns_503_and_logs_redacted_reason(self):
        for component, mock in (("db", self.cursor), ("redis", self.redis), ("chroma_storage", self.storage)):
            with self.subTest(component=component):
                mock.side_effect = OperationalError("unavailable postgres://user:password@db:5432/app private-key")
                with patch.dict(os.environ, {"HEALTH_TEST_API_KEY": "private-key"}):
                    with self.assertLogs("restaurantBE.health", level="ERROR") as logs:
                        response = Client().get("/health/", HTTP_HOST="localhost")
                self.assertEqual(response.status_code, 503)
                self.assertEqual(response.json()[component], "error")
                self.assertEqual(response.json()["status"], "error")
                self.assertNotIn("reason", response.json())
                output = " ".join(logs.output)
                self.assertIn("component=" + component, output)
                self.assertIn("exception=OperationalError", output)
                self.assertNotIn("user:password", output)
                self.assertNotIn("private-key", output)
                mock.side_effect = None

    def test_head_and_healthy_log(self):
        with self.assertLogs("restaurantBE.health", level="INFO") as logs:
            response = Client().head("/health/", HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")
        self.assertIn("method=HEAD", " ".join(logs.output))
        self.assertIn("elapsed_ms=", " ".join(logs.output))

    def test_rejected_host_is_logged_before_health_view(self):
        with self.assertLogs("django.security.DisallowedHost", level="ERROR") as logs:
            response = Client().get("/health/", HTTP_HOST="untrusted.example.net")
        self.assertEqual(response.status_code, 400)
        self.assertIn("untrusted.example.net", " ".join(logs.output))
        self.cursor.assert_not_called()

    def test_storage_probe_leaves_no_files(self):
        with tempfile.TemporaryDirectory() as directory:
            with override_settings(CHATBOT_CHROMA_DIR=directory):
                _check_chroma_storage()
            self.assertEqual(os.listdir(directory), [])


if __name__ == "__main__":
    unittest.main()
