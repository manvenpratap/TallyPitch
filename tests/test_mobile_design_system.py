# tests/test_mobile_design_system.py
# Validation Tests for Mobile Design System (Mobile-First · Touch-First · Platform-Respectful)

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestMobileDesignSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        # Emulate standard physical iPhone (iPhone 13/14/15: 375x812, touch enabled)
        cls.browser = cls.playwright.chromium.launch(headless=True)
        cls.context = cls.browser.new_context(
            viewport={"width": 375, "height": 812},
            device_scale_factor=3,
            is_mobile=True,
            has_touch=True
        )

    @classmethod
    def tearDownClass(cls):
        cls.context.close()
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.page = self.context.new_page()
        self.console_errors = []
        self.page.on("console", lambda msg: self.console_errors.append(msg.text) if msg.type == "error" else None)
        self.page.goto(APP_URL, wait_until="domcontentloaded")

    def tearDown(self):
        self.page.close()
        critical_errors = [e for e in self.console_errors if any(kw in e for kw in ["TypeError", "ReferenceError", "SyntaxError", "is not a function"])]
        self.assertEqual(critical_errors, [], f"Critical console errors observed: {critical_errors}")

    def test_mobile_bottom_navigation_bar_visibility_and_ergonomics(self):
        """Verify the bottom navigation bar is visible on mobile viewport with >= 44px touch targets"""
        page = self.page

        # 1. Assert bottom nav is visible
        bottom_nav = page.locator("nav.mobile-bottom-nav")
        self.assertTrue(bottom_nav.is_visible(), "Mobile bottom nav must be visible on mobile viewport (375x812)")

        # 2. Check 5 core thumb-zone tabs exist
        tabs = ["bottom-nav-S07", "bottom-nav-S13", "bottom-nav-tournaments", "bottom-nav-teams-profiles", "bottom-nav-S03"]
        for tab_id in tabs:
            tab = page.locator(f"#{tab_id}")
            self.assertTrue(tab.count() > 0, f"Tab #{tab_id} must exist in bottom nav")
            box = tab.bounding_box()
            self.assertIsNotNone(box, f"Tab #{tab_id} must have bounding box")
            # Fitts' Law touch target >= 44px
            self.assertGreaterEqual(box["height"], 44, f"Tab #{tab_id} height ({box['height']}px) must be >= 44px")
            self.assertGreaterEqual(box["width"], 44, f"Tab #{tab_id} width ({box['width']}px) must be >= 44px")

        # 3. Initially S07 tab is active
        self.assertTrue(page.locator("#bottom-nav-S07").evaluate("el => el.classList.contains('active')"))

    def test_mobile_bottom_nav_navigation_switching(self):
        """Verify tapping mobile bottom nav items smoothly switches screens and synchronizes active indicators"""
        page = self.page

        # Tap Scorecard (S13)
        page.click("#bottom-nav-S13")
        self.assertTrue(page.locator("#screen-S13").is_visible(), "Screen S13 should be visible")
        self.assertTrue(page.locator("#bottom-nav-S13").evaluate("el => el.classList.contains('active')"))
        self.assertFalse(page.locator("#bottom-nav-S07").evaluate("el => el.classList.contains('active')"))

        # Tap Tournaments
        page.click("#bottom-nav-tournaments")
        self.assertTrue(page.locator("#screen-tournaments").is_visible(), "Screen Tournaments should be visible")
        self.assertTrue(page.locator("#bottom-nav-tournaments").evaluate("el => el.classList.contains('active')"))

        # Tap Teams & Scouting
        page.click("#bottom-nav-teams-profiles")
        self.assertTrue(page.locator("#screen-teams-profiles").is_visible(), "Screen Teams should be visible")
        self.assertTrue(page.locator("#bottom-nav-teams-profiles").evaluate("el => el.classList.contains('active')"))

        # Tap Setup & More
        page.click("#bottom-nav-S03")
        self.assertTrue(page.locator("#screen-S03").is_visible(), "Screen S03 should be visible")
        self.assertTrue(page.locator("#bottom-nav-S03").evaluate("el => el.classList.contains('active')"))

        # Tap back to Scoring Console
        page.click("#bottom-nav-S07")
        self.assertTrue(page.locator("#screen-S07").is_visible(), "Screen S07 should be visible")
        self.assertTrue(page.locator("#bottom-nav-S07").evaluate("el => el.classList.contains('active')"))

    def test_mobile_scoring_keypad_touch_targets_and_actions(self):
        """Verify S07 keypad buttons and primary action CTAs meet Fitts' Law touch target standards"""
        page = self.page
        page.click("#bottom-nav-S07")

        # Verify 6 main scoring keypad buttons >= 50px height
        keypad_buttons = page.locator(".keypad-btn")
        self.assertEqual(keypad_buttons.count(), 6)
        for i in range(6):
            btn = keypad_buttons.nth(i)
            box = btn.bounding_box()
            self.assertIsNotNone(box)
            self.assertGreaterEqual(box["height"], 50, f"Keypad button #{i} height must be >= 50px")

        # Verify extras bar buttons have minimum height 40px
        extra_buttons = page.locator(".extra-btn")
        self.assertEqual(extra_buttons.count(), 5)
        for i in range(5):
            btn = extra_buttons.nth(i)
            box = btn.bounding_box()
            self.assertIsNotNone(box)
            self.assertGreaterEqual(box["height"], 40, f"Extra button #{i} height must be >= 40px")

        # Verify primary actions grid on mobile has prominent Wicket CTA (>= 44px)
        wicket_btn = page.locator("#btn-wicket-action")
        self.assertTrue(wicket_btn.count() > 0)
        wbox = wicket_btn.bounding_box()
        self.assertIsNotNone(wbox)
        self.assertGreaterEqual(wbox["height"], 44, "Wicket button height must be >= 44px")
        # On mobile Wicket spans wider
        self.assertGreaterEqual(wbox["width"], 200, "Wicket button should span prominently across mobile grid")

        # Verify secondary action buttons (Undo, Strike, Wagon, Stream)
        for act_id in ["undo-btn", "btn-wagon-wheel", "btn-stream-overlay-keypad"]:
            btn = page.locator(f"#{act_id}")
            box = btn.bounding_box()
            self.assertIsNotNone(box)
            self.assertGreaterEqual(box["height"], 40, f"Action button #{act_id} must have touch height >= 40px")

    def test_mobile_bottom_sheet_modal_presentation(self):
        """Verify modals present as native bottom sheets on mobile viewports"""
        page = self.page
        page.click("#bottom-nav-S07")

        # Open Wicket Modal
        page.click("#btn-wicket-action")
        modal = page.locator("#wicket-modal")
        self.assertTrue(modal.is_visible())

        # Verify modal-backdrop aligns to bottom
        align_items = modal.evaluate("el => window.getComputedStyle(el).alignItems")
        self.assertEqual(align_items, "flex-end", "Modals on mobile must align to flex-end (bottom sheet)")

        # Verify dialog width occupies full viewport width
        dialog = modal.locator(".modal-dialog")
        dbox = dialog.bounding_box()
        self.assertIsNotNone(dbox)
        self.assertGreaterEqual(dbox["width"], 340, "Bottom sheet dialog should stretch across mobile screen")

        # Close modal
        page.click("#wicket-modal button:has-text('Cancel')")
        self.assertFalse(modal.is_visible())

    def test_mobile_form_inputs_prevent_safari_zoom(self):
        """Verify form controls on mobile have font-size >= 16px to prevent iOS Safari auto-zoom"""
        page = self.page
        page.click("#bottom-nav-S03")

        # Check input font-size
        team_input = page.locator("#team-a-name")
        font_size = team_input.evaluate("el => parseFloat(window.getComputedStyle(el).fontSize)")
        self.assertGreaterEqual(font_size, 16.0, "Form input font size on mobile must be >= 16px to prevent auto-zoom")

        # Check select font-size
        overs_select = page.locator("#match-overs")
        select_font_size = overs_select.evaluate("el => parseFloat(window.getComputedStyle(el).fontSize)")
        self.assertGreaterEqual(select_font_size, 16.0, "Form select font size on mobile must be >= 16px")

if __name__ == "__main__":
    unittest.main()
