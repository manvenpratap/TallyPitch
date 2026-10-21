# tests/test_stadium_sfx_engine.py
# End-to-end and Validation Tests for Track 17: Stadium SFX & Interactive Umpire Audio Soundboard
# Reverse-engineered from CricHeroes assets/sounds/ and SoundManager schemas.
# Covers S07 SFX Toggle, Modal 15 Soundboard, Web Audio API Sound Generation, In-Match Auto-Triggers, and Zero Console Errors.

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestStadiumSfxEngine(unittest.TestCase):
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

    def test_sfx_header_controls_and_soundboard_modal(self):
        """Verify S07 header contains SFX toggle and Soundboard button opening Modal 15."""
        page = self.page
        page.click("#tab-S07")

        # Toggle button
        sfx_toggle = page.locator("#btn-sfx-toggle")
        self.assertTrue(sfx_toggle.is_visible())
        self.assertIn("SFX:", sfx_toggle.inner_text())
        tooltip = sfx_toggle.get_attribute("data-tooltip")
        self.assertIsNotNone(tooltip)

        # Soundboard opener
        board_btn = page.locator("#btn-open-soundboard")
        self.assertTrue(board_btn.is_visible())
        self.assertIn("Soundboard", board_btn.inner_text())

        # Test toggle behavior
        init_text = sfx_toggle.inner_text()
        sfx_toggle.click()
        toggled_text = sfx_toggle.inner_text()
        self.assertNotEqual(init_text, toggled_text)
        # Restore to ON
        sfx_toggle.click()

        # Open Modal 15
        board_btn.click()
        page.wait_for_selector("#soundboard-modal", state="visible")

        # Verify modal controls
        self.assertTrue(page.locator("#sfx-master-toggle").is_visible())
        self.assertTrue(page.locator("#sfx-volume-slider").is_visible())
        self.assertTrue(page.locator("#sfx-volume-val").is_visible())
        self.assertTrue(page.locator("#sfx-active-pill").is_visible())

        # Close modal
        page.click("#soundboard-modal button:has-text('✕')")
        self.assertFalse(page.locator("#soundboard-modal").is_visible())

    def test_soundboard_grid_audio_triggers(self):
        """Verify all 8 soundboard acoustic trigger cards invoke Web Audio API synthesizer."""
        page = self.page
        page.click("#tab-S07")
        page.click("#btn-open-soundboard")
        page.wait_for_selector("#soundboard-modal", state="visible")

        # Hook playStadiumSfx to verify acoustic trigger dispatches
        page.evaluate("""() => {
            window.__last_sfx_dispatched = null;
            const orig = window.playStadiumSfx;
            window.playStadiumSfx = (type) => {
                window.__last_sfx_dispatched = type;
                orig(type);
            };
        }""")

        sound_cards = [
            ("#sfx-btn-four", "four"),
            ("#sfx-btn-six", "six"),
            ("#sfx-btn-wicket", "wicket"),
            ("#sfx-btn-whistle", "over"),
            ("#sfx-btn-toss", "toss"),
            ("#sfx-btn-bat", "dot"),
            ("#sfx-btn-dhol", "dhol"),
            ("#sfx-btn-fanfare", "fanfare"),
        ]

        for selector, expected_type in sound_cards:
            btn = page.locator(selector)
            self.assertTrue(btn.is_visible())
            btn.click()
            dispatched = page.evaluate("() => window.__last_sfx_dispatched")
            self.assertEqual(dispatched, expected_type, f"Expected {expected_type} to be dispatched on clicking {selector}")

        # Test volume slider updates display
        page.evaluate("() => updateSfxVolume(0.5)")
        vol_display = page.locator("#sfx-volume-val").inner_text()
        self.assertEqual(vol_display, "50%")

        # Close modal
        page.click("#soundboard-modal button:has-text('Close')")
        self.assertFalse(page.locator("#soundboard-modal").is_visible())

    def test_in_match_automatic_sfx_scoring_triggers(self):
        """Verify boundary 4s, 6s, dots, and coin toss automatically trigger acoustic sound effects."""
        page = self.page

        # Hook playStadiumSfx call history
        page.evaluate("""() => {
            window.__sfx_history = [];
            const orig = window.playStadiumSfx;
            window.playStadiumSfx = (type) => {
                window.__sfx_history.push(type);
                orig(type);
            };
        }""")

        # Navigate to S07 scoring
        page.click("#tab-S07")

        # Score a 4
        page.click("button.keypad-btn:has-text('4 FOUR!')")
        history = page.evaluate("() => window.__sfx_history")
        self.assertIn("four", history)

        # Score a 6
        page.click("button.keypad-btn:has-text('6 SIX!')")
        history = page.evaluate("() => window.__sfx_history")
        self.assertIn("six", history)

        # Score a dot ball
        page.click("button.keypad-btn:has-text('0 Dot')")
        history = page.evaluate("() => window.__sfx_history")
        self.assertIn("dot", history)

        # Test coin toss virtual spin trigger
        page.evaluate("() => navigate('S05')")
        page.click("button:has-text('Spin Virtual Coin')")
        history = page.evaluate("() => window.__sfx_history")
        self.assertIn("toss", history)

if __name__ == "__main__":
    unittest.main()
