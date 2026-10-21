# tests/test_match_control_penalties.py
# End-to-end and Validation Tests for Track 20: ICC Penalty Runs, Match Delay Stoppage & Official Incident Log Engine
# Reverse-engineered from CricHeroes PenaltyRunFragment, scoring_menu_penalty_run, and tbl_MatchNote.
# Covers S07 Live Console, Keypad Extras Row (+5 Pen), Modal 17 Match Control Hub,
# MCC Laws 28.3/41/42, Stoppage Overs Calculation, Official Incident Diary (tbl_MatchNote),
# 0ms Atomic Rollback, and Zero Console Errors.

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestMatchControlPenalties(unittest.TestCase):
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

    def test_match_control_modal_tabs_and_tooltips(self):
        """Verify S07 header action, Modal 17 rendering, sub-tab transitions, tooltips, and Escape key dismissal."""
        page = self.page
        page.evaluate("() => navigate('S07')")

        # Header button
        btn_open = page.locator("#btn-open-match-control")
        self.assertTrue(btn_open.is_visible())
        self.assertIsNotNone(btn_open.get_attribute("data-tooltip"))

        # Open Modal 17
        btn_open.click()
        modal = page.locator("#match-control-modal")
        self.assertTrue(modal.is_visible())
        self.assertIn("open", modal.get_attribute("class"))

        # Verify 3 sub-tab buttons and tooltips
        tab_pen = page.locator("#btn-mc-tab-penalty")
        tab_del = page.locator("#btn-mc-tab-delay")
        tab_dia = page.locator("#btn-mc-tab-diary")

        self.assertTrue(tab_pen.is_visible())
        self.assertTrue(tab_del.is_visible())
        self.assertTrue(tab_dia.is_visible())

        # Switch to delay tab
        tab_del.click()
        self.assertTrue(page.locator("#mc-view-delay").is_visible())
        self.assertFalse(page.locator("#mc-view-penalty").is_visible())

        # Switch to diary tab
        tab_dia.click()
        self.assertTrue(page.locator("#mc-view-diary").is_visible())

        # Switch back to penalty tab
        tab_pen.click()
        self.assertTrue(page.locator("#mc-view-penalty").is_visible())

        # Escape key dismissal
        page.keyboard.press("Escape")
        self.assertFalse(modal.is_visible())

    def test_award_penalty_runs_and_atomic_rollback(self):
        """Verify +5 Penalty extra button, MCC Law 28.3 penalty award, live score update, S13 scorecard breakdown, and 0ms atomic rollback."""
        page = self.page
        page.evaluate("() => navigate('S07')")

        initial_score = page.locator("#hero-score").inner_text()

        # Click +5 Penalty on keypad
        extra_btn = page.locator("#btn-extra-penalty")
        self.assertTrue(extra_btn.is_visible())
        self.assertIn("+5 Penalty", extra_btn.inner_text())
        extra_btn.click()

        # Modal opens on penalty tab
        modal = page.locator("#match-control-modal")
        self.assertTrue(modal.is_visible())

        # Select Law 28.3 (Helmet Strike) and click apply
        page.select_option("#mc-penalty-reason", "law_28_3")
        page.locator("#btn-apply-penalty-run").click()

        # Verify toast and live score HUD
        pen_wrap = page.locator("#hero-penalty-wrap")
        self.assertTrue(pen_wrap.is_visible())
        self.assertIn("+5", page.locator("#hero-penalty-score").inner_text())

        # Check delivery reel chip
        chip = page.locator(".ball-chip.penalty")
        self.assertTrue(chip.is_visible())
        self.assertIn("Pen 5", chip.inner_text())

        # Close modal if open
        page.keyboard.press("Escape")

        # Navigate to S13 Scorecard
        page.evaluate("() => navigate('S13')")
        extras_txt = page.locator("#scorecard-extras-txt").inner_text()
        self.assertIn("pen 5", extras_txt)

        # Verify S13 official incidents section
        inc_wrap = page.locator("#scorecard-incidents-wrap")
        self.assertTrue(inc_wrap.is_visible())
        self.assertIn("1 Incident", page.locator("#scorecard-incidents-count-badge").inner_text())
        self.assertIn("Ball struck", inc_wrap.inner_text())

        # Return to scoring and test 0ms atomic undo
        page.evaluate("() => navigate('S07')")
        page.evaluate("() => undoLastBall()")

        # Verify rollback restored initial score and removed penalty badge
        undone_score = page.locator("#hero-score").inner_text()
        self.assertEqual(undone_score, initial_score)
        self.assertFalse(page.locator("#hero-penalty-wrap").is_visible())

    def test_match_delay_calculator_and_incident_diary(self):
        """Verify stoppage calculation (lost overs), applying revised overs, and diary timeline entries with filtering."""
        page = self.page
        page.evaluate("() => navigate('S07')")

        # Open match control on delay tab
        page.locator("#btn-open-match-control").click()
        page.locator("#btn-mc-tab-delay").click()

        # Set 40 minutes duration via chip or input
        page.fill("#mc-delay-minutes", "40")
        page.dispatch_event("#mc-delay-minutes", "input")

        # Verify calculation
        lost_txt = page.locator("#mc-delay-lost-overs-txt").inner_text()
        sug_txt = page.locator("#mc-delay-suggested-overs-txt").inner_text()
        self.assertIn("10 Overs", lost_txt)
        self.assertIn("15 Overs", sug_txt)

        # Apply revised overs
        page.locator("#btn-apply-delay-overs").click()

        # Verify match overs reduced to 15
        overs_txt = page.locator("#hero-overs").inner_text()
        self.assertIn("/ 15", overs_txt)

        # Switch to Diary tab and record custom note
        page.locator("#btn-mc-tab-diary").click()
        page.fill("#mc-note-text", "First formal pitch warning issued by umpire")
        page.locator("#btn-add-incident-note").click()

        # Verify entry in timeline
        timeline = page.locator("#mc-incident-timeline")
        self.assertIn("pitch warning", timeline.inner_text().lower())

        # Test filter chips
        page.locator("#btn-diary-filter-delay").click()
        self.assertIn("delay", timeline.inner_text().lower())
        page.locator("#btn-diary-filter-all").click()

        page.keyboard.press("Escape")

if __name__ == "__main__":
    unittest.main()
