# tests/test_scorebook_pdf_engine.py
# End-to-end and Validation Tests for Track 16: Official ICC / BCCI Printable PDF Match Scorebook Generator
# Reverse-engineered from CricHeroes ScorecardPdfExportWorker schema.
# Covers S13 Entry Point, Modal 14, Official Scorebook Sheet, Innings Filtering, Signatures Verification Box, Print Trigger, and Zero Console Errors.

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestScorebookPdfEngine(unittest.TestCase):
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

    def test_scorebook_button_and_modal_opening(self):
        """Verify S13 header has Official Scorebook button and opens Modal 14 with full ICC/BCCI scoresheet."""
        page = self.page
        page.click("#tab-S13")

        btn = page.locator("#btn-print-scorebook")
        self.assertTrue(btn.is_visible())
        tooltip = btn.get_attribute("data-tooltip")
        self.assertIsNotNone(tooltip)
        self.assertIn("scorebook", tooltip.lower())

        # Open Modal 14
        btn.click()
        page.wait_for_selector("#scorebook-modal", state="visible")

        # Verify modal header and toolbar
        self.assertTrue(page.locator("#scorebook-filter-innings").is_visible())
        self.assertTrue(page.locator("#scorebook-chk-officials").is_visible())
        self.assertTrue(page.locator("#btn-trigger-scorebook-print").is_visible())

        # Verify official sheet contents
        sheet = page.locator("#scorebook-print-area")
        self.assertTrue(sheet.is_visible())
        self.assertIn("OFFICIAL CRICKET MATCH SCORESHEET", sheet.inner_text())

        title = page.locator("#scorebook-tournament-title").inner_text()
        self.assertTrue(len(title) > 0)

        toss = page.locator("#scorebook-toss-txt").inner_text()
        self.assertIn("Toss", toss)

        # Check batting, bowling and FOW in sheet
        self.assertTrue(page.locator(".scorebook-print-table").count() >= 2)
        self.assertIn("Fall of Wickets", sheet.inner_text())

        # Check officials verification sign-off blocks
        self.assertTrue(page.locator("#scorebook-sign-cap-a").is_visible())
        self.assertTrue(page.locator("#scorebook-sign-cap-b").is_visible())
        self.assertTrue(page.locator("#scorebook-sign-umpire-1").is_visible())
        self.assertTrue(page.locator("#scorebook-sign-umpire-2").is_visible())
        self.assertTrue(page.locator("#scorebook-sign-scorer").is_visible())

        # Close modal
        page.click("#scorebook-modal button:has-text('✕')")
        self.assertFalse(page.locator("#scorebook-modal").is_visible())

    def test_scorebook_filter_and_officials_toggle(self):
        """Verify innings selector filters displayed blocks and officials checkbox toggles scrutiny box."""
        page = self.page
        page.click("#tab-S13")
        page.click("#btn-print-scorebook")
        page.wait_for_selector("#scorebook-modal", state="visible")

        # Default is both innings
        initial_blocks = page.locator(".scorebook-innings-block").count()
        self.assertEqual(initial_blocks, 2)

        # Filter to Innings 1 only
        page.select_option("#scorebook-filter-innings", "inn1")
        self.assertEqual(page.locator(".scorebook-innings-block").count(), 1)
        self.assertIn("Innings 1:", page.locator(".scorebook-innings-block").first.inner_text())

        # Filter to Innings 2 only
        page.select_option("#scorebook-filter-innings", "inn2")
        self.assertEqual(page.locator(".scorebook-innings-block").count(), 1)
        self.assertIn("Innings 2:", page.locator(".scorebook-innings-block").first.inner_text())

        # Switch back to both
        page.select_option("#scorebook-filter-innings", "both")
        self.assertEqual(page.locator(".scorebook-innings-block").count(), 2)

        # Toggle Officials Verification Box
        self.assertTrue(page.locator(".scorebook-officials-box").is_visible())
        page.uncheck("#scorebook-chk-officials")
        self.assertEqual(page.locator(".scorebook-officials-box").count(), 0)

        page.check("#scorebook-chk-officials")
        self.assertEqual(page.locator(".scorebook-officials-box").count(), 1)

    def test_scorebook_print_trigger_and_result_modal_access(self):
        """Verify print trigger invokes window.print and match result modal provides 1-click access."""
        page = self.page
        page.click("#tab-S13")
        page.click("#btn-print-scorebook")
        page.wait_for_selector("#scorebook-modal", state="visible")

        # Mock window.print
        page.evaluate("() => { window.__test_print_invoked = false; window.print = () => { window.__test_print_invoked = true; }; }")

        # Click print button
        page.click("#btn-trigger-scorebook-print")
        is_printed = page.evaluate("() => window.__test_print_invoked")
        self.assertTrue(is_printed, "window.print() should have been invoked by #btn-trigger-scorebook-print")

        # Close modal
        page.click("#scorebook-modal button:has-text('✕')")
        self.assertFalse(page.locator("#scorebook-modal").is_visible())

        # Test access from Match Result modal
        page.evaluate("() => openModal('match-result-modal')")
        page.wait_for_selector("#match-result-modal", state="visible")

        result_btn = page.locator("#btn-result-scorebook")
        self.assertTrue(result_btn.is_visible())
        result_btn.click()

        # Match result modal should be closed, scorebook modal open
        page.wait_for_selector("#scorebook-modal", state="visible")
        self.assertFalse(page.locator("#match-result-modal").is_visible())

if __name__ == "__main__":
    unittest.main()
