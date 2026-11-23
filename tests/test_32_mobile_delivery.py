# tests/test_32_mobile_delivery.py
# Mobile delivery guard: versioned pre-push hook and dist/ Android APK artifact

import os
import unittest
from pathlib import Path

class TestMobileDelivery(unittest.TestCase):
    def test_versioned_pre_push_hook_is_present(self):
        """Ship a versioned pre-push hook so mobile artifacts refresh on every git push."""
        hook = Path(".githooks/pre-push")
        self.assertTrue(hook.exists(), "Missing versioned hook .githooks/pre-push")
        text = hook.read_text(encoding="utf-8")
        self.assertIn("universal-pipeline pre-push hook", text)
        self.assertIn("pipeline.sh", text)
        self.assertTrue(os.access(hook, os.X_OK), ".githooks/pre-push must be executable")

    def test_android_apk_delivery_artifact_in_dist(self):
        """Doctor requires an Android APK under dist/ as the shippable delivery artifact."""
        dist = Path("dist")
        apk_found = list(dist.glob("**/*.apk")) + list(Path(".").glob("*.apk"))
        self.assertTrue(
            apk_found,
            "Android APK delivery artifact is missing from dist/ (expected dist/mobile/*.apk)",
        )
        apk = apk_found[0]
        self.assertGreater(apk.stat().st_size, 1024, f"{apk} is too small to be a real APK")
        self.assertTrue(apk.name.endswith(".apk"))

    def test_gitignore_tracks_dist_mobile_apk(self):
        """dist/mobile APK must not be blanket-ignored or doctor/ship cannot persist it."""
        gitignore = Path(".gitignore").read_text(encoding="utf-8")
        self.assertIn("!dist/mobile/", gitignore)
        self.assertIn("!dist/mobile/*.apk", gitignore)
        self.assertNotIn("\ndist/mobile/\n", "\n" + gitignore)
