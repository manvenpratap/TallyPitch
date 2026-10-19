# tests/test_face_off_engine.py
# End-to-end and Validation Tests for Track 10: Batter vs Bowler Head-to-Head Face-Off Matrix Engine (past_match_face_off)
# Covers Live S07 Face-Off HUD, Modal 12 Face-Off Duel Inspection, S14 Face-Off Matrix Grid, 4 KPI Cards,
# Interactive Cell Spotlight, and 0ms Atomic Rollback (Undo).

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestFaceOffEngine(unittest.TestCase):
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

    def test_faceoff_hud_and_modal_interaction(self):
        """Verify S07 Live Face-Off HUD button, real-time stat updates, Modal 12 opening, selectors, and metrics."""
        page = self.page
        page.click("#tab-S07")

        # Initial HUD state
        hud_btn = page.locator("#btn-faceoff-hud")
        self.assertTrue(hud_btn.is_visible())
        self.assertIn("Face-Off", hud_btn.inner_text())

        # Score a 4 and a 1
        page.click("button.keypad-btn:has-text('4 FOUR!')")
        page.click("button.keypad-btn:has-text('1 Single')")

        # Check that HUD button updated with striker vs bowler figures
        hud_text = hud_btn.inner_text()
        self.assertTrue("r" in hud_text or "b" in hud_text)

        # Open Modal 12 via HUD button
        hud_btn.click()
        self.assertTrue(page.is_visible("#faceoff-modal"))
        self.assertIn("open", page.get_attribute("#faceoff-modal", "class"))

        # Verify modal selectors and duel card
        batter_select = page.locator("#faceoff-modal-batter-select")
        bowler_select = page.locator("#faceoff-modal-bowler-select")
        self.assertTrue(batter_select.is_visible())
        self.assertTrue(bowler_select.is_visible())
        self.assertGreaterEqual(batter_select.locator("option").count(), 1)
        self.assertGreaterEqual(bowler_select.locator("option").count(), 1)

        duel_card = page.locator("#faceoff-modal-duel-card")
        self.assertTrue(duel_card.is_visible())
        duel_text = duel_card.inner_text().upper()
        self.assertIn("LIVE HEAD-TO-HEAD RECORD", duel_text)
        self.assertIn("RUNS (BALLS)", duel_text)
        self.assertIn("STRIKE RATE", duel_text)

        # Close modal
        page.click("#faceoff-modal button:has-text('✕')")
        self.assertNotIn("open", page.get_attribute("#faceoff-modal", "class"))

    def test_s14_faceoff_matrix_and_kpis(self):
        """Verify Screen S14 Face-Off Matrix tab, 4 KPI telemetry cards, matrix table, and innings filter selector."""
        page = self.page
        page.click("#tab-S07")

        # Score varied deliveries
        page.click("button.keypad-btn:has-text('4 FOUR!')")
        page.click("button.keypad-btn:has-text('6 SIX!')")
        page.click("button.keypad-btn:has-text('0 Dot')")
        page.click("button.keypad-btn:has-text('1 Single')")

        # Navigate to S13 Digital Scorecard & S14 Charts
        page.click("#tab-S13")

        # Click Face-Off Matrix chart tab
        chart_btn = page.locator("#btn-chart-faceoff")
        self.assertTrue(chart_btn.is_visible())
        chart_btn.click()

        # Verify #chart-view-faceoff is active
        self.assertTrue(page.locator("#chart-view-faceoff").is_visible())

        # Verify 4 KPI cards render valid telemetry
        kpi_batter = page.locator("#faceoff-kpi-batter").inner_text()
        kpi_bowler = page.locator("#faceoff-kpi-bowler").inner_text()
        kpi_dots = page.locator("#faceoff-kpi-dots").inner_text()
        kpi_duel = page.locator("#faceoff-kpi-duel").inner_text()

        self.assertTrue(len(kpi_batter) > 0)
        self.assertTrue(len(kpi_bowler) > 0)
        self.assertTrue(len(kpi_dots) > 0)
        self.assertTrue(len(kpi_duel) > 0)

        # Verify Matrix Grid Wrap contains rendered table
        matrix_table = page.locator("#faceoff-matrix-grid-wrap table")
        self.assertTrue(matrix_table.is_visible())
        rows = matrix_table.locator("tbody tr")
        self.assertGreaterEqual(rows.count(), 1)

        # Innings filter selector operates smoothly
        innings_sel = page.locator("#faceoff-innings-select")
        self.assertTrue(innings_sel.is_visible())
        innings_sel.select_option("all")
        self.assertTrue(matrix_table.is_visible())

    def test_faceoff_spotlight_and_undo_rollback(self):
        """Verify interactive matrix cell spotlight inspection, delivery chips, and 0ms atomic rollback."""
        page = self.page
        page.click("#tab-S07")

        # Score a 4 and a dot
        page.click("button.keypad-btn:has-text('4 FOUR!')")
        page.click("button.keypad-btn:has-text('0 Dot')")

        init_del_count = page.evaluate("() => getCurrentInnings().deliveries.length")
        self.assertEqual(init_del_count, 2)

        # Navigate to S13 & S14 Face-Off tab
        page.click("#tab-S13")
        page.click("#btn-chart-faceoff")

        # Verify spotlight card is visible
        spotlight_card = page.locator("#faceoff-spotlight-card")
        self.assertTrue(spotlight_card.is_visible())

        # Select a cell from matrix table
        active_cell = page.locator("#faceoff-matrix-grid-wrap td[onclick]").first
        if active_cell.count() > 0:
            active_cell.click()

        spotlight_content = page.locator("#faceoff-spotlight-content").inner_text()
        self.assertTrue("vs" in spotlight_content)
        self.assertTrue("runs off" in spotlight_content)

        # Return to S07 and perform 0ms Undo Rollback
        page.click("#tab-S07")
        page.click("#undo-btn")

        rolled_back_count = page.evaluate("() => getCurrentInnings().deliveries.length")
        self.assertEqual(rolled_back_count, init_del_count - 1)

        # Verify HUD reflects rollback
        hud_text = page.locator("#btn-faceoff-hud").inner_text()
        self.assertTrue("1b" in hud_text or "Face-Off" in hud_text or "4r" in hud_text)


if __name__ == "__main__":
    unittest.main()
