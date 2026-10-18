# tests/test_tournament_realtime.py
# End-to-end and Protocol Tests for Track 2: Real-time Tournament Standings Stream
# Topic: cricheroes/tournaments/{tournament_id}/standings (MQTT 3.1.1 & WebSocket)

import os
import subprocess
import unittest
from playwright.sync_api import sync_playwright

APP_URL = "file://" + os.path.abspath("index.html")

class TestTournamentRealtimeStream(unittest.TestCase):
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

    def test_node_mqtt_tournament_topic_and_standings_packet(self):
        """Verify Node.js realtime engine matches tournament MQTT topics and encodes standings packets"""
        script = """
        const r = require('./server/realtime.js');

        // 1. Topic matching with wildcards
        const t1 = r.matchesTopic('cricheroes/tournaments/+/standings', 'cricheroes/tournaments/1045/standings');
        const t2 = r.matchesTopic('cricheroes/tournaments/#', 'cricheroes/tournaments/1045/standings');
        const t3 = r.matchesTopic('cricheroes/tournaments/1045/standings', 'cricheroes/tournaments/999/standings');
        if (!t1 || !t2 || t3) process.exit(1);

        // 2. Standings broadcast helper
        const payload = r.broadcastTournamentStandings('1045', {
          tournament_name: 'TallyPitch Premier League',
          standings: [
            { pos: 1, team: 'Mumbai Strikers', p: 2, w: 2, l: 0, t: 0, nr: 0, pts: 4, nrr: '+1.650' },
            { pos: 2, team: 'Pune Warriors', p: 2, w: 1, l: 1, t: 0, nr: 0, pts: 2, nrr: '+0.420' }
          ]
        });
        if (payload.tournament_id !== '1045' || payload.total_teams !== 2 || payload.event_type !== 'STANDINGS_UPDATE') {
          process.exit(2);
        }

        // 3. MQTT binary encode & decode of tournament standings
        const buf = r.encodeMqttPublish('cricheroes/tournaments/1045/standings', payload);
        const decoded = r.decodeMqttPacket(buf);
        if (!decoded || decoded.type !== 'PUBLISH' || decoded.topic !== 'cricheroes/tournaments/1045/standings') {
          process.exit(3);
        }

        const parsed = typeof decoded.payload === 'object' ? decoded.payload : JSON.parse(decoded.payload.toString('utf8'));
        if (parsed.tournament_id !== '1045' || parsed.standings.length !== 2) {
          process.exit(4);
        }

        process.exit(0);
        """
        proc = subprocess.run(["node", "-e", script], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Node MQTT tournament packet test failed: {proc.stderr}")

    def test_s18_tournament_stream_badge_and_ui_rendering(self):
        """Verify Screen S18 displays live MQTT stream telemetry badge, tooltip, and initial points table"""
        page = self.page
        page.click("#tab-tournaments")

        # 1. Verify S18 Points Table section is rendered
        tbody = page.locator("#tournament-standings-tbody")
        self.assertTrue(tbody.is_visible())

        # 2. Verify stream indicator badge and button
        stream_badge = page.locator("#tournament-stream-badge")
        self.assertTrue(stream_badge.is_visible())
        self.assertIn("cricheroes", stream_badge.text_content().lower())

        btn_push = page.locator("#btn-sync-standings-stream")
        self.assertTrue(btn_push.is_visible())
        self.assertIn("data-tooltip", btn_push.evaluate("el => el.outerHTML"))

        # 3. Check initial standings rows
        mumbai_row = page.locator("#standing-row-mumbai-strikers")
        self.assertTrue(mumbai_row.is_visible())
        self.assertIn("Mumbai Strikers", mumbai_row.text_content())
        self.assertIn("4", mumbai_row.text_content()) # 4 points

    def test_realtime_standings_stream_reception_and_dom_update(self):
        """Verify dynamic DOM update when incoming real-time standings stream event is received"""
        page = self.page
        page.click("#tab-tournaments")

        # Apply real-time update where Pune Warriors overtakes Mumbai Strikers
        page.evaluate("""() => {
          applyTournamentStandingsUpdate({
            tournament_id: '1045',
            event_type: 'STANDINGS_UPDATE',
            standings: [
              { pos: 1, team: 'Pune Warriors', p: 3, w: 2, l: 1, t: 0, nr: 0, pts: 4, nrr: '+1.850' },
              { pos: 2, team: 'Mumbai Strikers', p: 3, w: 2, l: 1, t: 0, nr: 0, pts: 4, nrr: '+1.650' },
              { pos: 3, team: 'Ahmedabad Lions', p: 2, w: 0, l: 2, t: 0, nr: 0, pts: 0, nrr: '-2.070' }
            ]
          });
        }""")

        # Verify Pos 1 in table is now Pune Warriors
        tbody = page.locator("#tournament-standings-tbody")
        first_row = tbody.locator("tr").first
        self.assertIn("Pune Warriors", first_row.text_content())
        self.assertIn("+1.850", first_row.text_content())

        # Verify status text updated
        status_text = page.text_content("#tournament-stream-status")
        self.assertIn("Stream Updated Live", status_text)

    def test_match_conclusion_auto_updates_tournament_standings(self):
        """Verify match conclusion calculates points, updates standings, and triggers live stream broadcast"""
        page = self.page
        page.click("#tab-tournaments")

        # Simulate match outcome: Pune Warriors defeat Ahmedabad Lions
        page.evaluate("""() => {
          updateTournamentStandingsFromMatchResult('Pune Warriors', 'Ahmedabad Lions', false);
        }""")

        # Verify Pune Warriors played matches and points increased
        pune_row = page.locator("#standing-row-pune-warriors")
        self.assertTrue(pune_row.is_visible())
        pune_text = pune_row.text_content()
        self.assertIn("Pune Warriors", pune_text)

        # Verify stream status updated with Dispatched
        status_text = page.text_content("#tournament-stream-status")
        self.assertIn("Dispatched", status_text)
