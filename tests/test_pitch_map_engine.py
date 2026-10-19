# tests/test_pitch_map_engine.py
# End-to-end and Validation Tests for Track 12: Delivery Pitch Line & Length Map Engine (tbl_PitchLineLength)
# Covers Pitch Inference, Modal 3 Length & Line Chips, S14 9th Chart Tab (#btn-chart-pitch),
# 4 KPI Telemetry Cards, 2D Turf Heatmap SVG, Length x Line Breakdown Matrix Table, and 0ms Atomic Rollback.

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestPitchMapEngine(unittest.TestCase):
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

    def test_pitch_inference_and_modal_chips(self):
        """Verify delivery automatically attaches pitchLength/pitchLine and Modal 3 displays interactive chips."""
        page = self.page
        page.click("#tab-S07")

        # Score a 4 (boundary)
        page.click("button.keypad-btn:has-text('4 FOUR!')")

        # Verify delivery has inferred pitch attributes
        del_info = page.evaluate("() => { const d = getCurrentInnings().deliveries[0]; return { len: d.pitchLength, ln: d.pitchLine }; }")
        self.assertIsNotNone(del_info["len"])
        self.assertIsNotNone(del_info["ln"])
        self.assertIn(del_info["len"], ['Yorker', 'Full', 'Good Length', 'Back of Length', 'Short', 'Full Toss'])

        # Open Wagon Wheel Modal (Modal 3)
        page.evaluate("openWagonWheelModal()")
        modal = page.locator("#wagon-wheel-modal")
        self.assertTrue(modal.is_visible())

        # Verify Pitch Pill and Chips in Modal
        pitch_pill = page.locator("#wagon-selected-pitch-pill")
        self.assertTrue(pitch_pill.is_visible())
        self.assertIn("•", pitch_pill.inner_text())

        # Click 'Yorker' length chip
        page.click("#wagon-pitch-length-chips button:has-text('Yorker')")
        # Click 'Middle / Leg' line chip
        page.click("#wagon-pitch-line-chips button:has-text('Middle / Leg')")

        self.assertIn("Yorker", pitch_pill.inner_text())
        self.assertIn("Middle / Leg", pitch_pill.inner_text())

        # Save modal placement
        page.evaluate("saveWagonWheelPlacement()")

        # Verify updated delivery
        updated_del = page.evaluate("() => { const d = getCurrentInnings().deliveries[0]; return { len: d.pitchLength, ln: d.pitchLine }; }")
        self.assertEqual(updated_del["len"], "Yorker")
        self.assertEqual(updated_del["ln"], "Middle / Leg")

    def test_s14_pitch_map_tab_kpis_and_svg_heatmap(self):
        """Verify S14 Pitch Map tab renders 4 KPI cards and 2D Turf Heatmap SVG."""
        page = self.page
        page.click("#tab-S07")

        # Score 3 balls: 4, 6, dot
        page.click("button.keypad-btn:has-text('4 FOUR!')")
        page.click("button.keypad-btn:has-text('6 SIX!')")
        page.click("button.keypad-btn:has-text('0 Dot')")

        # Navigate to S13 / S14
        page.click("#tab-S13")
        pitch_tab_btn = page.locator("#btn-chart-pitch")
        self.assertTrue(pitch_tab_btn.is_visible())
        pitch_tab_btn.click()

        # Verify Pitch Map tab active
        self.assertTrue(page.locator("#chart-view-pitch").is_visible())
        self.assertIn("active", page.get_attribute("#btn-chart-pitch", "class"))

        # Verify 4 KPI cards render telemetry
        kpi_freq = page.locator("#pitch-kpi-frequent").inner_text()
        kpi_eco = page.locator("#pitch-kpi-economical").inner_text()
        kpi_exp = page.locator("#pitch-kpi-expensive").inner_text()
        kpi_wkt = page.locator("#pitch-kpi-wickets").inner_text()

        self.assertTrue(len(kpi_freq) > 0)
        self.assertTrue(len(kpi_eco) > 0)
        self.assertTrue(len(kpi_exp) > 0)
        self.assertTrue(len(kpi_wkt) > 0)

        # Verify Heatmap SVG renders with pitch strip and ball dots
        heatmap_svg = page.locator("#pitch-heatmap-svg-wrap svg")
        self.assertTrue(heatmap_svg.is_visible())
        dots = heatmap_svg.locator("#pitch-dots-group circle")
        self.assertEqual(dots.count(), 3)

    def test_pitch_matrix_table_and_undo_rollback(self):
        """Verify Length x Line matrix table, delivery type filter buttons, and 0ms atomic rollback."""
        page = self.page
        page.click("#tab-S07")

        # Score balls
        page.click("button.keypad-btn:has-text('4 FOUR!')")
        page.click("button.keypad-btn:has-text('0 Dot')")

        # Navigate to S14 Pitch Map
        page.click("#tab-S13")
        page.click("#btn-chart-pitch")

        # Verify Matrix Table exists and has rows for all 6 lengths
        table = page.locator("#pitch-matrix-table-wrap table")
        self.assertTrue(table.is_visible())
        rows = table.locator("tbody tr")
        self.assertEqual(rows.count(), 6)

        # Verify delivery filter toggles
        dots_filter = page.locator("#btn-pitch-type-dots")
        dots_filter.click()
        self.assertIn("active", dots_filter.get_attribute("class"))
        dots_count = page.locator("#pitch-dots-group circle").count()
        self.assertEqual(dots_count, 1)

        all_filter = page.locator("#btn-pitch-type-all")
        all_filter.click()
        self.assertIn("active", all_filter.get_attribute("class"))
        all_count = page.locator("#pitch-dots-group circle").count()
        self.assertEqual(all_count, 2)

        # 0ms Atomic Undo Rollback
        page.click("#tab-S07")
        page.click("#undo-btn")
        del_count = page.evaluate("() => getCurrentInnings().deliveries.length")
        self.assertEqual(del_count, 1)

        # Re-check Pitch Map after undo
        page.click("#tab-S13")
        page.click("#btn-chart-pitch")
        post_undo_dots = page.locator("#pitch-dots-group circle").count()
        self.assertEqual(post_undo_dots, 1)

if __name__ == "__main__":
    unittest.main()
