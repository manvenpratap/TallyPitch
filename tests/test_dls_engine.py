# tests/test_dls_engine.py
# End-to-end tests for REA Track: Duckworth-Lewis-Stern (DLS) Rain Rule & Target Revision Engine

import os
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestDlsEngine(unittest.TestCase):
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

    def test_dls_button_and_modal_elements(self):
        """Verify DLS button on S07, modal markup, and accessible tooltips exist"""
        btn = self.page.locator("#btn-dls-modal")
        self.assertTrue(btn.is_visible(timeout=5000), "#btn-dls-modal must be visible on S07")
        self.assertEqual(btn.get_attribute("data-tooltip"), "Duckworth-Lewis-Stern (DLS) rain rule & revised target calculator")

        # Open modal
        btn.click()
        self.page.wait_for_selector("#dls-modal.open")

        apply_btn = self.page.locator("#btn-apply-dls")
        conclude_btn = self.page.locator("#btn-conclude-dls")
        self.assertEqual(apply_btn.get_attribute("data-tooltip"), "Apply DLS target to 2nd innings and update live scoring HUD")
        self.assertEqual(conclude_btn.get_attribute("data-tooltip"), "Declare match completed using current DLS Par Score")

        # Dismiss modal via Escape
        self.page.keyboard.press("Escape")
        self.page.wait_for_function("() => !document.getElementById('dls-modal').classList.contains('open')")

    def test_dls_target_revision_and_hud_update(self):
        """Verify reducing innings 2 overs computes mathematically revised target and updates S07 HUD"""
        # Set Innings 1 score to 165
        self.page.evaluate("""() => {
            state.innings1.totalRuns = 165;
            state.innings1.wickets = 6;
            state.innings1.legalBalls = 120;
            state.match.currentInningsNumber = 2;
            state.innings2.targetRuns = 166;
            renderLiveConsole();
        }""")

        # Open DLS modal
        self.page.click("#btn-dls-modal")
        self.page.wait_for_selector("#dls-modal.open")

        # Input revised overs: 14
        input_el = self.page.locator("#dls-revised-overs-input")
        input_el.fill("14")

        # Check resource % and target
        resource_pct = self.page.locator("#dls-resource-pct-display").inner_text()
        self.assertIn("82.3%", resource_pct)

        target_val = self.page.locator("#dls-calc-target-val").inner_text()
        self.assertIn("136", target_val)

        # Apply revision
        self.page.click("#btn-apply-dls")
        self.page.wait_for_function("() => !document.getElementById('dls-modal').classList.contains('open')")

        # Verify S07 reflects DLS Target
        hero_target = self.page.locator("#hero-target").inner_text()
        self.assertIn("136 (DLS)", hero_target)

        chase_text = self.page.locator("#hero-chase-banner").inner_text()
        self.assertIn("DLS Revised", chase_text)

    def test_dls_live_par_score_and_matrix(self):
        """Verify DLS Par Score HUD dynamically displays par runs and ahead/behind badge in Innings 2"""
        # Simulate 8.0 overs bowled (48 balls), 2 wickets down, 68 runs scored
        self.page.evaluate("""() => {
            state.innings1.totalRuns = 165;
            state.match.totalOvers = 20;
            state.match.currentInningsNumber = 2;
            state.innings2.totalRuns = 68;
            state.innings2.wickets = 2;
            state.innings2.legalBalls = 48;
            renderLiveConsole();
        }""")

        par_wrap = self.page.locator("#hero-dls-par-wrap")
        self.assertTrue(par_wrap.is_visible(), "DLS Par Score HUD must be visible in Innings 2")

        par_score = self.page.locator("#hero-dls-par-score").inner_text()
        diff_badge = self.page.locator("#hero-dls-diff-badge").inner_text()

        # Par score at 8 ov, 2 wkts for 165 target is 60. Current runs 68 -> Ahead by 8 runs!
        self.assertEqual(par_score, "60")
        self.assertIn("+8", diff_badge)
        self.assertIn("Ahead", diff_badge)

        # Open DLS modal and check par score matrix table
        self.page.click("#btn-dls-modal")
        self.page.wait_for_selector("#dls-modal.open")

        matrix_cells = self.page.locator("#dls-matrix-row td")
        self.assertEqual(matrix_cells.count(), 11, "Matrix row must contain 1 header + 10 wicket columns (0..9)")

    def test_dls_conclude_match_verdict(self):
        """Verify calling off match after minimum 5 overs declares winner by DLS Method"""
        self.page.evaluate("""() => {
            state.innings1.totalRuns = 165;
            state.match.totalOvers = 20;
            state.match.currentInningsNumber = 2;
            state.innings2.totalRuns = 68;
            state.innings2.wickets = 2;
            state.innings2.legalBalls = 48; // 8.0 overs (> 5 overs minimum)
            renderLiveConsole();
            openDlsModal();
        }""")

        self.page.wait_for_selector("#dls-modal.open")
        self.page.click("#btn-conclude-dls")

        self.page.wait_for_selector("#match-result-modal.open")
        desc = self.page.locator("#winner-modal-desc").inner_text()
        self.assertIn("DLS Method", desc)
        self.assertIn("won by 8 runs", desc)


if __name__ == "__main__":
    unittest.main()
