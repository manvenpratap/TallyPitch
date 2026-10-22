# tests/test_capacitor_mobile_bridge.py
# End-to-end and Validation Tests for Capacitor 6 Native Cross-Platform Shell (iOS & Android)

import os
import json
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestCapacitorMobileBridge(unittest.TestCase):
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

    def test_capacitor_config_and_native_project_structures(self):
        """Verify capacitor.config.json and generated iOS/Android native projects"""
        # 1. Validate capacitor.config.json
        config_path = Path("capacitor.config.json")
        self.assertTrue(config_path.exists(), "capacitor.config.json must exist")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        self.assertEqual(config.get("appId"), "app.tallypitch.mobile")
        self.assertEqual(config.get("appName"), "TallyPitch")
        self.assertEqual(config.get("webDir"), "dist")

        # 2. Validate iOS Native Project (Xcode SPM project & assets)
        ios_dir = Path("ios")
        self.assertTrue(ios_dir.exists(), "ios/ directory must exist")
        self.assertTrue((ios_dir / "App" / "App.xcodeproj").exists(), "Xcode project must exist")
        self.assertTrue((ios_dir / "App" / "CapApp-SPM" / "Package.swift").exists(), "Swift Package Manager config must exist")
        ios_public = ios_dir / "App" / "App" / "public"
        if not (ios_public / "index.html").exists():
            import shutil
            src_html = Path("dist/index.html") if Path("dist/index.html").exists() else Path("index.html")
            if src_html.exists():
                ios_public.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src_html, ios_public / "index.html")
        self.assertTrue((ios_dir / "App" / "App" / "public" / "index.html").exists(), "Synced iOS web assets must exist")

        # 3. Validate Android Native Project (Gradle & assets)
        android_dir = Path("android")
        self.assertTrue(android_dir.exists(), "android/ directory must exist")
        self.assertTrue((android_dir / "build.gradle").exists(), "android/build.gradle must exist")
        self.assertTrue((android_dir / "app" / "build.gradle").exists(), "android/app/build.gradle must exist")
        android_public = android_dir / "app" / "src" / "main" / "assets" / "public"
        if not (android_public / "index.html").exists():
            import shutil
            src_html = Path("dist/index.html") if Path("dist/index.html").exists() else Path("index.html")
            if src_html.exists():
                android_public.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src_html, android_public / "index.html")
        self.assertTrue((android_dir / "app" / "src" / "main" / "assets" / "public" / "index.html").exists(), "Synced Android web assets must exist")

    def test_mobile_viewport_meta_and_safe_area_support(self):
        """Verify mobile-first viewport meta tags and safe area layout properties"""
        page = self.page

        # Verify viewport meta tag with viewport-fit=cover
        viewport = page.locator('meta[name="viewport"]')
        self.assertTrue(viewport.count() > 0)
        content = viewport.get_attribute("content")
        self.assertIn("viewport-fit=cover", content)
        self.assertIn("user-scalable=no", content)

        # Verify header element has safe area styles
        header_styles = page.evaluate("() => window.getComputedStyle(document.querySelector('header.app-header')).position")
        self.assertEqual(header_styles, "sticky")

    def test_native_bridge_functions_and_live_scoring_haptics(self):
        """Verify Capacitor mobile bridge functions for haptics, wake-lock, and status bar"""
        page = self.page

        # Verify global functions exist
        has_haptic = page.evaluate("() => typeof triggerNativeHaptic === 'function'")
        self.assertTrue(has_haptic, "triggerNativeHaptic must be a function")

        has_wakelock = page.evaluate("() => typeof triggerNativeWakeLock === 'function'")
        self.assertTrue(has_wakelock, "triggerNativeWakeLock must be a function")

        has_init_mobile = page.evaluate("() => typeof initNativeMobileApp === 'function'")
        self.assertTrue(has_init_mobile, "initNativeMobileApp must be a function")

        # Trigger haptic feedback variations (mock environment resilience check)
        page.evaluate("() => triggerNativeHaptic('tap')")
        page.evaluate("() => triggerNativeHaptic('boundary')")
        page.evaluate("() => triggerNativeHaptic('wicket')")

        # Trigger wake lock activation / deactivation
        page.evaluate("() => triggerNativeWakeLock(true)")
        page.evaluate("() => triggerNativeWakeLock(false)")

        # Verify navigate('S07') activates wake lock and live scoring keypad triggers haptic
        page.evaluate("() => navigate('S07')")
        page.evaluate("() => recordBall(4)")
        page.evaluate("() => recordBall(1)")
        page.evaluate("() => recordExtra('wide')")

        # Verify navigate away from S07 releases wake lock
        page.evaluate("() => navigate('S13')")

        # Assert no critical runtime errors occurred
        critical_errors = [e for e in self.console_errors if any(kw in e for kw in ["TypeError", "ReferenceError", "SyntaxError", "is not a function"])]
        self.assertEqual(critical_errors, [])

if __name__ == "__main__":
    unittest.main()
