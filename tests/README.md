# Test Suite: TallyPitch

Automated regression and end-to-end testing infrastructure powered by Playwright and Pytest.

## Test Inventory

| Module | Flow / Scope | Scenarios Covered |
| :--- | :--- | :--- |
| `test_cricket_engine.py` | Core Match & Scoring Flows | • F01: Match setup, toss, and openers<br>• F02/F03: Ball scoring, boundaries, extras, and strike rotation<br>• F04: Wicket dismissal & incoming batter<br>• F05: Over completion & bowler rotation<br>• Atomic 0ms rollback verification |

## Running Tests

Execute tests via the Universal Pipeline:

```bash
# Token-efficient summary (recommended for agents & CI)
./pipeline.sh test --summary

# Fast smoke tests only
./pipeline.sh test --smoke

# Full verbose run
pytest -v tests/test_cricket_engine.py
```

## Test Harness Helpers
- `conftest.py`: Playwright browser session fixtures and local screenshot capturing.
- `helpers.py`: Bounding-box collision detection, viewport overflow checking, and zero console error assertion.
