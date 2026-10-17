# tests/test_ground_and_insights.py
# End-to-end tests for Ground & Pitch Intelligence (Track 1) and CricInsights PRO Analytics (Track 2)

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestGroundAndInsights(unittest.TestCase):
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

    def test_venue_intelligence_report_rendering_and_selection(self):
        """Verify S14 Venue & Pitch Intelligence renders win ratio, benchmarks, pace/spin, and dismissal bars"""
        page = self.page
        page.click("#tab-S13")

        # 1. Switch to Venue Telemetry tab
        page.click("#btn-chart-venue")
        self.assertTrue(page.is_visible("#chart-view-venue"))

        # 2. Check default venue (Oval Maidan) metrics
        self.assertIn("Oval Maidan", page.text_content("#venue-select-s14 option:checked"))
        self.assertIn("142", page.text_content("#venue-avg-1st"))
        self.assertIn("130", page.text_content("#venue-avg-2nd"))
        self.assertIn("70%", page.text_content("#venue-pace-stat"))
        self.assertIn("30%", page.text_content("#venue-spin-stat"))

        # 3. Check dismissal breakdown bars have data-tooltips
        caught_bar = page.query_selector("#dis-bar-caught")
        self.assertIsNotNone(caught_bar)
        self.assertIn("CAUGHT", caught_bar.get_attribute("data-tooltip"))

        # 4. Switch to Wankhede Stadium
        page.select_option("#venue-select-s14", "wankhede")
        self.assertIn("172", page.text_content("#venue-avg-1st"))
        self.assertIn("Red Soil", page.text_content("#venue-pitch-pill"))
        self.assertIn("58%", page.text_content("#venue-win-ratio-txt"))

    def test_match_setup_venue_telemetry_preview(self):
        """Verify S03 Match Setup updates instant venue telemetry preview badge on selection"""
        page = self.page
        page.click("#tab-S03")

        self.assertTrue(page.is_visible("#setup-venue-telemetry"))
        self.assertIn("Pitch:", page.text_content("#setup-tele-pitch"))
        self.assertIn("Avg 1st Inns:", page.text_content("#setup-tele-avg"))

        # Switch to Chinnaswamy
        page.select_option("#ground-name", "chinnaswamy")
        self.assertIn("188", page.text_content("#setup-tele-avg"))
        self.assertIn("Batting Paradise", page.text_content("#setup-tele-pitch"))

    def test_live_win_predictor_hud_updates(self):
        """Verify S07 Live Scoring Console displays un-paywalled Win Predictor and updates dynamically"""
        page = self.page
        page.click("#tab-S07")

        # 1. Win Predictor container visible
        self.assertTrue(page.is_visible("#win-predictor-wrap"))
        initial_text = page.text_content("#win-pred-team-a")
        self.assertIn("%", initial_text)

        # 2. Score runs and verify predictor updates
        page.click("button:has-text('6 SIX!')")
        page.click("button:has-text('4 FOUR!')")
        updated_text = page.text_content("#win-pred-team-a")
        self.assertIn("%", updated_text)

        # 3. Bar widths exist
        width_a = page.get_attribute("#win-pred-bar-a", "style")
        self.assertIn("width", width_a)

    def test_wagon_wheel_vulnerability_heatmap_toggle(self):
        """Verify S14 Wagon Wheel toggles CricInsights Field Vulnerability Heatmap overlay"""
        page = self.page
        page.click("#tab-S13")
        page.click("#btn-chart-wagon")

        # Initial state: vulnerability banner hidden
        self.assertFalse(page.is_visible("#wagon-vulnerability-banner"))

        # Toggle Vulnerability Heatmap
        page.click("#btn-wf-vulnerability")
        self.assertTrue(page.is_visible("#wagon-vulnerability-banner"))
        self.assertIn("Vulnerability Analysis", page.text_content("#wagon-vulnerability-banner"))

        # Verify SVG contains hazard text
        svg_content = page.inner_html("#scorecard-wagon-svg-container")
        self.assertIn("Hazard", svg_content)
        self.assertIn("Prime Arc", svg_content)

    def test_cricinsights_player_scouting_query_engine(self):
        """Verify Screen S06 Player Scouting Engine filters players by role, strike rate, and name"""
        page = self.page
        page.click("#tab-teams-profiles")

        # 1. Scouting card rendered
        self.assertTrue(page.is_visible("#scout-results-tbody"))
        initial_rows = page.query_selector_all("#scout-results-tbody tr")
        self.assertGreaterEqual(len(initial_rows), 10)

        # 2. Filter by Bowlers only
        page.select_option("#scout-role-select", "Bowler")
        bowler_rows = page.query_selector_all("#scout-results-tbody tr")
        for row in bowler_rows:
            self.assertIn("Bowler", row.inner_text())

        # 3. Filter by search keyword "Bumrah"
        page.fill("#scout-search-name", "Bumrah")
        filtered_rows = page.query_selector_all("#scout-results-tbody tr")
        self.assertEqual(len(filtered_rows), 1)
        self.assertIn("Bumrah", filtered_rows[0].inner_text())

        # 4. Click View Record button and verify player profile switches
        page.click("#scout-results-tbody tr:first-child button:has-text('View Record')")
        profile_name = page.text_content("#profile-name")
        self.assertIn("Bumrah", profile_name)

        # 5. Reset filters
        page.click("button:has-text('Reset')")
        reset_rows = page.query_selector_all("#scout-results-tbody tr")
        self.assertEqual(len(reset_rows), len(initial_rows))

if __name__ == "__main__":
    unittest.main()
