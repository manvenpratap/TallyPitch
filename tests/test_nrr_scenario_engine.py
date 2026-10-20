# tests/test_nrr_scenario_engine.py
# End-to-end and Validation Tests for Track 14: Dynamic Tournament NRR Qualification Scenario Calculator
# Reverse-engineered from CricHeroes TournamentScenarioActivityKt & CalculateNRRDialogFragment (Un-paywalled PRO).
# Covers Defending Scenario, Chasing Scenario, Direct Head-to-Head Clash, Presets, Match Setup Pre-fill, and Zero Console Errors.

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestNrrScenarioEngine(unittest.TestCase):
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

    def test_nrr_calculator_ui_rendering_and_presets(self):
        """Verify S18 NRR Calculator card renders with team selectors, presets, and telemetry cards."""
        page = self.page
        page.evaluate("() => navigate('tournaments')")
        page.wait_for_selector("#nrr-calculator-card", state="visible")

        # Verify selectors exist and have options
        team_sel = page.locator("#nrr-team-select")
        rival_sel = page.locator("#nrr-rival-select")
        self.assertTrue(team_sel.is_visible())
        self.assertTrue(rival_sel.is_visible())

        opts = team_sel.locator("option")
        self.assertGreaterEqual(opts.count(), 2)

        # Verify quick presets update inputs
        page.click("#btn-nrr-preset-120")
        runs_val = page.locator("#nrr-projected-runs-input").input_value()
        self.assertEqual(runs_val, "120")

        page.click("#btn-nrr-preset-200")
        runs_val2 = page.locator("#nrr-projected-runs-input").input_value()
        self.assertEqual(runs_val2, "200")

        # Verify Defending and Chasing cards render
        defend_card = page.locator("#nrr-defend-card")
        chase_card = page.locator("#nrr-chase-card")
        self.assertTrue(defend_card.is_visible())
        self.assertTrue(chase_card.is_visible())

        defend_text = page.locator("#nrr-defend-target-text").inner_text()
        chase_text = page.locator("#nrr-chase-target-text").inner_text()
        self.assertGreater(len(defend_text), 0)
        self.assertGreater(len(chase_text), 0)

    def test_nrr_scenario_mathematical_precision_and_clash(self):
        """Verify mathematical calculation of runs allowed, chase overs, and direct clash toggle."""
        page = self.page
        page.evaluate("() => navigate('tournaments')")
        page.wait_for_selector("#nrr-calculator-card", state="visible")

        # Select Pune Warriors seeking to overtake Mumbai Strikers
        page.select_option("#nrr-team-select", "Pune Warriors")
        page.select_option("#nrr-rival-select", "Mumbai Strikers")

        # Set 160 runs in 20 overs
        page.fill("#nrr-projected-runs-input", "160")
        page.fill("#nrr-match-overs-input", "20")

        # Check gap meter
        gap_text = page.locator("#nrr-gap-val").inner_text()
        self.assertTrue(len(gap_text) > 0)
        self.assertIn("-", gap_text) # Pune is behind Mumbai

        # Check Defend result
        defend_pill = page.locator("#nrr-defend-status-pill").inner_text()
        self.assertIn("QUALIFIES", defend_pill)
        defend_target = page.locator("#nrr-defend-target-text").inner_text()
        self.assertIn("Restrict", defend_target)

        # Check Chase result
        chase_pill = page.locator("#nrr-chase-status-pill").inner_text()
        self.assertIn("QUALIFIES", chase_pill)
        chase_target = page.locator("#nrr-chase-target-text").inner_text()
        self.assertIn("Chase 161", chase_target)

        # Toggle Direct Clash off and verify recalculation executes
        clash_cb = page.locator("#nrr-direct-clash-toggle")
        clash_cb.uncheck()
        defend_proj = page.locator("#nrr-defend-proj-nrr").inner_text()
        self.assertTrue(len(defend_proj) > 0)

    def test_nrr_apply_to_match_setup_and_zero_errors(self):
        """Verify 1-click pre-filling of S03 Match Setup from NRR simulator."""
        page = self.page
        page.evaluate("() => navigate('tournaments')")
        page.wait_for_selector("#nrr-calculator-card", state="visible")

        page.select_option("#nrr-team-select", "Pune Warriors")
        page.select_option("#nrr-rival-select", "Ahmedabad Lions")
        page.fill("#nrr-match-overs-input", "15")

        # Click Set Up This Match
        page.click("#btn-apply-nrr-setup")

        # Verify navigation to S03 and pre-filled inputs
        page.wait_for_selector("#screen-S03", state="visible")
        team_a = page.locator("#team-a-name").input_value()
        team_b = page.locator("#team-b-name").input_value()
        overs = page.locator("#match-overs").input_value()

        self.assertEqual(team_a, "Pune Warriors")
        self.assertEqual(team_b, "Ahmedabad Lions")
        self.assertEqual(overs, "15")

if __name__ == "__main__":
    unittest.main()
