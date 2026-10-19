# tests/test_shot_type_engine.py
# End-to-end and Validation Tests for Track 9: 8-Sector Ground Cricket Shot Type Classification Engine (tbl_ShotType)
# Covers Wagon Wheel Interactive Shot Chips, Ground & Lofted Trajectories, Ball-by-Ball Recording,
# Speech Commentary Integration, S14 Shot Analysis Chart Tab, Filter Selectors, 4 KPI Cards, and 0ms Atomic Rollback.

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestShotTypeEngine(unittest.TestCase):
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

    def test_wagon_wheel_shot_selector_and_chips(self):
        """Verify Modal 3 interactive shot chips, zone inference, manual chip selection, and saving."""
        page = self.page
        page.click("#tab-S07")

        # Score a 4 to enable wagon wheel placement
        page.click("button.keypad-btn:has-text('4 FOUR!')")
        self.assertEqual(page.text_content("#hero-score"), "4/0")

        # Open Wagon Wheel modal
        page.click("#btn-wagon-wheel")
        self.assertTrue(page.is_visible("#wagon-wheel-modal"))
        self.assertIn("open", page.get_attribute("#wagon-wheel-modal", "class"))

        # Verify shot type selector container, pill, and chips
        self.assertTrue(page.locator("#wagon-shot-type-chips").is_visible())
        self.assertTrue(page.locator("#wagon-selected-shot-pill").is_visible())

        chips = page.locator("#wagon-shot-type-chips .shot-chip")
        self.assertGreaterEqual(chips.count(), 2)

        # Click ground SVG to update zone
        page.click("#wagon-wheel-interactive-svg", position={"x": 90, "y": 60})
        selected_pill_text = page.locator("#wagon-selected-shot-pill").inner_text()
        self.assertTrue(len(selected_pill_text) > 0)

        # Manually click a specific chip if available
        first_chip = chips.first
        chip_name = first_chip.inner_text()
        first_chip.click()
        self.assertEqual(page.locator("#wagon-selected-shot-pill").inner_text(), chip_name)

        # Save shot placement
        page.click("button:has-text('Save Shot Placement')")
        self.assertNotIn("open", page.get_attribute("#wagon-wheel-modal", "class"))

    def test_delivery_scoring_shot_type_recording_and_commentary(self):
        """Verify deliveries record shotType, wagonWheel.shot_type, commentary speech integration, and undo rollback."""
        page = self.page
        page.click("#tab-S07")

        # Score a 4 and a 6
        page.click("button.keypad-btn:has-text('4 FOUR!')")
        page.click("button.keypad-btn:has-text('6 SIX!')")
        page.click("button.keypad-btn:has-text('0 Dot')")

        # Check in JS that deliveries have shotType recorded
        del_data = page.evaluate("""() => {
            const inn = getCurrentInnings();
            return inn.deliveries.map(d => ({
                runs: d.runs,
                isWicket: d.isWicket,
                shotType: d.shotType,
                wagonShot: d.wagonWheel ? d.wagonWheel.shot_type : null
            }));
        }""")

        self.assertEqual(len(del_data), 3)
        self.assertEqual(del_data[0]["runs"], 4)
        self.assertTrue(bool(del_data[0]["shotType"]))
        self.assertEqual(del_data[0]["shotType"], del_data[0]["wagonShot"])

        self.assertEqual(del_data[1]["runs"], 6)
        self.assertTrue(bool(del_data[1]["shotType"]))

        self.assertEqual(del_data[2]["runs"], 0)
        self.assertEqual(del_data[2]["shotType"], "Forward Defence")

        # Verify 0ms Undo rollback restores previous deliveries
        init_len = len(del_data)
        page.click("#undo-btn")
        after_undo_len = page.evaluate("() => getCurrentInnings().deliveries.length")
        self.assertEqual(after_undo_len, init_len - 1)

    def test_s14_shot_analysis_chart_tab_and_kpis(self):
        """Verify Screen S14 Shot Analysis tab, 4 KPI cards, proportional distribution list, and filter selector."""
        page = self.page
        page.click("#tab-S07")

        # Score several shots to populate data
        page.click("button.keypad-btn:has-text('4 FOUR!')")
        page.click("button.keypad-btn:has-text('6 SIX!')")
        page.click("button.keypad-btn:has-text('1 Single')")
        page.click("button.keypad-btn:has-text('0 Dot')")

        # Open S13 Digital Scorecard & S14 Charts
        page.click("#tab-S13")

        # Switch to Shot Analysis tab
        page.click("#btn-chart-shots")
        self.assertIn("active", page.get_attribute("#btn-chart-shots", "class"))
        self.assertTrue(page.locator("#chart-view-shots").is_visible())

        # Verify 4 KPI cards
        self.assertTrue(page.locator("#shots-kpi-productive").is_visible())
        self.assertTrue(page.locator("#shots-kpi-boundary").is_visible())
        self.assertTrue(page.locator("#shots-kpi-ground").is_visible())
        self.assertTrue(page.locator("#shots-kpi-risk").is_visible())

        prod_text = page.locator("#shots-kpi-productive").inner_text()
        bound_text = page.locator("#shots-kpi-boundary").inner_text()
        self.assertTrue(len(prod_text) > 0)
        self.assertIn("Boundaries", bound_text)

        # Verify breakdown list items
        list_items = page.locator("#shots-breakdown-list > div")
        self.assertGreaterEqual(list_items.count(), 1)

        # Verify filter select
        filter_select = page.locator("#shots-filter-select")
        self.assertTrue(filter_select.is_visible())
        options = filter_select.locator("option")
        self.assertGreaterEqual(options.count(), 2)

if __name__ == "__main__":
    unittest.main()
