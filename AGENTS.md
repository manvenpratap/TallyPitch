# Project Agent Governance & Pipeline Rules

## 1. Mandatory Context Reading
- **ALWAYS** read `PROJECT_CONTEXT.md` at the start of every session before modifying code or proposing plans.
- **ALWAYS** check `PRODUCT.md` and `DESIGN.md` for architectural constraints and design token consistency.

## 2. Minimal Tokens Protocol (MANDATORY)
- Do NOT run unbuffered commands that dump thousands of lines of compiler/test output into context.
- Use `./pipeline.sh test --summary` for all test runs.
- Review only compact failure reports (failing test names and line numbers).

## 3. Persistent Context Maintenance
- After every completed feature or meaningful change, update `PROJECT_CONTEXT.md`:
  - **Current Status**: mark completed phase and timestamp.
  - **Implemented Features**: add concise bullet points.
  - **Roadmap Progress**: check off completed milestones.
- Keep `tests/README.md` coverage map in sync when adding new test modules.

## 4. Regression Test Suite Rules
- **Never delete tests**: If a feature is modified or refactored, update the existing test rather than deleting it.
- **Write a test for every feature**: Add `test_NN_<feature_name>.py` sequentially.
- **Zero console errors**: Always assert `assert_no_critical_errors(page)`.
- **Local resources only**: All Playwright screenshots and test caches stay in `tests/screenshots/` on local disk.

## 5. UI Tooltips & Accessibility Invariants
- Every icon button, metric card, and complex action must include contextual help.
- Use the accessible `data-tooltip="..."` attribute.
- Ensure tooltips dismiss on `Escape` and outside click.

## 6. Packaging & Release Ship Rule
- Never push raw source code without verifying distribution artifacts.
- For single-file web apps: ensure `dist/index.html` is byte-for-byte identical to root app.
- For Java/Node/Rust apps: run `./pipeline.sh package` before committing.
- Use `./pipeline.sh ship "<conventional commit message>"` to automate the complete verified release.
