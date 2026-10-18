# tests/test_realtime_bridge.py
# End-to-end and Protocol Compatibility Tests for CricHeroes MQTT Bridge and OBS Streaming Overlay (Track 1)

import os
import subprocess
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestRealtimeBridge(unittest.TestCase):
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

    def tearDown(self):
        self.page.close()
        critical_errors = [e for e in self.console_errors if any(kw in e for kw in ["TypeError", "ReferenceError", "SyntaxError", "is not a function"])]
        self.assertEqual(critical_errors, [], f"Critical console errors observed: {critical_errors}")

    def test_node_mqtt_protocol_and_packet_encoding(self):
        """Verify Node.js realtime module handles MQTT 3.1.1 packets and CricHeroes topic matching"""
        script = """
        const r = require('./server/realtime.js');
        
        // 1. Topic wildcard matches
        const t1 = r.matchesTopic('cricheroes/matches/+/score', 'cricheroes/matches/1078193/score');
        const t2 = r.matchesTopic('cricheroes/matches/1078193/#', 'cricheroes/matches/1078193/ball');
        const t3 = r.matchesTopic('cricheroes/#', 'cricheroes/matches/1078193/overlay');
        const t4 = r.matchesTopic('cricheroes/matches/1078193/score', 'cricheroes/matches/999/score');
        if (!t1 || !t2 || !t3 || t4) process.exit(1);

        // 2. MQTT PUBLISH frame encoding & decoding
        const pubBuf = r.encodeMqttPublish('cricheroes/matches/1078193/score', { runs: 114, wickets: 3 });
        const decodedPub = r.decodeMqttPacket(pubBuf);
        if (decodedPub.type !== 'PUBLISH' || decodedPub.topic !== 'cricheroes/matches/1078193/score') process.exit(2);
        if (decodedPub.payload.runs !== 114) process.exit(3);

        // 3. MQTT PINGREQ frame decoding
        const pingBuf = Buffer.from([0xc0, 0x00]);
        const decodedPing = r.decodeMqttPacket(pingBuf);
        if (decodedPing.type !== 'PINGREQ') process.exit(4);

        console.log('MQTT_PROTOCOL_OK');
        """
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True)
        self.assertIn("MQTT_PROTOCOL_OK", result.stdout)

    def test_obs_overlay_rendering_and_zero_errors(self):
        """Verify standalone OBS Browser Source rendering (?overlay=true) with transparent background and zero errors"""
        page = self.page
        overlay_url = APP_URL + "?overlay=true"
        page.goto(overlay_url, wait_until="domcontentloaded")

        # 1. Assert body has obs-overlay-mode class
        body_class = page.get_attribute("body", "class") or ""
        self.assertIn("obs-overlay-mode", body_class)

        # 2. Assert lower-third scoreboard container is visible
        self.assertTrue(page.is_visible("#obs-overlay-container"))
        self.assertTrue(page.is_visible("#obs-lower-third"))

        # 3. Assert live elements exist
        self.assertTrue(page.is_visible("#obs-score-runs"))
        self.assertTrue(page.is_visible("#obs-score-wickets"))
        self.assertTrue(page.is_visible("#obs-overs"))
        self.assertTrue(page.is_visible("#obs-crr"))
        self.assertTrue(page.is_visible("#obs-striker-name"))
        self.assertTrue(page.is_visible("#obs-bowler-name"))
        self.assertTrue(page.is_visible("#obs-ticker-bar"))

        # 4. Assert app shell elements are hidden in overlay mode
        self.assertFalse(page.is_visible(".app-header"))
        self.assertFalse(page.is_visible(".app-nav-tabs"))
        self.assertFalse(page.is_visible(".app-footer"))

    def test_broadcast_stream_modal_in_scorer(self):
        """Verify live scoring console (S07) modal opens and exhibits complete broadcast telemetry & tooltips"""
        page = self.page
        page.goto(APP_URL, wait_until="domcontentloaded")
        page.click("#tab-S07")

        # 1. Verify OBS Stream buttons exist and have accessible tooltips
        stream_btn = page.locator("#btn-stream-overlay")
        self.assertTrue(stream_btn.is_visible())
        self.assertEqual(stream_btn.get_attribute("data-tooltip"), "Live streaming OBS overlay & CricHeroes MQTT bridge")

        keypad_stream_btn = page.locator("#btn-stream-overlay-keypad")
        self.assertTrue(keypad_stream_btn.is_visible())
        self.assertEqual(keypad_stream_btn.get_attribute("data-tooltip"), "Live streaming OBS overlay & CricHeroes MQTT bridge")

        # 2. Open Stream Overlay modal
        stream_btn.click()
        self.assertTrue(page.is_visible("#broadcast-modal"))
        self.assertIn("open", page.get_attribute("#broadcast-modal", "class") or "")

        # 3. Check OBS URL input contains overlay query param
        obs_url = page.input_value("#obs-url-input")
        self.assertIn("overlay=true", obs_url)

        # 4. Check CricHeroes MQTT topics are displayed
        self.assertIn("cricheroes/matches/", page.text_content("#mqtt-topic-score"))
        self.assertIn("cricheroes/matches/", page.text_content("#mqtt-topic-ball"))
        self.assertIn("cricheroes/matches/", page.text_content("#mqtt-topic-overlay"))

        # 5. Check test overlay trigger buttons
        page.click("button:has-text('⚡ Test 4')")
        self.assertTrue(page.is_visible("#app-toast"))
        self.assertIn("Test FOUR", page.text_content("#app-toast"))

        # 6. Close modal
        page.click("#broadcast-modal button:has-text('Done')")
        self.assertNotIn("open", page.get_attribute("#broadcast-modal", "class") or "")

    def test_cricheroes_ball_payload_schema_and_overlay_sync(self):
        """Verify delivery events format valid CricHeroes ball payload schema with polar coordinates"""
        page = self.page
        page.goto(APP_URL, wait_until="domcontentloaded")
        page.click("#tab-S07")

        # Score a boundary 4
        page.click("button:has-text('4 FOUR!')")
        self.assertEqual(page.text_content("#hero-score"), "4/0")

        # Evaluate snapshot schema generated in browser
        snapshot = page.evaluate("getLiveMatchSnapshot()")
        self.assertIsNotNone(snapshot)
        self.assertIn("ball", snapshot)
        self.assertIn("score", snapshot)
        self.assertIn("overlay", snapshot)

        # Verify CricHeroes forensic schema parity
        ball = snapshot["ball"]
        self.assertEqual(ball["runs_scored"], 4)
        self.assertTrue(ball["is_boundary"])
        self.assertEqual(ball["boundary_type"], 4)
        self.assertIn("wagon_wheel", ball)
        self.assertIn("zone", ball["wagon_wheel"])
        self.assertIn("angle_degrees", ball["wagon_wheel"])
        self.assertIn("distance_pct", ball["wagon_wheel"])

        score = snapshot["score"]
        self.assertEqual(score["total_runs"], 4)
        self.assertEqual(score["wickets"], 0)

        overlay = snapshot["overlay"]
        self.assertEqual(overlay["runs"], 4)
        self.assertTrue(len(overlay["chips"]) > 0)
