# tests/test_pwa_offline.py
# End-to-end tests for Track 3: PWA & Offline Service Worker Infrastructure

import os
import json
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestPwaOffline(unittest.TestCase):
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

    def test_pwa_manifest_and_icons_exist(self):
        """Verify Web App Manifest and PWA icons are valid and properly structured"""
        manifest_path = Path("manifest.json")
        self.assertTrue(manifest_path.exists(), "manifest.json must exist in project root")

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)

        self.assertIn("TallyPitch", manifest_data["name"])
        self.assertEqual(manifest_data["short_name"], "TallyPitch")
        self.assertEqual(manifest_data["display"], "standalone")
        self.assertEqual(manifest_data["theme_color"], "#0f172a")

        # Icons verification
        icons = manifest_data.get("icons", [])
        self.assertGreaterEqual(len(icons), 2)
        sizes = [icon["sizes"] for icon in icons]
        self.assertIn("192x192", sizes)
        self.assertIn("512x512", sizes)

        self.assertTrue(Path("icon-192.png").exists())
        self.assertTrue(Path("icon-512.png").exists())
        self.assertGreater(Path("icon-192.png").stat().st_size, 1000)
        self.assertGreater(Path("icon-512.png").stat().st_size, 1000)

    def test_service_worker_asset_caching_and_registration(self):
        """Verify sw.js contains proper caching lifecycle and index.html includes manifest link"""
        sw_path = Path("sw.js")
        self.assertTrue(sw_path.exists(), "sw.js must exist in project root")
        sw_content = sw_path.read_text(encoding="utf-8")

        self.assertIn("CACHE_NAME", sw_content)
        self.assertIn("STATIC_ASSETS", sw_content)
        self.assertIn("index.html", sw_content)
        self.assertIn("tooltip.js", sw_content)

        page = self.page
        # Verify manifest link tag in DOM
        manifest_link = page.get_attribute("link[rel='manifest']", "href")
        self.assertEqual(manifest_link, "manifest.json")

    def test_network_status_badge_and_tooltip(self):
        """Verify network status indicator badge is visible in header with accessible tooltip"""
        page = self.page
        badge = page.query_selector("#network-status-badge")
        self.assertIsNotNone(badge)
        self.assertTrue(page.is_visible("#network-status-badge"))
        
        badge_text = page.text_content("#network-status-badge")
        self.assertIn("Online", badge_text)
        
        tooltip = badge.get_attribute("data-tooltip")
        self.assertIsNotNone(tooltip)
        self.assertIn("Network Status", tooltip)

if __name__ == "__main__":
    unittest.main()
