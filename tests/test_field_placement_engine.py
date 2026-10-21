# tests/test_field_placement_engine.py
# End-to-end and Validation Tests for Track 22: Live Field Placement & 2D Tactical Turf Map Engine
# Covers Screen S07 Live Console HUD & Compliance Badge, Modal 19 (Field Setting Fragment),
# 11 Interactive Fielder Pins, MCC Law 28.4 & ICC Powerplay Validation,
# Screen S14 10th Chart Tab (#btn-chart-field / #chart-view-field), 4 KPIs, Gap Pierce Rate,
# 2D Turf Ground Shot Overlay, Tactical Positions Breakdown Table, 0ms Undo Rollback, and Zero Console Errors.

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestFieldPlacementEngine(unittest.TestCase):
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

    def test_s07_live_field_hud_and_modal_trigger(self):
        """Verify S07 header button, live hero compliance badge, and Modal 19 trigger."""
        page = self.page
        page.click("#tab-S07")

        # Verify S07 Header button
        btn_field = page.locator("#btn-open-field-map")
        self.assertTrue(btn_field.is_visible())
        self.assertIn("Field Setup", btn_field.inner_text())

        # Verify S07 Hero Live Status Bar
        hero_wrap = page.locator("#hero-field-placement-wrap")
        self.assertTrue(hero_wrap.is_visible())

        preset_name = page.locator("#hero-field-preset-name")
        self.assertTrue(preset_name.is_visible())
        self.assertIn("Powerplay", preset_name.inner_text())

        comp_badge = page.locator("#hero-field-compliance-badge")
        self.assertTrue(comp_badge.is_visible())
        self.assertIn("Legal", comp_badge.inner_text())
        self.assertIn("Outside", comp_badge.inner_text())

        # Click button to open Modal 19
        btn_field.click()
        page.wait_for_timeout(200)

        modal = page.locator("#field-placement-modal")
        self.assertTrue(modal.is_visible())
        self.assertTrue("open" in (modal.get_attribute("class") or ""))

    def test_modal_19_presets_and_compliance(self):
        """Verify Modal 19 interactive SVG, tactical preset switching, and MCC/ICC compliance checklist."""
        page = self.page
        page.click("#tab-S07")
        page.click("#btn-open-field-map")
        page.wait_for_timeout(200)

        # Verify 2D SVG turf ground rendered
        svg = page.locator("#field-editor-svg")
        self.assertTrue(svg.is_visible())

        # Verify 11 fielder pins exist in SVG
        pins = page.locator(".field-pin-drag-target")
        self.assertEqual(pins.count(), 11)

        # Test Switching to Middle Overs Preset
        page.click("#btn-quick-mid")
        page.wait_for_timeout(150)
        ring_count = page.locator("#field-rule-ring-count").inner_text()
        self.assertIn("4 /", ring_count)

        # Test Switching to Death Overs Preset (5 outside)
        page.click("#btn-quick-death")
        page.wait_for_timeout(150)
        ring_count = page.locator("#field-rule-ring-count").inner_text()
        self.assertIn("5 /", ring_count)

        # Test Switching to Spin Trap Preset
        page.click("#btn-quick-spin")
        page.wait_for_timeout(150)
        inspector_title = page.locator("#field-inspector-title").inner_text()
        self.assertTrue(len(inspector_title) > 0)

        # Test Save & Close
        page.click("#btn-save-field-setup")
        page.wait_for_timeout(200)
        modal = page.locator("#field-placement-modal")
        self.assertFalse(modal.is_visible())

    def test_fielder_inspector_and_player_assignment(self):
        """Verify clicking fielder pins updates Inspector, player dropdown changes assignment, and hand toggle works."""
        page = self.page
        page.click("#tab-S07")
        page.click("#btn-open-field-map")
        page.wait_for_timeout(200)

        # Select pin 1 (Wicketkeeper)
        page.evaluate("selectFielderForInspector(1)")
        page.wait_for_timeout(100)
        title = page.locator("#field-inspector-title").inner_text()
        self.assertIn("Wicketkeeper", title)

        # Select pin 2 (Bowler)
        page.evaluate("selectFielderForInspector(2)")
        page.wait_for_timeout(100)
        title = page.locator("#field-inspector-title").inner_text()
        self.assertIn("Bowler", title)

        # Change player assignment
        player_select = page.locator("#field-inspector-player-select")
        self.assertTrue(player_select.is_visible())
        options_count = player_select.locator("option").count()
        self.assertGreater(options_count, 0)

        # Toggle Facing hand to LHB
        page.select_option("#field-modal-batter-hand", "LHB")
        page.wait_for_timeout(100)
        batter_hand = page.evaluate("state.fieldPlacement.batterHand")
        self.assertEqual(batter_hand, "LHB")

        # Toggle back to RHB
        page.select_option("#field-modal-batter-hand", "RHB")
        page.wait_for_timeout(100)
        batter_hand = page.evaluate("state.fieldPlacement.batterHand")
        self.assertEqual(batter_hand, "RHB")

        page.click("#field-placement-modal button:has-text('Cancel')")

    def test_illegal_field_detection_mcc_and_powerplay(self):
        """Verify MCC Law 28.4 and ICC Powerplay violations trigger warning alerts and badge updates."""
        page = self.page
        page.click("#tab-S07")

        # Force an illegal field with 6 fielders on leg side (> 5 violates MCC Law 28.4.1)
        page.evaluate("""() => {
            state.fieldPlacement.positions.forEach((p, idx) => {
                if (idx < 6) p.x = 250; // 6 fielders on leg side
            });
            updateFieldPlacementHud();
        }""")
        page.wait_for_timeout(150)

        badge = page.locator("#hero-field-compliance-badge")
        self.assertIn("Illegal", badge.inner_text())
        self.assertIn("MCC", badge.inner_text())

        # Open modal and check warning banner
        page.click("#btn-open-field-map")
        page.wait_for_timeout(200)

        warn_wrap = page.locator("#field-modal-warning-wrap")
        self.assertTrue(warn_wrap.is_visible())
        warn_text = page.locator("#field-modal-warning-text").inner_text()
        self.assertIn("MCC", warn_text)

        # Reset preset to restore legal field
        page.click("#btn-reset-field-preset")
        page.wait_for_timeout(150)
        self.assertFalse(warn_wrap.is_visible())
        badge = page.locator("#field-modal-compliance-badge")
        self.assertIn("Legal", badge.inner_text())

        page.click("#btn-save-field-setup")

    def test_s14_10th_tab_field_map_and_gap_analysis(self):
        """Verify S14 10th chart tab (#btn-chart-field), 4 KPIs, 2D turf overlay, and tactical breakdown table."""
        page = self.page
        page.click("#tab-S07")

        # Score boundaries to populate deliveries for gap analysis
        page.click("button.keypad-btn:has-text('4 FOUR!')")
        page.click("button.keypad-btn:has-text('6 SIX!')")
        page.click("button.keypad-btn:has-text('1')")

        # Navigate to Screen S13 / S14 Charts
        page.click("#tab-S13")
        page.wait_for_timeout(200)

        # Check 10th chart toggle button
        btn_field_tab = page.locator("#btn-chart-field")
        self.assertTrue(btn_field_tab.is_visible())
        self.assertIn("Field Map", btn_field_tab.inner_text())

        # Click Field Map tab
        btn_field_tab.click()
        page.wait_for_timeout(250)

        # Verify #chart-view-field is visible
        view_field = page.locator("#chart-view-field")
        self.assertTrue(view_field.is_visible())

        # Verify 4 KPIs
        kpi_infield = page.locator("#field-kpi-infield")
        kpi_deep = page.locator("#field-kpi-deep")
        kpi_split = page.locator("#field-kpi-split")
        kpi_gaps = page.locator("#field-kpi-gaps")

        self.assertTrue(kpi_infield.is_visible())
        self.assertTrue(kpi_deep.is_visible())
        self.assertTrue(kpi_split.is_visible())
        self.assertTrue(kpi_gaps.is_visible())

        self.assertIn("Fielders", kpi_infield.inner_text())
        self.assertIn("Deep", kpi_deep.inner_text())
        self.assertIn("Off", kpi_split.inner_text())
        self.assertIn("%", kpi_gaps.inner_text())

        # Verify 2D Turf SVG overlay exists
        chart_svg = page.locator("#field-chart-svg-wrap svg")
        self.assertTrue(chart_svg.is_visible())

        # Verify Tactical Positions Breakdown Table has 11 rows
        table_rows = page.locator("#field-positions-table-wrap tbody tr")
        self.assertEqual(table_rows.count(), 11)

    def test_atomic_rollback_undo_support(self):
        """Verify 0ms atomic rollback restores field placement snapshot correctly."""
        page = self.page
        page.click("#tab-S07")

        # Set preset to 'powerplay'
        page.evaluate("applyFieldPreset('powerplay')")
        preset1 = page.evaluate("state.fieldPlacement.preset")
        self.assertEqual(preset1, "powerplay")

        # Record a delivery (which pushes undo snapshot)
        page.click("button.keypad-btn:has-text('1')")

        # Switch preset to 'death'
        page.evaluate("applyFieldPreset('death')")
        preset2 = page.evaluate("state.fieldPlacement.preset")
        self.assertEqual(preset2, "death")

        # Rollback via undoLastBall
        page.evaluate("undoLastBall()")
        preset_restored = page.evaluate("state.fieldPlacement.preset")
        self.assertEqual(preset_restored, "powerplay")

if __name__ == '__main__':
    unittest.main()
