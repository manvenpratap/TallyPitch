# tests/test_tournament_leaderboards.py
# End-to-end and Validation Tests for Track 5: Dynamic Tournament Leaderboards & Cap Honors Engine (S19)
# Covers Orange Cap (runs), Purple Cap (wickets), Tournament MVP, Maximum Sixes, Top 5 tables, and live score aggregation.

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestTournamentLeaderboards(unittest.TestCase):
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

    def test_leaderboard_podium_initial_rendering(self):
        """Verify initial S19 honors podium rendering and top-5 batting table"""
        # Navigate to tournaments screen
        self.page.evaluate("() => navigate('tournaments')")
        self.page.wait_for_selector("#leader-orange-name", state="visible")

        # Check Orange Cap, Purple Cap, MVP, and Maximum Sixes initial values
        orange_name = self.page.locator("#leader-orange-name").inner_text()
        purple_name = self.page.locator("#leader-purple-name").inner_text()
        mvp_name = self.page.locator("#leader-mvp-name").inner_text()
        sixes_name = self.page.locator("#leader-sixes-name").inner_text()

        self.assertEqual(orange_name, "Rohit Sharma")
        self.assertEqual(purple_name, "Jasprit Bumrah")
        self.assertEqual(mvp_name, "Hardik Pandya")
        self.assertEqual(sixes_name, "Rohit Sharma")

        # Verify Batting Top 5 rows
        batting_rows = self.page.locator("#tournament-batting-leaderboard-tbody tr")
        self.assertEqual(batting_rows.count(), 5)
        self.assertIn("[ORANGE CAP]", batting_rows.nth(0).inner_text())

        # Verify accessible tooltip on recalculate button
        refresh_btn = self.page.locator("#btn-refresh-leaderboard")
        self.assertTrue(refresh_btn.is_visible())
        self.assertEqual(refresh_btn.get_attribute("data-tooltip"), "Recalculate tournament player statistics and rankings")

    def test_leaderboard_tab_switching(self):
        """Verify switching between Batting Top 5 and Bowling Top 5 views"""
        self.page.evaluate("() => navigate('tournaments')")
        self.page.wait_for_selector("#btn-tab-leader-bowling", state="visible")

        # Switch to Bowling
        self.page.click("#btn-tab-leader-bowling")
        bowling_view = self.page.locator("#leader-view-bowling")
        batting_view = self.page.locator("#leader-view-batting")

        self.assertTrue(bowling_view.is_visible())
        self.assertFalse(batting_view.is_visible())

        # Check Bowling Top 5 rows
        bowling_rows = self.page.locator("#tournament-bowling-leaderboard-tbody tr")
        self.assertEqual(bowling_rows.count(), 5)
        self.assertIn("[PURPLE CAP]", bowling_rows.nth(0).inner_text())

        # Switch back to Batting
        self.page.click("#btn-tab-leader-batting")
        self.assertTrue(batting_view.is_visible())
        self.assertFalse(bowling_view.is_visible())

    def test_dynamic_cap_recalculation_on_live_scoring(self):
        """Verify dynamic cap honor reassignment when live match stats overtake tournament leaders"""
        self.page.evaluate("() => navigate('tournaments')")

        # Simulate live match stats where Virat Kohli scores 50 runs (total 218 > Rohit 184)
        # and Mohammed Siraj takes 4 wickets (total 10 > Bumrah 8)
        self.page.evaluate("""() => {
            state.innings2.batters['B1'] = {
                id: 'B1',
                name: 'Virat Kohli',
                runs: 50,
                balls: 28,
                fours: 4,
                sixes: 3,
                isOut: false
            };
            state.innings1.bowlers['B8'] = {
                id: 'B8',
                name: 'Mohammed Siraj',
                legalBalls: 24,
                runsConceded: 20,
                wickets: 4,
                maidens: 1
            };
            renderTournamentLeaderboards();
        }""")

        # Orange Cap should now be Virat Kohli
        orange_name = self.page.locator("#leader-orange-name").inner_text()
        orange_stats = self.page.locator("#leader-orange-stats").inner_text()
        self.assertEqual(orange_name, "Virat Kohli")
        self.assertIn("218 runs", orange_stats)

        # Purple Cap should now be Mohammed Siraj
        purple_name = self.page.locator("#leader-purple-name").inner_text()
        purple_stats = self.page.locator("#leader-purple-stats").inner_text()
        self.assertEqual(purple_name, "Mohammed Siraj")
        self.assertIn("10 wkts", purple_stats)

        # Test commitMatchPlayerStatsToTournament persists to tournament ledger
        persisted_stats = self.page.evaluate("""() => {
            commitMatchPlayerStatsToTournament();
            const t = tournamentState.tournaments[0];
            const kohli = t.playerStats.find(p => p.id === 'B1');
            const siraj = t.playerStats.find(p => p.id === 'B8');
            return { kohliRuns: kohli.runs, sirajWkts: siraj.wickets };
        }""")
        self.assertEqual(persisted_stats["kohliRuns"], 218)
        self.assertEqual(persisted_stats["sirajWkts"], 10)

if __name__ == "__main__":
    unittest.main()
