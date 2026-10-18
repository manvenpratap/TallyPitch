# tests/test_wagon_wheel_and_charts.py
# End-to-end tests for Wagon Wheel (S09) and Match Analytics Charts (S14: Manhattan, Worm, Phases)

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestWagonWheelAndCharts(unittest.TestCase):
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

    def test_wagon_wheel_modal_interaction_and_shot_placement(self):
        """Verify opening S09 Wagon Wheel modal, clicking ground canvas, and saving shot placement"""
        page = self.page
        page.click("#tab-S07")

        # 1. Score a boundary 4
        page.click("button:has-text('4 FOUR!')")
        self.assertEqual(page.text_content("#hero-score"), "4/0")

        # 2. Open Wagon Wheel modal
        page.click("#btn-wagon-wheel")
        self.assertTrue(page.is_visible("#wagon-wheel-modal"))
        self.assertIn("open", page.get_attribute("#wagon-wheel-modal", "class"))

        # 3. Click on the SVG ground (e.g. extra cover / long off area)
        page.click("#wagon-wheel-interactive-svg", position={"x": 90, "y": 60})
        
        telemetry = page.text_content("#wagon-telemetry-badge")
        self.assertTrue(len(telemetry) > 0)
        self.assertIn("Zone", telemetry)

        # 4. Save Shot Placement
        page.click("button:has-text('Save Shot Placement')")
        self.assertNotIn("open", page.get_attribute("#wagon-wheel-modal", "class"))

    def test_manhattan_chart_and_worm_chart_rendering(self):
        """Verify S14 Match Progression Charts (Manhattan, Worm, Wagon, Phases) render cleanly with data-tooltips"""
        page = self.page
        page.click("#tab-S07")

        # Deliveries in over 1: 4, 6, 1, 0, wicket
        page.click("button:has-text('4 FOUR!')")
        page.click("button:has-text('6 SIX!')")
        page.click("button:has-text('1 Single')")
        page.click("button:has-text('0 Dot')")

        # Score a wicket
        page.click("button:has-text('🔥 WICKET')")
        self.assertTrue(page.is_visible("#wicket-modal"))
        page.click("button:has-text('Confirm Wicket')")

        # Navigate to Digital Scorecard (S13)
        page.click("#tab-S13")
        self.assertTrue(page.is_visible("#screen-S13"))

        # 1. Manhattan View verification
        manhattan_svg = page.locator("#manhattan-svg-container svg")
        self.assertTrue(manhattan_svg.is_visible())
        bars = page.locator("#manhattan-svg-container .manhattan-bar")
        self.assertTrue(bars.count() > 0)
        # Verify accessible tooltip attribute
        first_bar_tooltip = bars.first.get_attribute("data-tooltip")
        self.assertIn("Over 1:", first_bar_tooltip)

        # 2. Worm Chart Tab verification
        page.click("#btn-chart-worm")
        worm_svg = page.locator("#worm-svg-container svg")
        self.assertTrue(worm_svg.is_visible())
        wicket_pins = page.locator("#worm-svg-container .wicket-pin")
        self.assertTrue(wicket_pins.count() > 0)
        pin_tooltip = wicket_pins.first.get_attribute("data-tooltip")
        self.assertIn("Wicket!", pin_tooltip)

        # 3. Wagon Wheel Summary Tab verification
        page.click("#btn-chart-wagon")
        wagon_svg = page.locator("#scorecard-wagon-svg-container svg")
        self.assertTrue(wagon_svg.is_visible())
        shot_lines = page.locator("#scorecard-wagon-svg-container .wagon-shot-line")
        self.assertTrue(shot_lines.count() >= 4)
        
        # Filter test
        page.click("#btn-wf-boundaries")
        boundary_lines = page.locator("#scorecard-wagon-svg-container .wagon-shot-line")
        self.assertEqual(boundary_lines.count(), 2) # the 4 and the 6

        # 4. Phases Table Tab verification
        page.click("#btn-chart-phases")
        phases_table = page.locator("#chart-view-phases table")
        self.assertTrue(phases_table.is_visible())
        phases_text = page.text_content("#phases-tbody")
        self.assertIn("Powerplay", phases_text)
        self.assertIn("Middle Overs", phases_text)
        self.assertIn("Death Overs", phases_text)


if __name__ == "__main__":
    unittest.main()
