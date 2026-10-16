# Contributing to TallyPitch 🏏

Thank you for contributing to TallyPitch! We are building an ad-free, high-integrity cricket scoring and tournament management platform for the grassroots community.

---

## 1. Development Principles

1. **Ad-Free Invariant**: The live scoring keypad must never be obstructed by advertisements, interstitials, or video popups.
2. **0ms Rollback**: Scoring error correction must remain instant and atomic.
3. **Distribution Parity**: For single-page web features, `dist/index.html` must remain synchronized with `index.html`.
4. **Minimal Tokens Protocol**: Run `./pipeline.sh test --summary` for token-efficient test feedback.

---

## 2. Git & Branching Workflow

### Branch Naming
- Features: `feat/<feature-name>`
- Bugfixes: `fix/<issue-name>`
- Documentation: `docs/<topic>`
- Maintenance: `chore/<description>`

### Commit Messages
We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
- `feat(scoring): add DLS calculation target display`
- `fix(toss): correct non-striker assignment after toss`
- `docs(readme): add OBS setup guide`
- `test(e2e): add boundary count tie-breaker scenario`
- `chore(pipeline): update CI test matrix`

### Optional: Local Git Hooks
Enable pre-commit verification checks:
```bash
git config core.hooksPath .githooks
```

---

## 3. Local Verification

Before creating a Pull Request, verify your changes locally:

```bash
# 1. Run doctor check
./pipeline.sh doctor

# 2. Run regression suite
./pipeline.sh test --summary

# 3. Synchronize distribution artifacts if index.html changed
./pipeline.sh package
```

---

## 4. Submitting a Pull Request

1. Ensure your branch is rebased on `main`.
2. Fill out the PR template with clear verification notes.
3. Ensure the automated GitHub Actions CI workflow passes.
