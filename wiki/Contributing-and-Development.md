# Developer Guide & Universal Pipeline

Guidelines for developing, testing, and maintaining TallyPitch using the local-first Universal Pipeline.

---

## 1. Quick Start for Developers

```bash
# Clone the repository
git clone https://github.com/manvenpratap/TallyPitch.git
cd TallyPitch

# Run local web server
python3 -m http.server 8080
# Visit http://localhost:8080/index.html
```

---

## 2. The Universal Pipeline (`./pipeline.sh`)

TallyPitch integrates the **Universal Pipeline** for self-analyzing, self-healing, and token-efficient test execution:

```bash
# 1. Run diagnostic invariant checks
./pipeline.sh doctor

# 2. Run automated regression test suite with token-efficient summary
./pipeline.sh test --summary

# 3. Run fast critical smoke tests
./pipeline.sh test --smoke

# 4. Synchronize production distribution build
./pipeline.sh package

# 5. Full guarded release gate (test -> package -> doc -> git commit/push)
./pipeline.sh ship "feat: description of change"
```

---

## 3. Playwright E2E Test Suite (`tests/`)

Tests are located in `tests/test_cricket_engine.py` and run against the live browser DOM:
- **Test Invariants**: Every test verifies `assert_no_critical_errors(page)`.
- **Flow Coverage**: Match setup (S03), live scoring (S07), ICC scorecard generation (S13), extras, strike rotation, wicket dismissals, and atomic rollback verification.
- **Local Screenshots**: Visual captures are preserved locally in `tests/screenshots/` and never leaked into git history.

---

## 4. Single-File Distribution Parity

For zero-runtime frontend deployments:
- `index.html` is the primary application source.
- `dist/index.html` must remain byte-for-byte identical to `index.html`.
- Run `./pipeline.sh package` to synchronize.
