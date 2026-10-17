# tests/test_community_and_badges.py
# End-to-end tests for Track 3: Milestone Badges (S21) & Community Matchmaking Board (S23)

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestCommunityAndBadges(unittest.TestCase):
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
        # Assert no uncaught JS runtime exceptions
        critical_errors = [e for e in self.console_errors if any(kw in e for kw in ["TypeError", "ReferenceError", "SyntaxError", "is not a function"])]
        self.assertEqual(critical_errors, [], f"Critical console errors observed: {critical_errors}")

    def test_milestone_badges_rendering_and_player_switching(self):
        """Verify S21 Milestone Badges render cards with proper unlocked/locked states and tooltips"""
        page = self.page
        page.click("#tab-teams-profiles")

        # 1. Verify badges container is visible
        self.assertTrue(page.is_visible("#profile-badges-wrap"))
        
        # 2. Verify all 8 milestone badges are rendered
        badges = page.query_selector_all("#profile-badges-wrap .badge-card")
        self.assertEqual(len(badges), 8)

        # 3. Verify badge count pill has text like 'X / 8 Unlocked'
        pill_text = page.text_content("#player-badge-count-pill")
        self.assertIn("/ 8 Unlocked", pill_text)

        # 4. Verify data-tooltip attributes exist on badges
        for b in badges:
            tooltip = b.get_attribute("data-tooltip")
            self.assertIsNotNone(tooltip)
            self.assertTrue(len(tooltip) > 0)

        # 5. Switch player to Bowler (e.g., Jasprit B) and verify badge updates
        page.select_option("#profile-player-select", "A10")
        updated_pill = page.text_content("#player-badge-count-pill")
        self.assertIn("/ 8 Unlocked", updated_pill)

    def test_community_board_rendering_and_category_filters(self):
        """Verify S23 Community Board renders listings, counts, and filters correctly"""
        page = self.page
        page.click("#tab-community")

        # 1. Verify listings container and active cards
        self.assertTrue(page.is_visible("#community-listings-container"))
        cards = page.query_selector_all("#community-listings-container .community-card")
        self.assertGreaterEqual(len(cards), 5)

        # 2. Verify count badge on 'All' tab matches card count
        all_count = page.text_content("#comm-count-all")
        self.assertEqual(str(len(cards)), all_count)

        # 3. Filter by Players seeking teams ('team')
        page.click("#filter-comm-team")
        team_cards = page.query_selector_all("#community-listings-container .community-card")
        team_count = int(page.text_content("#comm-count-team"))
        self.assertEqual(len(team_cards), team_count)

        # 4. Filter by Umpires ('umpire')
        page.click("#filter-comm-umpire")
        umpire_cards = page.query_selector_all("#community-listings-container .community-card")
        umpire_count = int(page.text_content("#comm-count-umpire"))
        self.assertEqual(len(umpire_cards), umpire_count)

        # 5. Return to all
        page.click("#filter-comm-all")
        self.assertEqual(len(page.query_selector_all("#community-listings-container .community-card")), len(cards))

    def test_post_new_classified_listing_modal_submission(self):
        """Verify posting a new classified listing prepends card and updates counts dynamically"""
        page = self.page
        page.click("#tab-community")

        initial_count = len(page.query_selector_all("#community-listings-container .community-card"))

        # 1. Open Post Listing Modal
        page.click("#btn-post-listing")
        self.assertTrue(page.is_visible("#post-listing-modal"))
        self.assertIn("open", page.get_attribute("#post-listing-modal", "class"))

        # 2. Fill form fields
        page.select_option("#comm-cat-select", "player")
        page.fill("#comm-title-input", "Top Order Batter & Off-Spinner Needed")
        page.fill("#comm-team-input", "Dadar Strikers CC")
        page.fill("#comm-location-input", "Shivaji Park Ground 4, Mumbai")
        page.fill("#comm-date-input", "This Saturday 7:30 AM")
        page.fill("#comm-format-input", "25 Overs Red Leather Ball")
        page.fill("#comm-contact-name-input", "Manven (Manager)")
        page.fill("#comm-contact-phone-input", "+91 99887 76655")
        page.fill("#comm-desc-input", "Looking for experienced batsman. Match fee & refreshments provided.")

        # 3. Submit listing
        page.click("#btn-submit-listing")

        # 4. Modal closes and listing count increments
        self.assertNotIn("open", page.get_attribute("#post-listing-modal", "class"))
        new_cards = page.query_selector_all("#community-listings-container .community-card")
        self.assertEqual(len(new_cards), initial_count + 1)

        # 5. First card contains new headline
        first_card_title = page.text_content("#community-listings-container .community-card:first-child .community-card-title")
        self.assertIn("Top Order Batter", first_card_title)

        # 6. Test 'Connect' button triggers action toast
        page.click("#community-listings-container .community-card:first-child button:has-text('Connect')")
        toast_text = page.text_content("#app-toast")
        self.assertIn("Contact", toast_text)

if __name__ == "__main__":
    unittest.main()
