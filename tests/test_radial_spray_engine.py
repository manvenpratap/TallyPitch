# tests/test_radial_spray_engine.py
# End-to-end and Validation Tests for Track 13: Ground Wagon Wheel Radial Sector Spray & Lofted Arc Chart
# Covers 8-Sector Ground Partitioning, Parabolic Lofted Flight Arcs vs Ground Roll Traces,
# 4 Radial KPI Telemetry Cards, 8-Sector Spray Distribution Table, Trajectory Filters (Ground vs Air),
# and 0ms Atomic Rollback.

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestRadialSprayEngine(unittest.TestCase):
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

    def test_radial_kpis_and_sector_matrix_table(self):
        """Verify S14 Wagon Wheel renders 4 Radial KPI cards and the 8-Sector Spray Distribution Table."""
        page = self.page
        page.click("#tab-S07")

        # Score balls: 4 (ground/drive), 6 (lofted six), 1 (single), 0 (dot)
        page.click("button.keypad-btn:has-text('4 FOUR!')")
        page.click("button.keypad-btn:has-text('6 SIX!')")
        page.click("button.keypad-btn:has-text('1 Single')")
        page.click("button.keypad-btn:has-text('0 Dot')")

        # Navigate to Digital Scorecard (S13) & Wagon Wheel Tab
        page.click("#tab-S13")
        page.click("#btn-chart-wagon")
        self.assertTrue(page.locator("#chart-view-wagon").is_visible())

        # Verify 4 Radial KPI Cards
        kpi_prod = page.locator("#wagon-kpi-productive").inner_text()
        kpi_loft = page.locator("#wagon-kpi-lofted").inner_text()
        kpi_grd = page.locator("#wagon-kpi-ground").inner_text()
        kpi_bdy = page.locator("#wagon-kpi-boundary").inner_text()

        self.assertTrue(len(kpi_prod) > 0)
        self.assertTrue(len(kpi_loft) > 0)
        self.assertTrue(len(kpi_grd) > 0)
        self.assertTrue(len(kpi_bdy) > 0)

        # Verify 8-Sector Radial Matrix Table
        matrix_table = page.locator("#wagon-radial-matrix-wrap table")
        self.assertTrue(matrix_table.is_visible())
        rows = matrix_table.locator("tbody tr")
        self.assertEqual(rows.count(), 8)

        # Check that sector names exist in table
        table_text = matrix_table.inner_text()
        self.assertIn("Mid-Wicket", table_text)
        self.assertIn("Cover", table_text)
        self.assertIn("Long-On", table_text)
        self.assertIn("Fine Leg", table_text)

    def test_lofted_arc_vs_ground_trajectories_and_filters(self):
        """Verify 360 SVG turf displays both lofted flight paths and ground lines, with ground/air filters."""
        page = self.page
        page.click("#tab-S07")

        # 1. Score a ground 4
        page.click("button.keypad-btn:has-text('4 FOUR!')")

        # 2. Score an aerial 6
        page.click("button.keypad-btn:has-text('6 SIX!')")

        # 3. Score a ground single
        page.click("button.keypad-btn:has-text('1 Single')")

        # Navigate to S14 Wagon Wheel
        page.click("#tab-S13")
        page.click("#btn-chart-wagon")

        # Check total shot items on SVG (both lines and paths have class wagon-shot-line)
        shot_items = page.locator("#scorecard-wagon-svg-container .wagon-shot-line")
        self.assertEqual(shot_items.count(), 3)

        # Check that parabolic curved flight arc is drawn for the six
        arced_paths = page.locator("#scorecard-wagon-svg-container path.wagon-shot-line")
        self.assertGreaterEqual(arced_paths.count(), 1)

        # Test Filter: Lofted / Air only
        air_btn = page.locator("#btn-wf-air")
        air_btn.click()
        self.assertIn("active", air_btn.get_attribute("class"))
        air_items = page.locator("#scorecard-wagon-svg-container .wagon-shot-line")
        self.assertEqual(air_items.count(), 1) # Only the 6

        # Test Filter: Ground Only
        ground_btn = page.locator("#btn-wf-ground")
        ground_btn.click()
        self.assertIn("active", ground_btn.get_attribute("class"))
        ground_items = page.locator("#scorecard-wagon-svg-container .wagon-shot-line")
        self.assertEqual(ground_items.count(), 2) # The 4 and the 1

        # Reset Filter: All
        all_btn = page.locator("#btn-wf-all")
        all_btn.click()
        self.assertIn("active", all_btn.get_attribute("class"))
        all_items = page.locator("#scorecard-wagon-svg-container .wagon-shot-line")
        self.assertEqual(all_items.count(), 3)

    def test_radial_batter_filter_and_undo_rollback(self):
        """Verify batter dropdown selector and 0ms atomic undo rollback on radial engine."""
        page = self.page
        page.click("#tab-S07")

        # Score balls
        page.click("button.keypad-btn:has-text('4 FOUR!')")
        page.click("button.keypad-btn:has-text('6 SIX!')")

        # Open Wagon Wheel
        page.click("#tab-S13")
        page.click("#btn-chart-wagon")

        # Check batter select has options
        btr_sel = page.locator("#wagon-batter-select")
        self.assertTrue(btr_sel.is_visible())
        opts = btr_sel.locator("option")
        self.assertGreaterEqual(opts.count(), 1)

        # Rollback delivery via Undo
        page.click("#tab-S07")
        page.click("#undo-btn")

        del_count = page.evaluate("() => getCurrentInnings().deliveries.length")
        self.assertEqual(del_count, 1)

        # Return to Wagon Wheel and verify shot count reduced to 1
        page.click("#tab-S13")
        page.click("#btn-chart-wagon")
        post_undo_items = page.locator("#scorecard-wagon-svg-container .wagon-shot-line")
        self.assertEqual(post_undo_items.count(), 1)

if __name__ == "__main__":
    unittest.main()
