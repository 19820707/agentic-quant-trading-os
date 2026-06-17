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
        }
        for name, sample in samples.items():
            self.assertRegex(sample, secret_artifact_audit.SECRET_PATTERNS[name])

    def test_generated_cache_file_is_not_text_candidate(self) -> None:
        path = Path("scripts") / "__pycache__" / "secret_artifact_audit.cpython-311.pyc"
        self.assertFalse(secret_artifact_audit.is_text_candidate(path))

    def test_local_virtual_environment_is_skipped(self) -> None:
        path = secret_artifact_audit.ROOT / ".venv" / "Lib" / "site-packages" / "pip" / "_internal"
        self.assertTrue(
            any(part in secret_artifact_audit.SKIPPED_DIRECTORY_NAMES for part in path.relative_to(secret_artifact_audit.ROOT).parts)
        )


if __name__ == "__main__":
    unittest.main()
