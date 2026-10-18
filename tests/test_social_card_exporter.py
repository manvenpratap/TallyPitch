# tests/test_social_card_exporter.py
# End-to-end tests for REA Track: Social Match Graphic & Award Card Exporter (S16)

import os
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestSocialCardExporter(unittest.TestCase):
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

    def test_social_card_modal_elements_and_tooltips(self):
        """Verify modal markup, mode tabs, action buttons and accessible tooltips exist"""
        modal = self.page.locator("#social-card-modal")
        self.assertTrue(modal.count() > 0, "#social-card-modal must exist in DOM")

        # Verify action buttons & tooltips
        download_btn = self.page.locator("#btn-download-social-card")
        copy_btn = self.page.locator("#btn-copy-social-card")
        share_btn = self.page.locator("#btn-share-social-card-api")

        self.assertTrue(download_btn.is_visible(timeout=5000) or modal.count() > 0)
        self.assertEqual(download_btn.get_attribute("data-tooltip"), "Save 1080x1080 high-res PNG image to your device")
        self.assertEqual(copy_btn.get_attribute("data-tooltip"), "Copy 1080x1080 image to clipboard (paste in WhatsApp/Slack)")
        self.assertEqual(share_btn.get_attribute("data-tooltip"), "Share via system share sheet (Mobile / Web Share API)")

        # Verify trigger buttons on S07 and S13
        s07_btn = self.page.locator("#btn-social-card-s07")
        self.assertEqual(s07_btn.get_attribute("data-tooltip"), "Export 1080x1080 social match card for WhatsApp and Instagram")

        s13_btn = self.page.locator("#btn-open-social-s13")
        self.assertEqual(s13_btn.get_attribute("data-tooltip"), "Export high-resolution 1080x1080 match graphic for WhatsApp and Instagram")

    def test_open_social_modal_from_s13_and_render_canvas(self):
        """Verify opening modal from Screen S13 draws 1080x1080 canvas and updates preview image"""
        self.page.click("#tab-S13")
        self.page.wait_for_selector("#screen-S13.active")

        # Click Social Card button
        self.page.click("#btn-open-social-s13")
        self.page.wait_for_selector("#social-card-modal.open")

        # Check canvas dimensions
        canvas_dims = self.page.evaluate("""() => {
            const c = document.getElementById('social-card-canvas');
            const img = document.getElementById('social-card-preview-img');
            return {
                width: c ? c.width : 0,
                height: c ? c.height : 0,
                hasSrc: img && img.src && img.src.startsWith('data:image/png')
            };
        }""")

        self.assertEqual(canvas_dims["width"], 1080, "Canvas width must be 1080")
        self.assertEqual(canvas_dims["height"], 1080, "Canvas height must be 1080")
        self.assertTrue(canvas_dims["hasSrc"], "Preview image must contain rendered data URL")

        # Test escape key dismiss
        self.page.keyboard.press("Escape")
        self.page.wait_for_function("() => !document.getElementById('social-card-modal').classList.contains('open')")

    def test_switch_to_player_award_mode_and_player_select(self):
        """Verify switching mode to Player Award re-renders certificate with selected squad player"""
        self.page.click("#btn-social-card-s07")
        self.page.wait_for_selector("#social-card-modal.open")

        # Switch to Player Award mode
        self.page.click("#tab-social-player")

        player_wrap_visible = self.page.evaluate("""() => {
            const wrap = document.getElementById('social-player-select-wrap');
            return wrap && wrap.style.display !== 'none';
        }""")
        self.assertTrue(player_wrap_visible, "Player selector wrap must be visible in player award mode")

        # Change player in dropdown
        self.page.select_option("#social-card-player-select", "A2")

        has_rendered_new_src = self.page.evaluate("""() => {
            const img = document.getElementById('social-card-preview-img');
            return img && img.src.length > 1000;
        }""")
        self.assertTrue(has_rendered_new_src, "Preview image must be re-rendered for selected player")

        # Download trigger simulation
        download_executed = self.page.evaluate("""() => {
            let clicked = false;
            const originalClick = HTMLAnchorElement.prototype.click;
            HTMLAnchorElement.prototype.click = function() { clicked = true; };
            try {
                downloadSocialCard();
                return clicked;
            } finally {
                HTMLAnchorElement.prototype.click = originalClick;
            }
        }""")
        self.assertTrue(download_executed, "downloadSocialCard() must trigger anchor download")

    def test_match_result_modal_share_trigger(self):
        """Verify completion modal includes direct 'Share Match Graphic (S16)' CTA"""
        result_btn = self.page.locator("#btn-open-social-modal-result")
        self.assertTrue(result_btn.count() > 0, "Share CTA must be present in match-result-modal")
        self.assertEqual(result_btn.get_attribute("data-tooltip"), "Generate and share 1080x1080 match summary graphic")


if __name__ == "__main__":
    unittest.main()
