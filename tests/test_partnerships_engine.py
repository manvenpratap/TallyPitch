# tests/test_partnerships_engine.py
# End-to-end and Validation Tests for Track 6: Live Batting Partnerships Engine (tbl_Partnership on S07 & S13)
# Covers live partnership HUD (runs, balls, run rate, 4s/6s), proportional split progress bar,
# wicket transition, unbroken innings partnership tracking, S13 scorecard breakdown, and 0ms atomic rollback.

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestPartnershipsEngine(unittest.TestCase):
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

    def test_initial_partnership_hud_rendering(self):
        """Verify initial S07 live partnership card layout, labels, and 0-score state"""
        self.page.wait_for_selector("#live-partnership-card", state="visible")

        # Label should display 1st Wicket Partnership
        w_label = self.page.locator("#partnership-wicket-label").inner_text()
        self.assertIn("1ST WICKET", w_label.upper())

        # Runs & balls should be zero
        runs_txt = self.page.locator("#partnership-runs").inner_text()
        balls_txt = self.page.locator("#partnership-balls").inner_text()
        rr_txt = self.page.locator("#partnership-rr").inner_text()
        self.assertEqual(runs_txt, "0")
        self.assertEqual(balls_txt, "0")
        self.assertEqual(rr_txt, "0.00")

        # Batter chips should be visible with opener names
        name_a = self.page.locator("#partnership-batter-a-name").inner_text()
        name_b = self.page.locator("#partnership-batter-b-name").inner_text()
        self.assertEqual(name_a, "Rohit Sharma")
        self.assertEqual(name_b, "Ishan Kishan")

        # Split bars should be initialized
        bar_a = self.page.locator("#partnership-bar-a")
        bar_b = self.page.locator("#partnership-bar-b")
        self.assertTrue(bar_a.is_visible())
        self.assertTrue(bar_b.is_visible())

        # Tooltip should exist
        card = self.page.locator("#live-partnership-card")
        self.assertTrue(card.get_attribute("data-tooltip") is not None)

    def test_partnership_updates_on_scoring_and_extras(self):
        """Verify live partnership updates runs, balls, boundaries, and batter splits as deliveries are scored"""
        self.page.wait_for_selector("#live-partnership-card", state="visible")

        # Score a 4 (boundary) by Rohit
        self.page.evaluate("recordBall(4)")
        self.assertEqual(self.page.locator("#partnership-runs").inner_text(), "4")
        self.assertEqual(self.page.locator("#partnership-balls").inner_text(), "1")
        self.assertEqual(self.page.locator("#partnership-4s").inner_text(), "1")
        self.assertEqual(self.page.locator("#partnership-batter-a-runs").inner_text(), "4")
        self.assertEqual(self.page.locator("#partnership-batter-a-balls").inner_text(), "1")

        # Score a single (1 run) - strike rotates to Ishan Kishan
        self.page.evaluate("recordBall(1)")
        self.assertEqual(self.page.locator("#partnership-runs").inner_text(), "5")
        self.assertEqual(self.page.locator("#partnership-balls").inner_text(), "2")
        self.assertEqual(self.page.locator("#partnership-batter-a-runs").inner_text(), "5")
        self.assertEqual(self.page.locator("#partnership-batter-a-balls").inner_text(), "2")

        # Ishan Kishan on strike scores a 2
        self.page.evaluate("recordBall(2)")
        self.assertEqual(self.page.locator("#partnership-runs").inner_text(), "7")
        self.assertEqual(self.page.locator("#partnership-balls").inner_text(), "3")
        self.assertEqual(self.page.locator("#partnership-batter-b-runs").inner_text(), "2")
        self.assertEqual(self.page.locator("#partnership-batter-b-balls").inner_text(), "1")

        # Record a wide extra (+1 run, 0 legal balls)
        self.page.evaluate("recordExtra('wide')")
        self.assertEqual(self.page.locator("#partnership-runs").inner_text(), "8")
        self.assertEqual(self.page.locator("#partnership-balls").inner_text(), "3")

        # Verify run rate: 8 runs off 3 balls = 16.00
        self.assertEqual(self.page.locator("#partnership-rr").inner_text(), "16.00")

    def test_partnership_wicket_rollover_and_scorecard(self):
        """Verify partnership completes on wicket, next partnership begins, and S13 scorecard renders breakdown with undo support"""
        self.page.wait_for_selector("#live-partnership-card", state="visible")

        # Score 6 runs (Rohit hits a six)
        self.page.evaluate("recordBall(6)")
        self.assertEqual(self.page.locator("#partnership-runs").inner_text(), "6")

        # Score a wicket: open modal, dismiss Rohit (A1), incoming Suryakumar Yadav (A3)
        self.page.evaluate("""() => {
            openWicketModal();
            document.querySelector('input[name="dismissal_type"][value="Caught"]').checked = true;
            document.getElementById('out-batter-select').value = 'A1';
            document.getElementById('next-batter-select').value = 'A3';
            confirmWicketDismissal();
        }""")

        # After wicket, new partnership should be for 2nd Wicket
        w_label = self.page.locator("#partnership-wicket-label").inner_text()
        self.assertIn("2ND WICKET", w_label.upper())
        self.assertEqual(self.page.locator("#partnership-runs").inner_text(), "0")
        self.assertEqual(self.page.locator("#partnership-balls").inner_text(), "0")

        # Batter names should now be surviving Ishan Kishan and incoming Suryakumar Yadav
        name_a = self.page.locator("#partnership-batter-a-name").inner_text()
        name_b = self.page.locator("#partnership-batter-b-name").inner_text()
        self.assertEqual(name_a, "Ishan Kishan")
        self.assertEqual(name_b, "Suryakumar Yadav")

        # Navigate to Full Scorecard (S13) and verify completed 1st Wicket partnership
        self.page.evaluate("() => navigate('S13')")
        self.page.wait_for_selector("#scorecard-partnerships-wrap", state="visible")
        scorecard_html = self.page.locator("#scorecard-partnerships-wrap").inner_html()
        self.assertIn("1st Wicket", scorecard_html)
        self.assertIn("Rohit Sharma", scorecard_html)
        self.assertIn("6 runs", scorecard_html)
        self.assertIn("2nd Wicket (Unbroken)", scorecard_html)

        # Return to S07 and verify 0ms Atomic Undo
        self.page.evaluate("() => navigate('S07')")
        self.page.evaluate("undoLastBall()")

        # After undoing wicket, 1st Wicket partnership is restored with 6 runs
        w_label_restored = self.page.locator("#partnership-wicket-label").inner_text()
        self.assertIn("1ST WICKET", w_label_restored.upper())
        self.assertEqual(self.page.locator("#partnership-runs").inner_text(), "6")
        self.assertEqual(self.page.locator("#partnership-batter-a-name").inner_text(), "Rohit Sharma")

if __name__ == "__main__":
    unittest.main()
