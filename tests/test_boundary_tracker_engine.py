# tests/test_boundary_tracker_engine.py
# End-to-end and Validation Tests for Track 19: Tournament Boundary Tracker & Boundarometer
# Reverse-engineered from CricHeroes BoundaryTrackerFragment and tournaments_boundary_tracker.
# Covers S18 Boundarometer KPIs, Franchise Boundary Share, Batting Hand Splits (RH vs LH), Boundary Kings Podium, and Zero Console Errors.

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestBoundaryTrackerEngine(unittest.TestCase):
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

    def test_boundarometer_kpis_rendering(self):
        """Verify S18 displays Tournament Boundary Tracker card with 4 Boundarometer telemetry KPIs."""
        page = self.page
        page.evaluate("() => navigate('tournaments')")

        card = page.locator("#tournament-boundary-tracker-card")
        self.assertTrue(card.is_visible())
        self.assertIsNotNone(card.get_attribute("data-tooltip"))

        # Verify 4 KPIs
        sixes_kpi = page.locator("#bnd-kpi-total-sixes")
        fours_kpi = page.locator("#bnd-kpi-total-fours")
        yield_kpi = page.locator("#bnd-kpi-runs-pct")
        freq_kpi = page.locator("#bnd-kpi-balls-per-bnd")

        self.assertTrue(sixes_kpi.is_visible())
        self.assertTrue(fours_kpi.is_visible())
        self.assertTrue(yield_kpi.is_visible())
        self.assertTrue(freq_kpi.is_visible())

        # Check values
        self.assertIn("Sixes", sixes_kpi.inner_text())
        self.assertIn("Fours", fours_kpi.inner_text())
        self.assertIn("%", yield_kpi.inner_text())
        self.assertIn("b", freq_kpi.inner_text())

    def test_boundary_subtabs_and_breakdowns(self):
        """Verify Franchise Share, Batting Hand Splits (RH vs LH), and Boundary Kings Podium tabs."""
        page = self.page
        page.evaluate("() => navigate('tournaments')")

        # 1. Franchise Boundary Share (Default active)
        panel_teams = page.locator("#bnd-panel-teams")
        self.assertTrue(panel_teams.is_visible())
        team_rows = page.locator("#bnd-teams-container .bnd-team-row")
        self.assertGreaterEqual(team_rows.count(), 2)

        # 2. Switch to Batting Hand Splits (RH vs LH)
        page.click("#btn-bnd-tab-hands")
        panel_hands = page.locator("#bnd-panel-hands")
        self.assertTrue(panel_hands.is_visible())
        self.assertFalse(panel_teams.is_visible())
        self.assertIn("Right-Hand vs Left-Hand", panel_hands.inner_text())
        self.assertIn("RH", panel_hands.inner_text())
        self.assertIn("LH", panel_hands.inner_text())

        # 3. Switch to Boundary Kings Podium
        page.click("#btn-bnd-tab-podium")
        panel_podium = page.locator("#bnd-panel-podium")
        self.assertTrue(panel_podium.is_visible())
        self.assertFalse(panel_hands.is_visible())

        six_leaders = page.locator("#bnd-podium-sixes .podium-six-row")
        four_leaders = page.locator("#bnd-podium-fours .podium-four-row")
        self.assertGreaterEqual(six_leaders.count(), 3)
        self.assertGreaterEqual(four_leaders.count(), 3)

    def test_recalculate_boundaries_action(self):
        """Verify 'Recalculate Boundaries' action re-evaluates statistics smoothly without console errors."""
        page = self.page
        page.evaluate("() => navigate('tournaments')")

        btn_refresh = page.locator("#btn-refresh-boundary-tracker")
        self.assertTrue(btn_refresh.is_visible())
        btn_refresh.click()

        # Re-check KPI card still valid
        sixes_kpi = page.locator("#bnd-kpi-total-sixes")
        self.assertTrue(sixes_kpi.is_visible())
        self.assertIn("Sixes", sixes_kpi.inner_text())

if __name__ == "__main__":
    unittest.main()
