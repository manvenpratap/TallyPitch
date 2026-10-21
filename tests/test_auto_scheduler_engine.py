# tests/test_auto_scheduler_engine.py
# End-to-end and Validation Tests for Track 18: Automated Tournament Fixture Scheduler & Calendar Generator
# Reverse-engineered from CricHeroes ScheduleMatchAutoActivity and FilterAutoScheduleActivity.
# Covers S17 UI Actions, Stage Filters, Modal 16 Auto Scheduler, Conflict-Free Algorithm, iCal (.ics) & Sheet Export, Pre-fill S03 Setup, and Zero Console Errors.

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestAutoSchedulerEngine(unittest.TestCase):
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

    def test_auto_scheduler_ui_elements(self):
        """Verify S17 has Auto Scheduler controls and opens Modal 16 with parameters and telemetry."""
        page = self.page
        page.evaluate("() => navigate('tournaments')")

        btn_open = page.locator("#btn-open-auto-scheduler")
        self.assertTrue(btn_open.is_visible())
        self.assertIn("fixture scheduler", btn_open.get_attribute("data-tooltip").lower())

        btn_ical = page.locator("#btn-export-fixtures-ical")
        self.assertTrue(btn_ical.is_visible())

        btn_copy = page.locator("#btn-copy-fixtures-sheet")
        self.assertTrue(btn_copy.is_visible())

        btn_regen = page.locator("#btn-regenerate-fixtures")
        self.assertTrue(btn_regen.is_visible())

        # Verify Stage filter buttons
        self.assertTrue(page.locator("#btn-fix-filter-all").is_visible())
        self.assertTrue(page.locator("#btn-fix-filter-groupA").is_visible())
        self.assertTrue(page.locator("#btn-fix-filter-groupB").is_visible())
        self.assertTrue(page.locator("#btn-fix-filter-knockouts").is_visible())

        # Open Modal 16
        btn_open.click()
        page.wait_for_selector("#auto-scheduler-modal", state="visible")

        # Verify form controls
        self.assertTrue(page.locator("#auto-sched-format").is_visible())
        self.assertTrue(page.locator("#auto-sched-start-date").is_visible())
        self.assertTrue(page.locator("#auto-sched-cadence").is_visible())
        self.assertTrue(page.locator("#auto-sched-slots").is_visible())
        self.assertTrue(page.locator("#auto-sched-venues").is_visible())
        self.assertTrue(page.locator("#btn-generate-schedule").is_visible())

        # Verify Telemetry KPI cards
        self.assertTrue(page.locator("#sched-kpi-total-matches").is_visible())
        self.assertTrue(page.locator("#sched-kpi-total-days").is_visible())
        self.assertTrue(page.locator("#sched-kpi-venues-count").is_visible())
        self.assertTrue(page.locator("#sched-kpi-conflicts").is_visible())
        self.assertIn("0 Conflicts", page.locator("#sched-kpi-conflicts").inner_text())

    def test_schedule_generation_and_persistence(self):
        """Verify conflict-free schedule generation, preview rendering, and application to tournament fixtures."""
        page = self.page
        page.evaluate("() => navigate('tournaments')")
        page.click("#btn-open-auto-scheduler")
        page.wait_for_selector("#auto-scheduler-modal", state="visible")

        # Generate schedule
        page.click("#btn-generate-schedule")

        # Check preview items
        preview_items = page.locator("#auto-sched-preview-list > div")
        count = preview_items.count()
        self.assertGreaterEqual(count, 5)

        # Apply schedule
        page.click("#btn-apply-auto-schedule")
        page.wait_for_selector("#auto-scheduler-modal", state="hidden")

        # Verify fixtures container updated on S17
        cards = page.locator("#tournament-fixtures-container .fixture-card")
        self.assertEqual(cards.count(), count)

        # Test stage filtering on S17
        page.click("#btn-fix-filter-groupA")
        ga_cards = page.locator("#tournament-fixtures-container .fixture-card")
        for i in range(ga_cards.count()):
            self.assertIn("Group A", ga_cards.nth(i).inner_text())

        # Reset filter to all
        page.click("#btn-fix-filter-all")
        self.assertEqual(page.locator("#tournament-fixtures-container .fixture-card").count(), count)

    def test_prefill_match_setup_and_exports(self):
        """Verify 1-click 'Score Match' button pre-fills S03 setup, and iCal / clipboard exports run without errors."""
        page = self.page
        page.evaluate("() => navigate('tournaments')")

        # Ensure fixtures are rendered
        page.click("#btn-regenerate-fixtures")
        first_card = page.locator("#tournament-fixtures-container .fixture-card").first
        self.assertTrue(first_card.is_visible())

        # Test iCal export function
        res_ical = page.evaluate("() => { try { downloadTournamentIcsCalendar(); return true; } catch(e) { return e.message; } }")
        self.assertTrue(res_ical is True)

        # Test Copy sheet function
        res_copy = page.evaluate("() => { try { copyTournamentFixtureSheet(); return true; } catch(e) { return e.message; } }")
        self.assertTrue(res_copy is True)

        # Click Score Match on first fixture
        score_btn = first_card.locator("button.btn-primary")
        score_btn.click()

        # Verify navigation to S03
        page.wait_for_selector("#screen-S03.active", state="visible")
        self.assertTrue(page.locator("#s03-scheduled-fixture-banner").is_visible())

        # Verify team inputs populated
        team_a = page.locator("#team-a-name").input_value()
        team_b = page.locator("#team-b-name").input_value()
        self.assertIn("Mumbai Strikers", team_a)
        self.assertIn("Pune Warriors", team_b)

if __name__ == "__main__":
    unittest.main()
