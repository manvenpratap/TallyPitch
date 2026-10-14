# tests/test_cricket_engine.py
# End-to-end Playwright tests for CricHeroes Replica core flows & edge cases

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestCricHeroesFlows(unittest.TestCase):
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
        self.page.goto(APP_URL)

    def tearDown(self):
        self.page.close()
        self.assertEqual(self.console_errors, [], f"Console errors observed: {self.console_errors}")

    def test_F01_H1_match_setup_and_openers(self):
        """F01-H1: Setup match, record toss, select openers, and enter live console"""
        page = self.page
        page.click("#tab-S03")

        page.fill("#team-a-name", "Chennai Super Kings")
        page.fill("#team-b-name", "Kolkata Knight Riders")
        page.select_option("#match-overs", "10")
        page.click("button[type='submit']")

        # S05: The Toss
        self.assertTrue(page.is_visible("#screen-S05"))
        page.click("#btn-toss-bat")
        page.click("text=Confirm & Select Openers (S06) →")

        # S06: Openers
        self.assertTrue(page.is_visible("#screen-S06"))
        page.click("text=Start Live Scoring (S07)")

        # S07: Console should be active
        self.assertTrue(page.is_visible("#screen-S07"))
        self.assertEqual(page.text_content("#hero-score"), "0/0")
        self.assertIn("10", page.text_content("#hero-overs"))

    def test_F02_H1_ball_by_ball_and_strike_rotation(self):
        """F02-H1: Ball scoring and automatic strike rotation on odd runs"""
        page = self.page
        page.click("#tab-S07")

        striker_name = page.text_content("#active-striker-name")
        self.assertIn("Rohit Sharma", striker_name)

        # 1. Tap 1 run (odd run) -> strike must swap to Ishan Kishan
        page.click("button:has-text('1 Single')")
        self.assertEqual(page.text_content("#hero-score"), "1/0")
        
        new_striker = page.text_content("#active-striker-name")
        self.assertIn("Ishan Kishan", new_striker)
        self.assertEqual(page.text_content("#active-striker-runs"), "0")

        # 2. Tap 4 runs (even run) -> strike remains with Ishan Kishan
        page.click("button:has-text('4 FOUR!')")
        self.assertEqual(page.text_content("#hero-score"), "5/0")
        self.assertIn("Ishan Kishan", page.text_content("#active-striker-name"))
        self.assertEqual(page.text_content("#active-striker-runs"), "4")

    def test_F02_E1_consecutive_boundaries_keep_strike(self):
        """F02-E1: Consecutive boundaries (4, 6) keep strike on same batter"""
        page = self.page
        page.click("#tab-S07")

        initial_striker = page.text_content("#active-striker-name")
        page.click("button:has-text('4 FOUR!')")
        self.assertEqual(page.text_content("#active-striker-name"), initial_striker)

        page.click("button:has-text('6 SIX!')")
        self.assertEqual(page.text_content("#active-striker-name"), initial_striker)
        self.assertEqual(page.text_content("#active-striker-runs"), "10")
        self.assertEqual(page.text_content("#hero-score"), "10/0")

    def test_F03_H1_extras_and_free_hit(self):
        """F03-H1: Extras recording (Wide & No Ball) without legal ball advancement"""
        page = self.page
        page.click("#tab-S07")

        # Score Wide
        page.click("button:has-text('+1 Wide')")
        self.assertEqual(page.text_content("#hero-score"), "1/0")
        self.assertIn("0.0", page.text_content("#hero-overs"))

        # Score No Ball
        page.click("button:has-text('+1 No Ball')")
        self.assertEqual(page.text_content("#hero-score"), "2/0")
        self.assertIn("0.0", page.text_content("#hero-overs"))

        # Score 1 run (legal) -> now 0.1
        page.click("button:has-text('1 Single')")
        self.assertEqual(page.text_content("#hero-score"), "3/0")
        self.assertIn("0.1", page.text_content("#hero-overs"))

    def test_F04_H1_wicket_dismissal(self):
        """F04-H1: Dismissal modal, bowler attribution, and fall of wicket"""
        page = self.page
        page.click("#tab-S07")

        page.click("button:has-text('WICKET')")
        self.assertTrue(page.is_visible("#wicket-modal"))

        page.click("input[value='Caught']")
        page.fill("#fielder-input", "Ravindra Jadeja")
        page.click("button:has-text('Confirm Wicket')")

        self.assertEqual(page.text_content("#hero-score"), "0/1")
        self.assertIn("0.1", page.text_content("#hero-overs"))

        page.click("#tab-S13")
        self.assertIn("1-0", page.text_content("#scorecard-fow-wrap"))
        self.assertIn("c Ravindra Jadeja", page.text_content("#scorecard-batting-tbody"))

    def test_F05_H1_over_completion_and_bowler_handover(self):
        """F05-H1: 6 legal balls trigger over completion modal and bowler handover"""
        page = self.page
        page.click("#tab-S07")

        # Bowl 6 legal balls (dots)
        for _ in range(6):
            page.click("button:has-text('0 Dot')")

        # Over completion modal should appear
        self.assertTrue(page.is_visible("#over-modal"))
        self.assertIn("Over 1 Complete", page.text_content("#over-modal-title"))

        # Confirm next bowler
        page.click("button:has-text('Start Next Over →')")
        self.assertFalse(page.is_visible("#over-modal"))
        self.assertIn("1.0", page.text_content("#hero-overs"))

    def test_F06_H1_undo_rollback_stack(self):
        """F06-H1: Rollback delivery and verify complete restoration of match state"""
        page = self.page
        page.click("#tab-S07")

        page.click("button:has-text('6 SIX!')")
        self.assertEqual(page.text_content("#hero-score"), "6/0")

        page.click("#undo-btn")
        self.assertEqual(page.text_content("#hero-score"), "0/0")
        self.assertIn("0.0", page.text_content("#hero-overs"))
        self.assertEqual(page.text_content("#active-striker-runs"), "0")

    def test_F08_H1_scorecard_and_commentary_generation(self):
        """F08-H1: Digital scorecard populated with live commentary stream"""
        page = self.page
        page.click("#tab-S07")

        page.click("button:has-text('4 FOUR!')")
        page.click("button:has-text('1 Single')")

        page.click("#tab-S13")
        self.assertTrue(page.is_visible("#screen-S13"))
        self.assertIn("5/0", page.text_content("#scorecard-total-txt"))
        
        commentary = page.text_content("#commentary-list")
        self.assertIn("FOUR!", commentary)
        self.assertIn("1 RUN(S)", commentary)

    def test_F09_H1_tournament_wizard_fixtures_and_standings(self):
        """F09-H1: Tournament management hub, fixtures, NRR standings, and cap leaderboards"""
        page = self.page
        page.click("#tab-tournaments")
        self.assertTrue(page.is_visible("#screen-tournaments"))

        # Verify tournament wizard toggle
        page.click("#btn-toggle-tournament-mode")
        self.assertTrue(page.is_visible("#tournament-create-panel"))

        # Verify groups are listed (S16)
        self.assertIn("Mumbai Strikers", page.text_content("#group-a-teams-list"))
        self.assertIn("Bangalore Blasters", page.text_content("#group-b-teams-list"))

        # Verify automated round-robin fixtures generated (S17)
        self.assertTrue(page.is_visible("#tournament-fixtures-container"))
        fixtures_text = page.text_content("#tournament-fixtures-container")
        self.assertIn("Mumbai Strikers vs Pune Warriors", fixtures_text)
        self.assertIn("Oval Ground, Mumbai", fixtures_text)

        # Verify dynamic points table & ICC NRR (S18)
        standings_text = page.text_content("#tournament-standings-tbody")
        self.assertIn("Mumbai Strikers", standings_text)
        self.assertIn("+1.650", standings_text)

        # Verify tournament leaderboards (S19)
        self.assertEqual(page.text_content("#leader-orange-name"), "Rohit Sharma")
        self.assertEqual(page.text_content("#leader-purple-name"), "Jasprit Bumrah")
        self.assertEqual(page.text_content("#leader-mvp-name"), "Hardik Pandya")

    def test_F10_H1_teams_roster_and_player_profiles(self):
        """F10-H1: Team squad management, role assignments (S01, S21), and digital career record (S20)"""
        page = self.page
        page.click("#tab-teams-profiles")
        self.assertTrue(page.is_visible("#screen-teams-profiles"))

        # Add a new player to roster with role selection (S01, S21)
        page.fill("#new-player-name", "Yashasvi Jaiswal")
        page.fill("#new-player-phone", "+919876543299")
        page.select_option("#new-player-role", "Batter")
        page.select_option("#new-player-flag", "none")
        page.click("button:has-text('Add Player')")

        # Verify player appears in active roster table
        roster_text = page.text_content("#team-roster-tbody")
        self.assertIn("Yashasvi Jaiswal", roster_text)
        self.assertIn("Batter", roster_text)

        # Verify digital career record (S20)
        self.assertIn("Rohit Sharma", page.text_content("#profile-name"))
        self.assertEqual(page.text_content("#prof-bat-matches"), "42")
        self.assertEqual(page.text_content("#prof-bat-runs"), "1,480")
        self.assertEqual(page.text_content("#prof-bat-avg"), "44.8")
        self.assertEqual(page.text_content("#prof-bat-sr"), "146.2")

if __name__ == "__main__":
    unittest.main()
