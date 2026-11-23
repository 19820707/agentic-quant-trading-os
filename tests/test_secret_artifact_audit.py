from pathlib import Path
import unittest

from scripts import secret_artifact_audit


class SecretArtifactAuditTests(unittest.TestCase):
    def test_env_example_is_allowed(self) -> None:
        path = secret_artifact_audit.ROOT / ".env.example"
        self.assertTrue(path.name in secret_artifact_audit.ALLOWED_FILE_NAMES)

    def test_real_env_files_are_blocked(self) -> None:
        self.assertIn(".env", secret_artifact_audit.BLOCKED_FILE_NAMES)
        self.assertIn(".env.production", secret_artifact_audit.BLOCKED_FILE_NAMES)

    def test_model_and_database_artifacts_are_blocked(self) -> None:
        for suffix in (".pt", ".pth", ".ckpt", ".onnx", ".sqlite", ".db", ".parquet"):
            self.assertIn(suffix, secret_artifact_audit.BLOCKED_FILE_SUFFIXES)

    def test_secret_patterns_detect_representative_values(self) -> None:
        samples = {
            "private_key_block": "-----BEGIN " + "PRIVATE KEY-----\nabc\n-----END PRIVATE KEY-----",
            "aws_access_key_id": "AKIA" + "ABCDEFGHIJKLMNOP",
            "github_token": "gh" + "p_abcdefghijklmnopqrstuvwxyz1234567890",
            "openrouter_api_key": "sk" + "-or-v1-abcdefghijklmnopqrstuvwxyz1234567890",
            "generic_secret_assignment": "API" + "_KEY=abcdefghijklmnopqrstuvwxyz123456",
            "prefixed_provider_api_key": "sk" + "-ant-api03-abcdefghijklmnopqrstuvwxyz_12345",
            "google_api_key": "AI" + "zaSyA1234567890abcdefghijklmnopqrstuv",
            "slack_token": "xox" + "b-1234567890-abcdefghijkl",
            "stripe_live_key": "sk" + "_live_abcdefghijklmnop1234",
            "json_web_token": "ey" + "JhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abcdefghijklmnop",
        }
        for name, sample in samples.items():
            self.assertRegex(sample, secret_artifact_audit.SECRET_PATTERNS[name])

    def test_web_and_notebook_files_are_scanned(self) -> None:
        for name in ("index.html", "app.js", "client.ts", "analysis.ipynb", ".env.example", "schema.sql"):
            with self.subTest(name=name):
                self.assertIn(Path(name).suffix, secret_artifact_audit.TEXT_FILE_SUFFIX_ALLOWLIST)

    def test_dashboard_html_is_a_text_candidate(self) -> None:
        path = secret_artifact_audit.ROOT / "apps" / "control-plane-dashboard" / "index.html"
        self.assertTrue(secret_artifact_audit.is_text_candidate(path))

    def test_generated_cache_file_is_not_text_candidate(self) -> None:
        path = Path("scripts") / "__pycache__" / "secret_artifact_audit.cpython-311.pyc"
        self.assertFalse(secret_artifact_audit.is_text_candidate(path))


if __name__ == "__main__":
    unittest.main()
