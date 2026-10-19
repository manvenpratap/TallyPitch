# tests/test_turning_point_engine.py
# End-to-end and Validation Tests for Track 11: Match Turning Point Overs & Momentum Engine (past_match_turning_point_overs)
# Covers S07 Live Turning Point Alert Pill, S14 8th Chart Tab, 4 KPI Telemetry Cards, Over-by-Over Momentum SVG Curve,
# Perspective Filtering (Batting, Bowling, Swings), and 0ms Atomic Rollback.

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestTurningPointEngine(unittest.TestCase):
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

    def test_live_turning_point_alert_in_s07(self):
        """Verify S07 Live Turning Point Alert pill appears on high impact overs and navigates to S14."""
        page = self.page
        page.click("#tab-S07")

        alert_pill = page.locator("#live-turning-point-alert")
        self.assertFalse(alert_pill.is_visible())

        # Score a boundary barrage (6 + 4 + 4 = 14 runs) to trigger boundary explosion
        page.click("button.keypad-btn:has-text('6 SIX!')")
        page.click("button.keypad-btn:has-text('4 FOUR!')")
        page.click("button.keypad-btn:has-text('4 FOUR!')")

        # Verify alert pill is now visible with game-changer message
        self.assertTrue(alert_pill.is_visible())
        alert_text = alert_pill.inner_text()
        self.assertIn("Game-Changer", alert_text)
        self.assertIn("14r", alert_text)

        # Click alert pill to trigger quick transition to S14 Turning Points tab
        alert_pill.click()
        self.assertTrue(page.locator("#chart-view-turning").is_visible())
        self.assertIn("active", page.get_attribute("#btn-chart-turning", "class"))

        # Return to S07 and verify 0ms rollback
        page.click("#tab-S07")
        page.click("#undo-btn")
        del_count = page.evaluate("() => getCurrentInnings().deliveries.length")
        self.assertEqual(del_count, 2)

    def test_s14_turning_points_tab_kpis_and_momentum_svg(self):
        """Verify S14 Turning Points tab renders 4 KPI cards and interactive Momentum Index SVG curve."""
        page = self.page
        page.click("#tab-S07")

        # Score a 4, a 6, and a dot
        page.click("button.keypad-btn:has-text('4 FOUR!')")
        page.click("button.keypad-btn:has-text('6 SIX!')")
        page.click("button.keypad-btn:has-text('0 Dot')")

        # Open S13 Digital Scorecard & S14 Charts
        page.click("#tab-S13")
        turning_tab_btn = page.locator("#btn-chart-turning")
        self.assertTrue(turning_tab_btn.is_visible())
        turning_tab_btn.click()

        # Verify #chart-view-turning is active
        self.assertTrue(page.locator("#chart-view-turning").is_visible())

        # Verify 4 KPI cards render valid telemetry
        kpi_biggest = page.locator("#tp-kpi-biggest").inner_text()
        kpi_deadliest = page.locator("#tp-kpi-deadliest").inner_text()
        kpi_tightest = page.locator("#tp-kpi-tightest").inner_text()
        kpi_swing = page.locator("#tp-kpi-swing").inner_text()

        self.assertTrue(len(kpi_biggest) > 0)
        self.assertTrue(len(kpi_deadliest) > 0)
        self.assertTrue(len(kpi_tightest) > 0)
        self.assertTrue(len(kpi_swing) > 0)

        # Verify Momentum SVG renders with bars and axis
        momentum_svg = page.locator("#tp-momentum-chart-container svg")
        self.assertTrue(momentum_svg.is_visible())
        rects = momentum_svg.locator("rect")
        self.assertGreaterEqual(rects.count(), 1)

    def test_turning_point_perspective_filters_and_overs_list(self):
        """Verify perspective filter buttons (All, Batting, Bowling, Swings) and breakdown cards list."""
        page = self.page
        page.click("#tab-S07")

        # Score varied overs
        page.click("button.keypad-btn:has-text('6 SIX!')")
        page.click("button.keypad-btn:has-text('4 FOUR!')")
        page.click("button.keypad-btn:has-text('4 FOUR!')")
        page.click("button.keypad-btn:has-text('1 Single')")

        # Open S14 Turning Points
        page.click("#tab-S13")
        page.click("#btn-chart-turning")

        # Verify breakdown list renders over cards
        overs_list = page.locator("#tp-overs-list")
        self.assertTrue(overs_list.is_visible())
        cards = overs_list.locator(".card")
        self.assertGreaterEqual(cards.count(), 1)

        # Click perspective filters and verify active toggle
        page.click("#btn-tp-batting")
        self.assertIn("active", page.get_attribute("#btn-tp-batting", "class"))

        page.click("#btn-tp-bowling")
        self.assertIn("active", page.get_attribute("#btn-tp-bowling", "class"))

        page.click("#btn-tp-swings")
        self.assertIn("active", page.get_attribute("#btn-tp-swings", "class"))

        page.click("#btn-tp-all")
        self.assertIn("active", page.get_attribute("#btn-tp-all", "class"))

        # Verify Innings filter selector
        innings_sel = page.locator("#tp-innings-select")
        self.assertTrue(innings_sel.is_visible())
        innings_sel.select_option("all")
        self.assertTrue(cards.first.is_visible())


if __name__ == "__main__":
    unittest.main()
