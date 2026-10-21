# tests/test_android_packaging.py
# End-to-end and Validation Tests for Track 3: Android TWA & Native APK Packaging
# Package: app.tallypitch.twa | Google Trusted Web Activity

import os
import json
import subprocess
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestAndroidPackaging(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.page = self.browser.new_page()
        self.console_errors = []
        self.page.on("console", lambda msg: self.console_errors.append(msg.text) if msg.type == "error" else None)
        self.page.goto(APP_URL, wait_until="domcontentloaded")

    def tearDown(self):
        self.page.close()
        critical_errors = [e for e in self.console_errors if any(kw in e for kw in ["TypeError", "ReferenceError", "SyntaxError", "is not a function"])]
        self.assertEqual(critical_errors, [], f"Critical console errors observed: {critical_errors}")

    def test_android_project_structure_and_manifest_spec(self):
        """Verify Android TWA project structure, Gradle config, and Digital Asset Links"""
        android_dir = Path("android")
        self.assertTrue(android_dir.exists(), "android/ directory must exist")
        self.assertTrue((android_dir / "build.gradle").exists(), "android/build.gradle must exist")
        self.assertTrue((android_dir / "twa-manifest.json").exists(), "twa-manifest.json must exist")
        self.assertTrue((android_dir / "app" / "build.gradle").exists(), "app/build.gradle must exist")

        # Validate twa-manifest.json
        with open(android_dir / "twa-manifest.json", "r", encoding="utf-8") as f:
            twa = json.load(f)
        self.assertEqual(twa["packageId"], "app.tallypitch.twa")
        self.assertEqual(twa["host"], "tallypitch.app")
        self.assertEqual(twa["name"], "TallyPitch")

        # Validate AndroidManifest.xml
        manifest_path = android_dir / "app" / "src" / "main" / "AndroidManifest.xml"
        self.assertTrue(manifest_path.exists())
        manifest_text = manifest_path.read_text(encoding="utf-8")
        self.assertTrue("app.tallypitch.twa" in manifest_text or "app.tallypitch.mobile" in manifest_text)
        self.assertIn("tallypitch.app", manifest_text)
        self.assertIn("LauncherActivity", manifest_text)

        # Validate Digital Asset Links
        assetlinks_path = Path(".well-known/assetlinks.json")
        self.assertTrue(assetlinks_path.exists())
        with open(assetlinks_path, "r", encoding="utf-8") as f:
            assetlinks = json.load(f)
        self.assertEqual(assetlinks[0]["target"]["package_name"], "app.tallypitch.twa")

    def test_build_android_twa_script_execution(self):
        """Verify Python Android packaging validator script executes cleanly"""
        proc = subprocess.run(["python3", "scripts/build_android_twa.py"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"build_android_twa.py failed: {proc.stderr}")
        self.assertIn("Packaging Verification Passed", proc.stdout)

    def test_android_modal_ui_interaction_and_assetlinks_drawer(self):
        """Verify Modal 10 opens via header CTA, displays TWA cards, toggles AssetLinks JSON, and closes on Escape"""
        page = self.page

        # 1. Check header button
        btn_header = page.locator("#btn-open-android-modal")
        self.assertTrue(btn_header.is_visible())
        self.assertIn("data-tooltip", btn_header.evaluate("el => el.outerHTML"))

        # 2. Click header button to open Modal 10
        btn_header.click()
        modal = page.locator("#android-apk-modal")
        self.assertTrue(modal.is_visible())
        self.assertIn("open", modal.get_attribute("class"))

        # 3. Verify modal action buttons and tooltips
        btn_install = page.locator("#btn-pwa-install-app")
        self.assertTrue(btn_install.is_visible())
        self.assertIn("data-tooltip", btn_install.evaluate("el => el.outerHTML"))

        btn_download = page.locator("#btn-download-apk-spec")
        self.assertTrue(btn_download.is_visible())
        self.assertIn("data-tooltip", btn_download.evaluate("el => el.outerHTML"))

        btn_assetlinks = page.locator("#btn-toggle-assetlinks")
        self.assertTrue(btn_assetlinks.is_visible())
        self.assertIn("data-tooltip", btn_assetlinks.evaluate("el => el.outerHTML"))

        # 4. Toggle AssetLinks drawer
        drawer = page.locator("#assetlinks-drawer")
        self.assertFalse(drawer.is_visible())
        btn_assetlinks.click()
        self.assertTrue(drawer.is_visible())
        self.assertIn("app.tallypitch.twa", page.text_content("#assetlinks-code-block"))

        # 5. Dismiss on Escape key
        page.keyboard.press("Escape")
        self.assertNotIn("open", modal.get_attribute("class") or "")
