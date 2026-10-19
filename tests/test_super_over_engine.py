# tests/test_super_over_engine.py
# End-to-end and Validation Tests for Track 7: Official ICC Super Over Engine (tbl_MatchSuperOverBallByBall)
# Covers automated tied match detection, Modal 11 setup (3 nominated batters & 1 bowler),
# live S07 console Super Over mode, 6-ball / 2-wicket limits, target calculation,
# winner declaration, digital scorecard breakdown (S13), and 0ms atomic rollback.

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestSuperOverEngine(unittest.TestCase):
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

    def test_tied_match_detection_and_button_visibility(self):
        """Verify #btn-launch-super-over is hidden on standard win and visible on match tie"""
        # 1. Simulate standard win
        self.page.evaluate("""
            state.innings1.totalRuns = 120;
            state.innings2.totalRuns = 124;
            state.innings2.targetRuns = 121;
            declareMatchWinner();
        """)
        so_btn = self.page.locator("#btn-launch-super-over")
        self.assertFalse(so_btn.is_visible())

        # Close result modal
        self.page.evaluate("closeModal('match-result-modal')")

        # 2. Simulate match tie (scores equal)
        self.page.evaluate("""
            state.innings1.totalRuns = 135;
            state.innings2.totalRuns = 135;
            state.innings2.targetRuns = 136;
            declareMatchWinner();
        """)
        self.assertTrue(so_btn.is_visible())
        self.assertIn("SUPER OVER", so_btn.inner_text().upper())
        self.assertTrue(so_btn.get_attribute("data-tooltip") is not None)

        # Result modal text should indicate match tie
        modal_title = self.page.locator("#winner-modal-title").inner_text()
        modal_desc = self.page.locator("#winner-modal-desc").inner_text()
        self.assertEqual(modal_title, "Match Tied!")
        self.assertIn("Super Over applicable", modal_desc)

    def test_super_over_modal_nominations_and_first_innings_scoring(self):
        """Verify Super Over Modal 11 opens, nominates 3 batters and 1 bowler, and launches S07 Super Over console"""
        # Trigger tied match and open Super Over setup modal
        self.page.evaluate("""
            state.innings1.totalRuns = 100;
            state.innings2.totalRuns = 100;
            declareMatchWinner();
            openSuperOverSetupModal(1);
        """)

        # Modal 11 should be open
        so_modal = self.page.locator("#super-over-modal")
        self.assertTrue(so_modal.is_visible())

        # Select 3 distinct nominated batters and 1 bowler
        self.page.select_option("#so-striker-select", "B1")      # Virat Kohli
        self.page.select_option("#so-non-striker-select", "B2")  # Faf du Plessis
        self.page.select_option("#so-reserve-select", "B4")      # Glenn Maxwell
        self.page.select_option("#so-bowler-select", "A8")       # Jasprit Bumrah

        # Click Start Super Over (1st Innings)
        self.page.click("#btn-start-so-action")

        # Modal should close and S07 should reflect Super Over live status
        self.page.wait_for_selector("#super-over-active-banner", state="visible")
        status_txt = self.page.locator("#hero-match-status").inner_text()
        overs_txt = self.page.locator("#hero-overs").inner_text()
        self.assertIn("SUPER OVER", status_txt)
        self.assertIn("1ST INNINGS", status_txt)
        self.assertIn("Max 6b • 2 Wkts", overs_txt)

        # Active striker should be Virat Kohli
        striker_name = self.page.locator("#active-striker-name").inner_text()
        self.assertIn("Virat Kohli", striker_name)

        # Score a 6 and a 4
        self.page.evaluate("recordBall(6)")
        self.page.evaluate("recordBall(4)")

        # Verify score is 10/0 in 0.2 overs
        score_txt = self.page.locator("#hero-score").inner_text()
        self.assertEqual(score_txt, "10/0")

        # Verify CricHeroes tbl_MatchSuperOverBallByBall schema tagging
        inn1_deliveries = self.page.evaluate("state.superOver.inn1.deliveries")
        self.assertEqual(len(inn1_deliveries), 2)
        self.assertEqual(inn1_deliveries[0]["superOverNumber"], 1)
        self.assertEqual(inn1_deliveries[0]["superOverInning"], 1)
        self.assertEqual(inn1_deliveries[0]["runs"], 6)
        self.assertEqual(inn1_deliveries[1]["runs"], 4)

        # Test 0ms atomic rollback
        self.page.evaluate("undoLastBall()")
        self.assertEqual(self.page.locator("#hero-score").inner_text(), "6/0")
        self.assertEqual(len(self.page.evaluate("state.superOver.inn1.deliveries")), 1)

    def test_super_over_wicket_limits_innings_break_and_chase_completion(self):
        """Verify 2-wicket limit, reserve batter rollover, chase target, winner declaration, and S13 scorecard"""
        # Setup Super Over directly via API
        self.page.evaluate("""
            state.innings1.totalRuns = 150;
            state.innings2.totalRuns = 150;
            openSuperOverSetupModal(1);
        """)
        self.page.select_option("#so-striker-select", "B1")
        self.page.select_option("#so-non-striker-select", "B2")
        self.page.select_option("#so-reserve-select", "B4")
        self.page.select_option("#so-bowler-select", "A8")
        self.page.click("#btn-start-so-action")

        # Score a 4 by striker B1
        self.page.evaluate("recordBall(4)")

        # 1st Wicket falls: B1 is caught
        self.page.evaluate("""
            openWicketModal();
            document.getElementById('out-batter-select').value = 'B1';
            document.querySelector('input[name="dismissal_type"][value="Caught"]').checked = true;
            document.getElementById('fielder-input').value = 'Rohit';
            confirmWicketDismissal();
        """)

        # Reserve batter B4 (Glenn Maxwell) must now be active
        striker_name = self.page.locator("#active-striker-name").inner_text()
        self.assertIn("Glenn Maxwell", striker_name)
        self.assertEqual(self.page.locator("#hero-score").inner_text(), "4/1")

        # Score a 2
        self.page.evaluate("recordBall(2)")

        # 2nd Wicket falls: B2 is bowled -> ALL OUT in Super Over (Max 2 wickets)!
        self.page.evaluate("""
            openWicketModal();
            document.getElementById('out-batter-select').value = 'B2';
            document.querySelector('input[name="dismissal_type"][value="Bowled"]').checked = true;
            confirmWicketDismissal();
        """)

        # Team B is all out at 6/2. Target for Team A should be 7!
        target_runs = self.page.evaluate("state.superOver.inn2.targetRuns")
        self.assertEqual(target_runs, 7)

        # Innings 2 setup modal should now be open
        so_modal = self.page.locator("#super-over-modal")
        self.assertTrue(so_modal.is_visible())
        target_banner = self.page.locator("#so-target-banner")
        self.assertTrue(target_banner.is_visible())
        self.assertIn("7", target_banner.inner_text())

        # Nominate Team A batters (Striker: A1, Non-Striker: A2, Reserve: A3) & Bowler (B8 Siraj)
        self.page.select_option("#so-striker-select", "A1")
        self.page.select_option("#so-non-striker-select", "A2")
        self.page.select_option("#so-reserve-select", "A3")
        self.page.select_option("#so-bowler-select", "B8")
        self.page.click("#btn-start-so-action")

        # Innings 2 is now LIVE on S07
        status_txt = self.page.locator("#hero-match-status").inner_text()
        self.assertIn("2ND INNINGS (CHASE)", status_txt)
        target_txt = self.page.locator("#hero-target").inner_text()
        self.assertEqual(target_txt, "7")

        # Hit a SIX (6 runs) -> Score 6/0, need 1 run
        self.page.evaluate("recordBall(6)")
        self.assertEqual(self.page.locator("#hero-score").inner_text(), "6/0")

        # Hit a FOUR (4 runs) -> Score 10/0 >= 7 target -> Team A WINS SUPER OVER!
        self.page.evaluate("recordBall(4)")

        # Match result modal should open declaring Super Over victory
        self.page.wait_for_selector("#match-result-modal", state="visible")
        winner_desc = self.page.locator("#winner-modal-desc").inner_text()
        self.assertIn("won the Super Over by 2 wicket(s)", winner_desc)

        # Navigate to Scorecard (S13)
        self.page.evaluate("navigate('S13')")
        self.page.wait_for_selector("#scorecard-super-over-wrap", state="visible")

        # Scorecard should show Super Over breakdown
        so_wrap_txt = self.page.locator("#scorecard-super-over-wrap").inner_text()
        self.assertIn("Official ICC Super Over Breakdown", so_wrap_txt)
        self.assertIn("tbl_MatchSuperOverBallByBall", so_wrap_txt)
        self.assertIn("won the Super Over", so_wrap_txt)

if __name__ == "__main__":
    unittest.main()
