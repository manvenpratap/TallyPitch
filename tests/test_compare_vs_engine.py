# tests/test_compare_vs_engine.py
# End-to-end and Validation Tests for Track 8: Player & Team Head-to-Head Compare VS Engine (Un-Paywalled)
# Covers Player VS Player, Team VS Team, Marquee Presets, 10 Metrics Split Bars, Dominance Index, and Cross-Screen Triggers.

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestCompareVsEngine(unittest.TestCase):
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

    def test_compare_vs_rendering_and_presets(self):
        """Verify Compare VS container, default player comparison, 10 metrics, and marquee presets."""
        self.page.evaluate("() => navigate('teams-profiles')")
        self.page.wait_for_selector("#player-team-compare-wrap", state="visible")

        # Verify header, mode switcher buttons, and VS badge
        self.assertTrue(self.page.locator("#btn-compare-mode-player").is_visible())
        self.assertTrue(self.page.locator("#btn-compare-mode-team").is_visible())
        self.assertTrue(self.page.locator("#compare-vs-badge").is_visible())

        # Check default selections (A1: Rohit Sharma vs B1: Virat Kohli)
        p1_val = self.page.locator("#compare-p1-select").input_value()
        p2_val = self.page.locator("#compare-p2-select").input_value()
        self.assertEqual(p1_val, "A1")
        self.assertEqual(p2_val, "B1")

        # Verify spotlight cards
        card_p1_text = self.page.locator("#compare-card-p1").inner_text()
        card_p2_text = self.page.locator("#compare-card-p2").inner_text()
        self.assertIn("Rohit Sharma", card_p1_text)
        self.assertIn("Virat Kohli", card_p2_text)
        self.assertIn("MVP Pts", card_p1_text)
        self.assertIn("Badges", card_p1_text)

        # Verify 10 comparative metrics rendered
        metrics = self.page.locator("#compare-player-metrics-wrap .compare-metric-row")
        self.assertEqual(metrics.count(), 10)

        # Check dominance pill
        dom_pill = self.page.locator("#compare-dominance-pill").inner_text()
        self.assertTrue("LEADS" in dom_pill or "TIED" in dom_pill)

        # Test Marquee Preset: Bumrah vs Siraj
        self.page.click("button[data-tooltip*='Jasprit Bumrah vs Mohammed Siraj']")
        self.assertEqual(self.page.locator("#compare-p1-select").input_value(), "A8")
        self.assertEqual(self.page.locator("#compare-p2-select").input_value(), "B8")
        self.assertIn("Jasprit Bumrah", self.page.locator("#compare-card-p1").inner_text())
        self.assertIn("Mohammed Siraj", self.page.locator("#compare-card-p2").inner_text())

    def test_compare_mode_switch_and_team_benchmark(self):
        """Verify switching to Team vs Team mode, team selectors, and team benchmark metrics."""
        self.page.evaluate("() => navigate('teams-profiles')")
        self.page.wait_for_selector("#btn-compare-mode-team", state="visible")

        # Switch to Team vs Team
        self.page.click("#btn-compare-mode-team")

        player_view = self.page.locator("#compare-player-view")
        team_view = self.page.locator("#compare-team-view")
        self.assertFalse(player_view.is_visible())
        self.assertTrue(team_view.is_visible())

        # Verify team selectors and defaults
        t1_val = self.page.locator("#compare-t1-select").input_value()
        t2_val = self.page.locator("#compare-t2-select").input_value()
        self.assertIn("Mumbai", t1_val)
        self.assertIn("Bangalore", t2_val)

        # Verify team spotlight cards
        card_t1_text = self.page.locator("#compare-card-t1").inner_text()
        card_t2_text = self.page.locator("#compare-card-t2").inner_text()
        self.assertIn("Mumbai Strikers", card_t1_text)
        self.assertIn("Bangalore Blasters", card_t2_text)

        # Verify team metrics (6 metrics)
        team_metrics = self.page.locator("#compare-team-metrics-wrap .compare-metric-row")
        self.assertEqual(team_metrics.count(), 6)

        # Verify dominance pill
        team_dom_pill = self.page.locator("#compare-team-dominance-pill").inner_text()
        self.assertTrue("LEADS" in team_dom_pill or "TIED" in team_dom_pill)

    def test_cross_screen_triggers(self):
        """Verify opening Compare VS from career profile and from scouting table."""
        self.page.evaluate("() => navigate('teams-profiles')")

        # 1. Test #btn-compare-from-profile
        compare_btn = self.page.locator("#btn-compare-from-profile")
        self.assertTrue(compare_btn.is_visible())
        self.assertEqual(compare_btn.get_attribute("data-tooltip"), "Compare this player head-to-head in VS Engine")

        # Select a specific player in career profile (e.g. Hardik Pandya A4)
        self.page.select_option("#profile-player-select", "A4")
        self.page.click("#btn-compare-from-profile")

        # Verify Player 1 is updated to Hardik Pandya
        self.assertEqual(self.page.locator("#compare-p1-select").input_value(), "A4")
        self.assertIn("Hardik Pandya", self.page.locator("#compare-card-p1").inner_text())

        # 2. Test ⚡ VS button in scouting table
        self.page.wait_for_selector("#scout-results-tbody tr", state="visible")
        # Click the ⚡ VS button on the first scouted row (Rohit Sharma A1)
        first_vs_btn = self.page.locator("#scout-results-tbody tr").nth(0).locator("button:has-text('⚡ VS')")
        self.assertTrue(first_vs_btn.is_visible())
        first_vs_btn.click()

        # Verify Player 1 updated to Rohit Sharma
        self.assertEqual(self.page.locator("#compare-p1-select").input_value(), "A1")
        self.assertIn("Rohit Sharma", self.page.locator("#compare-card-p1").inner_text())

if __name__ == "__main__":
    unittest.main()
