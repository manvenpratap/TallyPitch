# tests/test_player_form_guide_engine.py
# End-to-end and Validation Tests for Track 21: Player Career Form Guide & Momentum Trajectory Engine
# Reverse-engineered from CricHeroes CurrentFormViewAllActivity, player_batting_current_form,
# getBattingCurrentForm, getBowlingCurrentForm, and team_current_form.
# Covers S20 Profile Form Card, 4 Telemetry KPIs, 5-Match Sparkline SVG, Batting/Bowling Toggle,
# Modal 18 (CurrentFormViewAllActivity), S06 Scouting Table Action, Live Match Sync, and Zero Console Errors.

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestPlayerFormGuideEngine(unittest.TestCase):
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

    def test_player_form_guide_rendering_and_kpis(self):
        """Verify S20 Player Profile form guide card, 4 KPI cards, SVG sparkline curve, and Batting/Bowling toggle."""
        page = self.page
        page.evaluate("() => navigate('teams-profiles')")

        # Verify Form Guide card visibility
        form_card = page.locator("#player-form-guide-card")
        self.assertTrue(form_card.is_visible())

        # Verify Form Badge
        badge = page.locator("#player-form-badge")
        self.assertTrue(badge.is_visible())
        badge_text = badge.inner_text()
        self.assertTrue("RED HOT" in badge_text or "CONSISTENT" in badge_text or "COLD SLUMP" in badge_text)

        # Verify 4 Telemetry KPI Cards
        avg_el = page.locator("#form-kpi-avg")
        sr_econ_el = page.locator("#form-kpi-sr-econ")
        bnd_dot_el = page.locator("#form-kpi-boundary-dot")
        trend_el = page.locator("#form-kpi-trend")

        self.assertTrue(avg_el.is_visible())
        self.assertTrue(sr_econ_el.is_visible())
        self.assertTrue(bnd_dot_el.is_visible())
        self.assertTrue(trend_el.is_visible())

        # Check default Batting Form labels
        self.assertEqual(page.locator("#form-kpi-sr-econ-title").inner_text(), "STRIKE RATE")
        self.assertEqual(page.locator("#form-kpi-bnd-dot-title").inner_text(), "BOUNDARY %")

        # Verify SVG Sparkline Curve
        sparkline_svg = page.locator("#form-sparkline-container svg")
        self.assertTrue(sparkline_svg.is_visible())
        circles = page.locator("#form-sparkline-container svg circle")
        self.assertEqual(circles.count(), 5)

        # Verify Dismissal Radar Bar
        radar_bar = page.locator("#form-radar-bar")
        self.assertTrue(radar_bar.is_visible())

        # Verify 5 Match cards in reel
        reel = page.locator("#form-matches-reel .card")
        self.assertEqual(reel.count(), 5)

        # Switch to Bowling Form
        bowl_btn = page.locator("#btn-form-type-bowling")
        self.assertTrue(bowl_btn.is_visible())
        bowl_btn.click()

        # Verify KPI titles update for bowling
        self.assertEqual(page.locator("#form-kpi-sr-econ-title").inner_text(), "ECONOMY RATE")
        self.assertEqual(page.locator("#form-kpi-bnd-dot-title").inner_text(), "DOT BALL %")
        self.assertIn("active", bowl_btn.get_attribute("class"))

        # Switch back to Batting Form
        bat_btn = page.locator("#btn-form-type-batting")
        bat_btn.click()
        self.assertEqual(page.locator("#form-kpi-sr-econ-title").inner_text(), "STRIKE RATE")
        self.assertIn("active", bat_btn.get_attribute("class"))

    def test_modal_18_form_view_all_and_player_switching(self):
        """Verify Modal 18 (CurrentFormViewAllActivity) launch, player switching, and Escape key dismissal."""
        page = self.page
        page.evaluate("() => navigate('teams-profiles')")

        # Click Form Guide button on S20 profile header
        btn_modal = page.locator("#btn-open-form-guide")
        self.assertTrue(btn_modal.is_visible())
        btn_modal.click()

        # Modal 18 opens
        modal = page.locator("#player-form-modal")
        self.assertTrue(modal.is_visible())
        self.assertIn("open", modal.get_attribute("class"))

        # Check Modal Title
        self.assertIn("CurrentFormViewAllActivity", modal.locator(".modal-title").inner_text())

        # Switch player inside modal (Select A8 Jasprit Bumrah)
        modal_select = page.locator("#modal-form-player-select")
        self.assertTrue(modal_select.is_visible())
        modal_select.select_option("A8")

        # Verify modal updates player name and avatar
        self.assertIn("Bumrah", page.locator("#modal-form-player-name").inner_text())
        self.assertEqual(page.locator("#modal-form-avatar").inner_text(), "J")

        # Dismiss modal with Escape
        page.keyboard.press("Escape")
        self.assertFalse(modal.is_visible())

    def test_scouting_table_form_action_and_live_scoring_sync(self):
        """Verify S06 Player Scouting '📈 Form' button and live match ongoing performance integration."""
        page = self.page
        page.evaluate("() => navigate('teams-profiles')")

        # Locate Form button on scouting table for A1 (Rohit Sharma)
        scout_btn = page.locator("#btn-scout-form-A1")
        self.assertTrue(scout_btn.is_visible())
        self.assertIn("Form", scout_btn.inner_text())

        # Click Form button from scouting table
        scout_btn.click()
        modal = page.locator("#player-form-modal")
        self.assertTrue(modal.is_visible())
        page.keyboard.press("Escape")
        self.assertFalse(modal.is_visible())

        # Navigate to scoring S07 and score a 4
        page.evaluate("() => navigate('S07')")
        page.evaluate("() => recordBall(4)")

        # Return to S20 profile
        page.evaluate("() => navigate('teams-profiles')")

        # Check 5th match in reel has LIVE badge
        reel = page.locator("#form-matches-reel")
        self.assertIn("LIVE", reel.inner_text())
        self.assertIn("Today (Live)", reel.inner_text())
