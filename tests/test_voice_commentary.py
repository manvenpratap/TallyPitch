# tests/test_voice_commentary.py
# End-to-end and Validation Tests for Track 4: Real-time Audio Voice & Speech Commentary Synthesizer
# Covers S07 live speech synthesis HUD, S13 over audio recap, zone-aware delivery generation, and zero console errors.

import os
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestVoiceCommentary(unittest.TestCase):
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

    def test_generate_ball_commentary_unit(self):
        """Test natural language commentary generation with field zones, wickets, boundaries and extras"""
        result = self.page.evaluate("""() => {
            const inn = {
                batters: { p1: { name: "Rohit Sharma" }, p2: { name: "Virat Kohli" } },
                bowlers: { b1: { name: "Jasprit Bumrah" } }
            };

            const fourWithZone = generateBallCommentary({
                strikerId: 'p1',
                bowlerId: 'b1',
                runs: 4,
                isExtra: false,
                isWicket: false,
                wagonWheel: { zone_name: 'Extra Cover', wagon_part: '6' }
            }, inn);

            const sixWithZone = generateBallCommentary({
                strikerId: 'p2',
                bowlerId: 'b1',
                runs: 6,
                isExtra: false,
                isWicket: false,
                wagonWheel: { zone_name: 'Mid-Wicket', wagon_part: '3' }
            }, inn);

            const wicket = generateBallCommentary({
                strikerId: 'p1',
                bowlerId: 'b1',
                runs: 0,
                isExtra: false,
                isWicket: true
            }, inn);

            const wide = generateBallCommentary({
                strikerId: 'p1',
                bowlerId: 'b1',
                runs: 0,
                isExtra: true,
                extraType: 'wide',
                isWicket: false
            }, inn);

            const dot = generateBallCommentary({
                strikerId: 'p1',
                bowlerId: 'b1',
                runs: 0,
                isExtra: false,
                isWicket: false
            }, inn);

            return { fourWithZone, sixWithZone, wicket, wide, dot };
        }""")

        self.assertIn("FOUR! Beautifully timed by Rohit Sharma through Extra Cover", result["fourWithZone"])
        self.assertIn("SIX! Smashed high and handsome over Mid-Wicket by Virat Kohli", result["sixWithZone"])
        self.assertIn("OUT! Wicket falls! Rohit Sharma has to depart", result["wicket"])
        self.assertIn("Wide ball called against Jasprit Bumrah", result["wide"])
        self.assertIn("No run. Solid defensive stroke by Rohit Sharma", result["dot"])

    def test_voice_commentary_toggle_buttons(self):
        """Test HUD and S13 voice commentary toggle buttons update state and labels"""
        toggle_btn = self.page.locator("#btn-voice-commentary-toggle")
        self.assertTrue(toggle_btn.is_visible(timeout=5000), "#btn-voice-commentary-toggle must be visible")
        self.assertIn("OFF", toggle_btn.inner_text())

        # Click to turn ON
        toggle_btn.click()
        self.assertIn("ON", toggle_btn.inner_text())
        state_on = self.page.evaluate("() => state.audioCommentary.enabled")
        self.assertTrue(state_on)

        # Check S13 toggle button also reflects ON
        s13_btn = self.page.locator("#btn-voice-commentary-s13")
        self.assertIn("ON", s13_btn.inner_text())

        # Click to turn OFF
        toggle_btn.click()
        self.assertIn("OFF", toggle_btn.inner_text())
        state_off = self.page.evaluate("() => state.audioCommentary.enabled")
        self.assertFalse(state_off)

    def test_speech_synthesis_recording_and_over_recap(self):
        self.assertTrue(self.page.locator("#btn-voice-commentary-toggle").is_visible(timeout=5000))

        # Inject speech synthesis spy
        self.page.evaluate("""() => {
            window.__spokenPhrases = [];
            window.speechSynthesis.cancel = () => {};
            window.speechSynthesis.speak = (utterance) => {
                window.__spokenPhrases.push(utterance.text);
            };
            // Enable voice commentary
            state.audioCommentary.enabled = true;
            updateVoiceCommentaryUI();
        }""")

        # Record a boundary 4
        self.page.evaluate("() => recordBall(4)")

        # Verify speech synthesis captured the boundary commentary
        spoken = self.page.evaluate("() => window.__spokenPhrases")
        self.assertTrue(len(spoken) > 0, "Speech synthesis should have spoken commentary")
        self.assertTrue(any("FOUR!" in phrase for phrase in spoken), f"Expected boundary text in {spoken}")

        # Trigger Over Audio Recap
        self.page.evaluate("() => speakOverAudioRecap()")
        spoken_after_recap = self.page.evaluate("() => window.__spokenPhrases")
        self.assertTrue(any("recap" in phrase.lower() for phrase in spoken_after_recap), f"Expected recap in {spoken_after_recap}")

if __name__ == "__main__":
    unittest.main()
