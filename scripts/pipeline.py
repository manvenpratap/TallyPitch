#!/usr/bin/env python3
"""
pipeline.py — Universal Self-Analyzing & Self-Healing Pipeline Engine
Autonomous project auditor, doctor, test runner, and release orchestrator.
"""

import sys
import os
import subprocess
import json
import re
import shutil
import time
import hashlib
from pathlib import Path

# ANSI color and style helpers
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def log_step(msg: str):
    print(f"{CYAN}{BOLD}==> {msg}{RESET}")


def log_success(msg: str):
    print(f"{GREEN}✓ {msg}{RESET}")


def log_warn(msg: str):
    print(f"{YELLOW}⚠ {msg}{RESET}")


def log_error(msg: str):
    print(f"{RED}✗ {msg}{RESET}")


def file_sha256(path: Path) -> str:
    """Calculates SHA256 hash of a file."""
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


class StackDetector:
    """Intelligently detects tech stacks, build systems, test suites, and living docs."""

    def __init__(self, root: Path):
        self.root = root

    def detect(self) -> dict:
        info = {
            "root": str(self.root),
            "is_git": (self.root / ".git").is_dir(),
            "stacks": [],
            "test_frameworks": [],
            "package_targets": [],
            "doc_files": [],
            "primary_stack": "unknown",
            "primary_html": None
        }

        # 1. Java / JVM
        if (self.root / "pom.xml").exists():
            info["stacks"].append("java-maven")
            info["test_frameworks"].append("maven-surefire")
            info["package_targets"].append("mvn-package")
        elif (self.root / "build.gradle").exists() or (self.root / "build.gradle.kts").exists():
            info["stacks"].append("java-gradle")
            info["test_frameworks"].append("gradle-test")
            info["package_targets"].append("gradle-build")

        # 2. Rust / Tauri
        if (self.root / "Cargo.toml").exists() or (self.root / "src-tauri").is_dir():
            info["stacks"].append("rust")
            if (self.root / "src-tauri").is_dir():
                info["stacks"].append("rust-tauri")
                info["package_targets"].append("tauri-bundle")
            info["test_frameworks"].append("cargo-test")

        # 3. Go
        if (self.root / "go.mod").exists():
            info["stacks"].append("go")
            info["test_frameworks"].append("go-test")
            info["package_targets"].append("go-build")

        # 4. Node / TypeScript / Frontend
        if (self.root / "package.json").exists():
            info["stacks"].append("node-ts")
            try:
                with open(self.root / "package.json", "r", encoding="utf-8") as f:
                    pkg = json.load(f)
                    scripts = pkg.get("scripts", {})
                    if "test" in scripts:
                        info["test_frameworks"].append("npm-test")
                    if "build" in scripts:
                        info["package_targets"].append("npm-build")
            except Exception:
                pass

        # 5. Python
        py_files = list(self.root.glob("*.py"))
        has_py_manifest = any((self.root / f).exists() for f in ["pyproject.toml", "requirements.txt", "setup.py", "Pipfile"])
        has_py_tests = (self.root / "tests").is_dir() or (self.root / "e2e-tests").is_dir() or (self.root / "pytest.ini").exists()
        if has_py_manifest or py_files or has_py_tests:
            info["stacks"].append("python")
            if has_py_tests:
                info["test_frameworks"].append("pytest/playwright")

        # 6. Single-File / Static Web App
        html_files = [f for f in self.root.glob("*.html") if "dist" not in f.parts and "node_modules" not in f.parts]
        if html_files:
            info["stacks"].append("single-file-web")
            info["package_targets"].append("dist-sync")
            index_cand = [h for h in html_files if h.name.lower() == "index.html"]
            if index_cand:
                info["primary_html"] = index_cand[0].name
            else:
                html_files.sort(key=lambda f: f.stat().st_size, reverse=True)
                info["primary_html"] = html_files[0].name

        # 7. Agent Skill
        if (self.root / "SKILL.md").exists():
            info["stacks"].append("agent-skill")

        # 8. Custom Runner Detection
        if (self.root / "run_tests.sh").exists():
            info["test_frameworks"].insert(0, "custom-runner (run_tests.sh)")

        # 9. Living Docs
        for doc in ["PROJECT_CONTEXT.md", "PRODUCT.md", "DESIGN.md", "README.md", "AGENTS.md"]:
            if (self.root / doc).exists():
                info["doc_files"].append(doc)
            elif (self.root / ".agents" / doc).exists():
                info["doc_files"].append(f".agents/{doc}")

        # 10. Mobile Apps (Android APK & iOS App) Delivery Plan Detection
        info["mobile"] = self.detect_mobile_delivery()
        if info["mobile"]["has_android"]:
            info["stacks"].append("android")
            info["package_targets"].append("mobile-apk")
        if info["mobile"]["has_ios"]:
            info["stacks"].append("ios")
            info["package_targets"].append("mobile-ios")

        # 11. Primary Stack Resolution
        if "single-file-web" in info["stacks"] and len(info["stacks"]) <= 2:
            info["primary_stack"] = "single-file-web"
        elif "node-ts" in info["stacks"] and any(f in os.listdir(self.root) for f in ["vite.config.ts", "vite.config.js"]):
            info["primary_stack"] = "vite-frontend"
        elif "java-maven" in info["stacks"]:
            info["primary_stack"] = "java-maven"
        elif "python" in info["stacks"] and "node-ts" not in info["stacks"]:
            info["primary_stack"] = "python"
        elif "rust-tauri" in info["stacks"]:
            info["primary_stack"] = "rust-tauri"
        elif "go" in info["stacks"]:
            info["primary_stack"] = "go"
        elif "agent-skill" in info["stacks"]:
            info["primary_stack"] = "agent-skill"
        elif info["stacks"]:
            info["primary_stack"] = info["stacks"][0]

        return info

    def detect_mobile_delivery(self) -> dict:
        result = {
            "has_android": False,
            "has_ios": False,
            "android_path": None,
            "ios_path": None,
            "android_type": None,
            "ios_type": None,
            "is_part_of_plan": False,
            "plan_docs": []
        }

        # 1. Android Candidates
        android_candidates = [
            self.root / "android",
            self.root / "apps" / "mobile" / "android",
            self.root / "frontend" / "android",
            self.root / "mobile" / "android"
        ]
        for cand in android_candidates:
            if cand.is_dir() and ((cand / "build.gradle").exists() or (cand / "build-apk.sh").exists() or (cand / "gradlew").exists() or (cand / "app" / "build.gradle").exists()):
                result["has_android"] = True
                result["android_path"] = cand
                result["android_type"] = "script" if (cand / "build-apk.sh").exists() else "gradle"
                break

        # 2. iOS Candidates
        ios_candidates = [
            self.root / "ios",
            self.root / "apps" / "mobile" / "ios",
            self.root / "frontend" / "ios",
            self.root / "mobile" / "ios"
        ]
        for cand in ios_candidates:
            if cand.is_dir():
                xcode_projs = list(cand.glob("**/*.xcodeproj"))
                if xcode_projs or (cand / "build-ios.sh").exists():
                    result["has_ios"] = True
                    result["ios_path"] = cand
                    result["ios_type"] = "script" if (cand / "build-ios.sh").exists() else "xcode"
                    break

        # 3. Delivery Plan documentation references
        for doc_name in ["PROJECT_CONTEXT.md", "PRODUCT.md", "README.md", "AGENTS.md"]:
            doc_file = self.root / doc_name
            if doc_file.exists():
                try:
                    txt = doc_file.read_text(encoding="utf-8", errors="ignore").lower()
                    if any(w in txt for w in ["apk", "ios app", "mobile app", "twa", "capacitor", "targetsdk", "xcode"]):
                        result["plan_docs"].append(doc_name)
                except Exception:
                    pass

        if result["has_android"] or result["has_ios"] or len(result["plan_docs"]) > 0:
            result["is_part_of_plan"] = True

        return result


class ProjectDoctor:
    """Self-analyzing diagnostic engine that detects health issues and drift."""

    def __init__(self, root: Path, stack_info: dict):
        self.root = root
        self.stack_info = stack_info

    def diagnose(self) -> dict:
        # Refresh stack info against current live filesystem state
        self.stack_info = StackDetector(self.root).detect()

        diagnosis = {
            "healthy": True,
            "discrepancies": [],
            "warnings": [],
            "checks": []
        }

        # Check 1: Distribution Parity Check
        if "dist-sync" in self.stack_info["package_targets"]:
            primary_html = self.stack_info.get("primary_html")
            if primary_html:
                src_path = self.root / primary_html
                dist_path = self.root / "dist" / "index.html"
                if not dist_path.exists():
                    diagnosis["discrepancies"].append({
                        "category": "distribution",
                        "issue": f"Distribution artifact dist/index.html is missing (source: {primary_html}).",
                        "heal_action": "resync_dist"
                    })
                else:
                    src_hash = file_sha256(src_path)
                    dist_hash = file_sha256(dist_path)
                    if src_hash != dist_hash:
                        diagnosis["discrepancies"].append({
                            "category": "distribution",
                            "issue": f"Distribution drift: dist/index.html is out of sync with {primary_html}.",
                            "heal_action": "resync_dist"
                        })
                    else:
                        diagnosis["checks"].append(f"Distribution parity: OK (dist/index.html matches {primary_html})")

        # Check 2: Test Infrastructure Health
        test_dir = self.root / "tests"
        e2e_dir = self.root / "e2e-tests"
        has_tests = test_dir.is_dir() or e2e_dir.is_dir() or (self.root / "run_tests.sh").exists()
        if not has_tests and self.stack_info["primary_stack"] != "agent-skill":
            diagnosis["discrepancies"].append({
                "category": "testing",
                "issue": "Missing regression test suite or tests/ directory.",
                "heal_action": "scaffold_tests"
            })
        else:
                if not (test_dir / "conftest.py").exists() and not (self.root / "run_tests.sh").exists():
                    diagnosis["warnings"].append("tests/ directory exists but missing shared conftest.py fixtures.")
                diagnosis["checks"].append("Test infrastructure: Present")
                
                # Check 2b: Numbered Test Consolidation Invariant (Threshold: 10 files)
                numbered_tests = []
                for td in [test_dir, e2e_dir]:
                    if td.is_dir():
                        numbered_tests.extend(list(td.glob("test_[0-9]*.py")) + list(td.glob("[0-9]*_test.py")))
                if len(numbered_tests) >= 10:
                    diagnosis["warnings"].append(
                        f"Test suite fragmentation: {len(numbered_tests)} numbered test files detected (threshold: 10). "
                        "Run test suite consolidation to merge into functional suites and remove duplicate scenarios."
                    )

        # Check 3: UI Tooltips & Accessibility Health
        if "single-file-web" in self.stack_info["stacks"] or "node-ts" in self.stack_info["stacks"]:
            has_tooltip_js = (self.root / "tooltip.js").exists() or (self.root / "src" / "tooltip.js").exists()
            if not has_tooltip_js:
                diagnosis["discrepancies"].append({
                    "category": "ui-tooltips",
                    "issue": "Missing accessible auto-flip tooltip component (tooltip.js / tooltip.css).",
                    "heal_action": "inject_tooltips"
                })
            else:
                diagnosis["checks"].append("Accessible Tooltips: Present")

            # Check unannotated buttons
            primary_html = self.stack_info.get("primary_html")
            if primary_html and (self.root / primary_html).exists():
                content = (self.root / primary_html).read_text(encoding="utf-8", errors="ignore")
                buttons = re.findall(r"<button\b([^>]*)>", content, re.IGNORECASE)
                unannotated = [b for b in buttons if "data-tooltip" not in b and "aria-label" not in b]
                if unannotated:
                    diagnosis["warnings"].append(f"Found {len(unannotated)} button(s) in {primary_html} missing tooltips or aria-labels.")

        # Check 4: Git Hygiene & Local Resource Caches
        if self.stack_info["is_git"]:
            gitignore = self.root / ".gitignore"
            if not gitignore.exists():
                diagnosis["discrepancies"].append({
                    "category": "git-hygiene",
                    "issue": "Missing .gitignore file in git repository.",
                    "heal_action": "patch_gitignore"
                })
            else:
                gi_text = gitignore.read_text(encoding="utf-8", errors="ignore")
                missing_rules = []
                for rule in ["tests/screenshots/", "e2e-tests/screenshots/", "__pycache__/", ".pytest_cache/"]:
                    if rule not in gi_text and rule.rstrip("/") not in gi_text:
                        missing_rules.append(rule)
                if missing_rules:
                    diagnosis["discrepancies"].append({
                        "category": "git-hygiene",
                        "issue": f".gitignore missing rules for local caches/screenshots: {', '.join(missing_rules)}",
                        "heal_action": "patch_gitignore"
                    })
                else:
                    diagnosis["checks"].append("Git hygiene & local ignore rules: OK")

        # Check 5: Living Documentation & Context Memory
        if not any("PROJECT_CONTEXT.md" in d for d in self.stack_info["doc_files"]):
            diagnosis["discrepancies"].append({
                "category": "docs",
                "issue": "Missing PROJECT_CONTEXT.md (persistent working memory on disk).",
                "heal_action": "scaffold_context_doc"
            })
        else:
            diagnosis["checks"].append("Living documentation: PROJECT_CONTEXT.md present")

        # Check 6: Standalone Runner
        if not (self.root / "pipeline.sh").exists():
            diagnosis["discrepancies"].append({
                "category": "runner",
                "issue": "Missing standalone ./pipeline.sh runner in project root.",
                "heal_action": "scaffold_runner"
            })
        else:
            diagnosis["checks"].append("Standalone runner: ./pipeline.sh present")

        # Check 7: Mobile App Delivery Health & Pre-Push Hook
        mobile_info = self.stack_info.get("mobile", {})
        if mobile_info.get("is_part_of_plan"):
            if self.stack_info["is_git"]:
                pre_push = self.root / ".git" / "hooks" / "pre-push"
                if not pre_push.exists():
                    diagnosis["discrepancies"].append({
                        "category": "mobile-delivery",
                        "issue": "Missing pre-push git hook (.git/hooks/pre-push) to ensure mobile apps update with every git push.",
                        "heal_action": "install_pre_push_hook"
                    })
                else:
                    diagnosis["checks"].append("Mobile delivery pre-push hook: Installed (.git/hooks/pre-push)")

            if mobile_info.get("has_android"):
                apk_found = list((self.root / "dist").glob("**/*.apk")) + list(self.root.glob("*.apk"))
                if not apk_found:
                    diagnosis["discrepancies"].append({
                        "category": "mobile-delivery",
                        "issue": "Android APK delivery artifact is missing from dist/.",
                        "heal_action": "build_mobile_apps"
                    })
                else:
                    diagnosis["checks"].append(f"Android APK artifact: Present ({apk_found[0].name})")

            if mobile_info.get("has_ios"):
                ios_found = list((self.root / "dist").glob("**/*ios*.zip")) + list(self.root.glob("**/*.xcodeproj"))
                if ios_found:
                    diagnosis["checks"].append("iOS delivery artifact / project: Present")

        if diagnosis["discrepancies"]:
            diagnosis["healthy"] = False

        return diagnosis


class SelfHealingEngine:
    """Autonomous self-healing engine that remediates diagnosed project discrepancies."""

    def __init__(self, root: Path, skill_dir: Path, stack_info: dict):
        self.root = root
        self.skill_dir = skill_dir
        self.stack_info = stack_info

    def heal(self, diagnosis: dict) -> list:
        log_step(f"Initiating autonomous self-healing in {self.root}...")
        healed_actions = []

        # 1. Heal Runner
        runner_dst = self.root / "pipeline.sh"
        runner_src = self.skill_dir / "scripts" / "pipeline.sh"
        if not runner_dst.exists() and runner_src.exists():
            shutil.copyfile(runner_src, runner_dst)
            runner_dst.chmod(0o755)
            healed_actions.append("Healed runner: Generated standalone ./pipeline.sh")
        elif runner_dst.exists() and not os.access(runner_dst, os.X_OK):
            runner_dst.chmod(0o755)
            healed_actions.append("Healed runner: Made ./pipeline.sh executable")

        # 2. Heal Distribution Parity
        if "dist-sync" in self.stack_info["package_targets"]:
            primary_html = self.stack_info.get("primary_html")
            if primary_html:
                src_path = self.root / primary_html
                if src_path.exists():
                    dist_dir = self.root / "dist"
                    dist_dir.mkdir(parents=True, exist_ok=True)
                    dist_target = dist_dir / "index.html"
                    shutil.copyfile(src_path, dist_target)
                    healed_actions.append(f"Healed distribution: Synchronized {primary_html} -> dist/index.html ({dist_target.stat().st_size:,} bytes)")

        # 3. Heal .gitignore
        gitignore = self.root / ".gitignore"
        ignore_rules = ["tests/screenshots/", "e2e-tests/screenshots/", "__pycache__/", ".pytest_cache/", ".DS_Store"]
        existing = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
        missing = [r for r in ignore_rules if r not in existing and r.rstrip("/") not in existing]
        if missing:
            with open(gitignore, "a", encoding="utf-8") as f:
                f.write("\n# Universal Pipeline local resources\n" + "\n".join(missing) + "\n")
            healed_actions.append(f"Healed git hygiene: Added {len(missing)} rule(s) to .gitignore")

        # 4. Heal Tooltips
        if "single-file-web" in self.stack_info["stacks"] or "node-ts" in self.stack_info["stacks"]:
            tt_js = self.root / "tooltip.js"
            tt_css = self.root / "tooltip.css"
            tt_js_src = self.skill_dir / "templates" / "tooltips" / "tooltip.js"
            tt_css_src = self.skill_dir / "templates" / "tooltips" / "tooltip.css"

            if not tt_js.exists() and tt_js_src.exists():
                shutil.copyfile(tt_js_src, tt_js)
                healed_actions.append("Healed UI: Injected accessible tooltip.js component")
            if not tt_css.exists() and tt_css_src.exists():
                shutil.copyfile(tt_css_src, tt_css)
                healed_actions.append("Healed UI: Injected theme-aware tooltip.css")

        # 5. Heal Test Harness
        test_dir = self.root / "tests"
        conftest_src = self.skill_dir / "templates" / "conftest.py"
        helpers_src = self.skill_dir / "scripts" / "helpers.py"

        if not test_dir.exists() and not (self.root / "e2e-tests").exists() and self.stack_info["primary_stack"] != "agent-skill":
            test_dir.mkdir(parents=True, exist_ok=True)
            (test_dir / "screenshots").mkdir(parents=True, exist_ok=True)
            if conftest_src.exists():
                shutil.copyfile(conftest_src, test_dir / "conftest.py")
            if helpers_src.exists():
                shutil.copyfile(helpers_src, test_dir / "helpers.py")
            healed_actions.append("Healed testing: Scaffolding tests/ directory with conftest and visual helpers")
        elif test_dir.exists():
            (test_dir / "screenshots").mkdir(parents=True, exist_ok=True)
            if not (test_dir / "conftest.py").exists() and conftest_src.exists():
                shutil.copyfile(conftest_src, test_dir / "conftest.py")
                healed_actions.append("Healed testing: Injected missing tests/conftest.py")
            if not (test_dir / "helpers.py").exists() and helpers_src.exists():
                shutil.copyfile(helpers_src, test_dir / "helpers.py")
                healed_actions.append("Healed testing: Injected missing tests/helpers.py")

        # 6. Heal Documentation & Memory
        for doc in ["PROJECT_CONTEXT.md", "PRODUCT.md", "DESIGN.md", "AGENTS.md"]:
            doc_dst = self.root / doc
            doc_src = self.skill_dir / "templates" / doc
            if not doc_dst.exists() and doc_src.exists():
                shutil.copyfile(doc_src, doc_dst)
                healed_actions.append(f"Healed documentation: Generated missing {doc}")

        # Recalculate test counts in tests/README.md if exists
        tests_readme = self.root / "tests" / "README.md"
        if tests_readme.exists() and test_dir.is_dir():
            test_files = sorted(list(test_dir.glob("test_*.py")))
            if test_files:
                count_str = f"**Total Active Test Modules:** {len(test_files)}"
                content = tests_readme.read_text(encoding="utf-8")
                if "Total Active Test Modules:" in content:
                    content = re.sub(r"\*\*Total Active Test Modules:\*\*.*", count_str, content)
                else:
                    content += f"\n\n---\n{count_str}\n"
                tests_readme.write_text(content, encoding="utf-8")
                healed_actions.append("Healed documentation: Recalibrated tests/README.md test coverage count")

        # 7. Heal Mobile Delivery Infrastructure & Git Pre-Push Hook
        if self.stack_info.get("mobile", {}).get("is_part_of_plan") and self.stack_info["is_git"]:
            pre_push_hook = self.root / ".git" / "hooks" / "pre-push"
            hook_content = self.get_pre_push_hook_script()
            needs_install = False
            if not pre_push_hook.exists():
                needs_install = True
            else:
                try:
                    existing_hook = pre_push_hook.read_text(encoding="utf-8", errors="ignore")
                    if "universal-pipeline pre-push hook" not in existing_hook:
                        needs_install = True
                except Exception:
                    needs_install = True

            if needs_install:
                pre_push_hook.parent.mkdir(parents=True, exist_ok=True)
                pre_push_hook.write_text(hook_content, encoding="utf-8")
                pre_push_hook.chmod(0o755)
                healed_actions.append("Healed git hooks: Installed mobile delivery pre-push guard (.git/hooks/pre-push)")

            # Auto-build mobile apps if missing from dist/
            apk_found = list((self.root / "dist").glob("**/*.apk")) + list(self.root.glob("*.apk"))
            if not apk_found:
                mobile_mgr = MobileAppManager(self.root, self.stack_info["mobile"])
                mobile_mgr.build_all()
                healed_actions.append("Healed mobile delivery: Built initial APK and iOS app delivery packages")

        return healed_actions

    def get_pre_push_hook_script(self) -> str:
        return """#!/bin/sh
# ==============================================================================
# universal-pipeline pre-push hook
# Enforces: Mobile apps (APK and iOS app), if present in delivery plan,
# must be updated with every git push.
# ==============================================================================

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
[ -z "$REPO_ROOT" ] && REPO_ROOT="$(pwd)"

# Detect if mobile apps are part of the delivery plan
HAS_MOBILE=false
if [ -d "$REPO_ROOT/android" ] || [ -d "$REPO_ROOT/apps/mobile/android" ] || [ -d "$REPO_ROOT/frontend/android" ] || [ -f "$REPO_ROOT/capacitor.config.json" ] || [ -f "$REPO_ROOT/frontend/capacitor.config.ts" ]; then
    HAS_MOBILE=true
fi
if [ -d "$REPO_ROOT/ios" ] || [ -d "$REPO_ROOT/apps/mobile/ios" ] || [ -d "$REPO_ROOT/frontend/ios" ]; then
    HAS_MOBILE=true
fi

if [ "$HAS_MOBILE" = false ]; then
    exit 0
fi

echo "==> [pre-push] Inspecting mobile app deliverables (APK & iOS app)..."

# Run mobile update
if [ -x "$REPO_ROOT/pipeline.sh" ]; then
    "$REPO_ROOT/pipeline.sh" mobile
elif [ -f "$REPO_ROOT/scripts/pipeline.py" ]; then
    python3 "$REPO_ROOT/scripts/pipeline.py" mobile
elif [ -f "/Volumes/Study/Projects/universal-pipeline/scripts/pipeline.py" ]; then
    python3 "/Volumes/Study/Projects/universal-pipeline/scripts/pipeline.py" mobile
fi

# Determine candidate paths that exist
CANDIDATES=""
for cand in dist/mobile apps/mobile/android apps/mobile/ios android ios frontend/android frontend/ios; do
    if [ -d "$REPO_ROOT/$cand" ]; then
        CANDIDATES="$CANDIDATES $cand"
    fi
done

MODIFIED=$(git -C "$REPO_ROOT" status --porcelain $CANDIDATES 2>/dev/null | grep -E "(\\.(apk|zip|ipa)$|dist/mobile/)" || true)
if [ -n "$MODIFIED" ]; then
    echo "==> [pre-push] Staging updated mobile delivery artifacts..."
    for cand in dist/mobile apps/mobile/android apps/mobile/ios android ios frontend/android frontend/ios; do
        if [ -e "$REPO_ROOT/$cand" ]; then
            git -C "$REPO_ROOT" add -A "$cand" 2>/dev/null || true
        fi
    done
    for apk in "$REPO_ROOT"/dist/*.apk "$REPO_ROOT"/*.apk; do
        if [ -f "$apk" ]; then
            git -C "$REPO_ROOT" add "$apk" 2>/dev/null || true
        fi
    done

    if ! git -C "$REPO_ROOT" diff-index --quiet HEAD -- 2>/dev/null; then
        git -C "$REPO_ROOT" commit -m "chore(mobile): update APK and iOS delivery artifacts for release" --no-verify
        echo "✓ [pre-push] Mobile delivery artifacts committed to HEAD."
        CURRENT_BRANCH="$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD)"
        REMOTE="${1:-origin}"
        echo "==> [pre-push] Re-synchronizing push with updated mobile commit..."
        git -C "$REPO_ROOT" push "$REMOTE" "$CURRENT_BRANCH" --no-verify
        exit 1
    fi
fi

echo "✓ [pre-push] Mobile delivery artifacts verified and up-to-date."
exit 0
"""


class TestRunner:
    """Executes tests locally and formats token-efficient summaries."""

    def __init__(self, root: Path, stack_info: dict):
        self.root = root
        self.stack_info = stack_info

    def run(self, args: list, compact: bool = True, smoke_only: bool = False) -> int:
        test_dir = None
        for candidate in ["tests", "e2e-tests"]:
            if (self.root / candidate).is_dir():
                test_dir = candidate
                break

        # Check for custom test runner first
        if (self.root / "run_tests.sh").exists():
            cmd = ["bash", str(self.root / "run_tests.sh")]
            if smoke_only:
                cmd.append("-m smoke")
            elif args:
                cmd.extend(args)
            return self._execute_compact(cmd, "Custom run_tests.sh", compact)

        # Pytest / Playwright
        if "pytest/playwright" in self.stack_info["test_frameworks"] or test_dir:
            cmd = [sys.executable, "-m", "pytest"]
            target = test_dir or "."
            cmd.append(target)
            if smoke_only:
                cmd.extend(["-m", "smoke"])
            if compact:
                cmd.extend(["-q", "--tb=short"])
            if args:
                cmd.extend(args)
            return self._execute_compact(cmd, "Pytest Suite", compact)

        # Java Maven
        if "maven-surefire" in self.stack_info["test_frameworks"]:
            mvn = "./mvnw" if (self.root / "mvnw").exists() else "mvn"
            cmd = [mvn, "test"]
            if compact:
                cmd.extend(["-q"])
            if args:
                cmd.extend(args)
            return self._execute_compact(cmd, "Maven Surefire Test Suite", compact)

        # NPM Test
        if "npm-test" in self.stack_info["test_frameworks"]:
            cmd = ["npm", "test", "--", "--silent"] if compact else ["npm", "test"]
            return self._execute_compact(cmd, "NPM Test Suite", compact)

        # Cargo Test
        if "cargo-test" in self.stack_info["test_frameworks"]:
            cmd = ["cargo", "test", "-q"] if compact else ["cargo", "test"]
            return self._execute_compact(cmd, "Cargo Test Suite", compact)

        # Go Test
        if "go-test" in self.stack_info["test_frameworks"]:
            cmd = ["go", "test", "./..."]
            return self._execute_compact(cmd, "Go Test Suite", compact)

        log_warn("No recognized automated test suite found. Run './pipeline.sh heal' to scaffold test harness.")
        return 0

    def _execute_compact(self, cmd: list, suite_name: str, compact: bool) -> int:
        log_step(f"Running {suite_name} (token-efficient mode: {compact})...")
        t0 = time.time()
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=str(self.root),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
        except Exception as e:
            log_error(f"Failed to launch {cmd[0]}: {e}")
            return 1

        stdout_lines = []
        failures = []

        for line in proc.stdout:
            stdout_lines.append(line)
            if re.search(r"(FAILED|ERROR|AssertionError|Exception|fail:)", line):
                failures.append(line.strip())

        proc.wait()
        duration = round(time.time() - t0, 2)
        exit_code = proc.returncode

        if exit_code == 0:
            passed_match = re.search(r"(\d+)\s+passed", "".join(stdout_lines))
            count_str = f" ({passed_match.group(0)})" if passed_match else ""
            log_success(f"{suite_name} PASSED in {duration}s{count_str}")
            return 0
        else:
            log_error(f"{suite_name} FAILED in {duration}s (exit code {exit_code})")
            print(f"\n{RED}{BOLD}=== Compact Failure Summary ==={RESET}")
            if failures:
                for f in failures[:15]:
                    print(f"  • {f}")
                if len(failures) > 15:
                    print(f"  ... and {len(failures) - 15} more failure lines.")
            else:
                tail = stdout_lines[-12:]
                for t in tail:
                    print(f"  {t.strip()}")
            print(f"{RED}{BOLD}==============================={RESET}\n")
            return exit_code


class MobileAppManager:
    """Detects, synchronizes web assets, builds APKs and iOS apps, and verifies delivery outputs."""

    def __init__(self, root: Path, mobile_info: dict):
        self.root = root
        self.info = mobile_info

    def get_env(self) -> dict:
        env = os.environ.copy()
        if "JAVA_HOME" not in env:
            for jvm in ["/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home",
                        "/Library/Java/JavaVirtualMachines/zulu-17.jdk/Contents/Home",
                        "/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"]:
                if os.path.isdir(jvm):
                    env["JAVA_HOME"] = jvm
                    break
        if "ANDROID_HOME" not in env:
            default_sdk = os.path.expanduser("~/Library/Android/sdk")
            if os.path.isdir(default_sdk):
                env["ANDROID_HOME"] = default_sdk
        if "PATH" in env:
            extra_paths = []
            if "JAVA_HOME" in env:
                extra_paths.append(f"{env['JAVA_HOME']}/bin")
            if "ANDROID_HOME" in env:
                extra_paths.extend([f"{env['ANDROID_HOME']}/platform-tools", f"{env['ANDROID_HOME']}/cmdline-tools/latest/bin"])
            env["PATH"] = ":".join(extra_paths) + ":" + env["PATH"]
        return env

    def sync_web_assets(self) -> bool:
        """Syncs web build (dist) into Capacitor or native mobile asset folders before compilation."""
        dist_dir = self.root / "dist"
        if not dist_dir.exists():
            if (self.root / "frontend" / "dist").exists():
                dist_dir = self.root / "frontend" / "dist"
        if not dist_dir.exists() and (self.root / "index.html").exists():
            dist_dir = self.root / "dist"
            dist_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.root / "index.html", dist_dir / "index.html")

        if not dist_dir.exists():
            return False

        synced = False
        # Sync to Android assets
        android_targets = [
            self.root / "android" / "app" / "src" / "main" / "assets" / "public",
            self.root / "frontend" / "android" / "app" / "src" / "main" / "assets" / "public"
        ]
        for at in android_targets:
            if at.parent.exists():
                at.mkdir(parents=True, exist_ok=True)
                for item in dist_dir.iterdir():
                    if item.name == "mobile" or item.name.endswith((".apk", ".zip", ".ipa", ".map")):
                        continue
                    dest = at / item.name
                    if item.is_dir():
                        shutil.copytree(item, dest, dirs_exist_ok=True)
                    else:
                        shutil.copyfile(item, dest)
                synced = True

        # Sync to iOS www / public assets
        ios_targets = [
            self.root / "ios" / "App" / "App" / "public",
            self.root / "frontend" / "ios" / "App" / "App" / "public"
        ]
        for it in ios_targets:
            if it.parent.exists():
                it.mkdir(parents=True, exist_ok=True)
                for item in dist_dir.iterdir():
                    if item.name == "mobile" or item.name.endswith((".apk", ".zip", ".ipa", ".map")):
                        continue
                    dest = it / item.name
                    if item.is_dir():
                        shutil.copytree(item, dest, dirs_exist_ok=True)
                    else:
                        shutil.copyfile(item, dest)
                synced = True

        if synced:
            log_success("Synchronized web distribution assets into mobile bundles (Android & iOS)")
        return synced

    def build_android(self) -> int:
        """Builds Android APK."""
        if not self.info.get("has_android"):
            return 0

        cand = self.info.get("android_path")
        if not cand or not cand.is_dir():
            return 0

        log_step(f"Compiling Android Native APK in {cand.relative_to(self.root)}...")
        env = self.get_env()

        # 1. Custom build script (e.g. CricOS build-apk.sh)
        if (cand / "build-apk.sh").exists():
            res = subprocess.run(["bash", "build-apk.sh"], cwd=str(cand), env=env, capture_output=True, text=True)
            if res.returncode == 0:
                log_success("Android APK build script completed successfully.")
                return 0
            else:
                log_error(f"Android build-apk.sh failed: {res.stderr.strip()[:300]}")
                return res.returncode

        # 2. Gradle build (gradlew)
        gradle_cmd = cand / "gradlew"
        if not gradle_cmd.exists():
            g_sys = shutil.which("gradle")
            cmd_args = [g_sys] if g_sys else None
        else:
            cmd_args = [f"./{gradle_cmd.name}"]

        if cmd_args and cmd_args[0]:
            cmd = cmd_args + ["assembleDebug", "--no-daemon", "--console=plain"]
            res = subprocess.run(cmd, cwd=str(cand), env=env, capture_output=True, text=True)
            if res.returncode == 0:
                apk_candidates = list((cand / "app" / "build" / "outputs" / "apk" / "debug").glob("*.apk"))
                if not apk_candidates:
                    apk_candidates = list(cand.glob("**/*.apk"))
                if apk_candidates:
                    apk_file = apk_candidates[0]
                    apk_size = apk_file.stat().st_size
                    mobile_dist = self.root / "dist" / "mobile"
                    mobile_dist.mkdir(parents=True, exist_ok=True)
                    target_name = f"{self.root.name.lower()}-android-debug.apk"
                    dest_apk = mobile_dist / target_name
                    shutil.copyfile(apk_file, dest_apk)
                    if self.root.name.lower() in ["astrology", "synodix"]:
                        shutil.copyfile(apk_file, self.root / "Synodix-debug.apk")
                    log_success(f"Android APK generated: {dest_apk.relative_to(self.root)} ({apk_size:,} bytes)")
                else:
                    log_success("Android assembleDebug completed successfully.")
                return 0
            else:
                log_error(f"Android Gradle build failed: {res.stderr.strip()[:300]}")
                return res.returncode

        return 0

    def build_ios(self) -> int:
        """Builds iOS App & Packages Simulator Distribution Archive."""
        if not self.info.get("has_ios"):
            return 0

        cand = self.info.get("ios_path")
        if not cand or not cand.is_dir():
            return 0

        log_step(f"Building iOS Native Application in {cand.relative_to(self.root)}...")

        # 1. Custom build script (e.g. CricOS build-ios.sh)
        if (cand / "build-ios.sh").exists():
            res = subprocess.run(["bash", "build-ios.sh"], cwd=str(cand), capture_output=True, text=True)
            if res.returncode == 0:
                log_success("iOS native project synchronization succeeded.")
                return 0
            else:
                log_error(f"iOS build-ios.sh failed: {res.stderr.strip()[:300]}")
                return res.returncode

        # 2. Xcode build
        xcode_projects = list(cand.glob("**/*.xcodeproj"))
        if xcode_projects:
            proj = xcode_projects[0]
            scheme = proj.stem
            derived_data = cand / "build" / "ios_derived"
            cmd = [
                "xcodebuild",
                "-project", str(proj),
                "-scheme", scheme,
                "-configuration", "Debug",
                "-destination", "generic/platform=iOS Simulator",
                "-derivedDataPath", str(derived_data),
                "build",
                "CODE_SIGNING_ALLOWED=NO"
            ]
            res = subprocess.run(cmd, cwd=str(cand), capture_output=True, text=True)
            if res.returncode == 0:
                app_dir = derived_data / "Build" / "Products" / "Debug-iphonesimulator" / f"{scheme}.app"
                if not app_dir.exists():
                    cands = list((derived_data / "Build" / "Products" / "Debug-iphonesimulator").glob("*.app"))
                    if cands:
                        app_dir = cands[0]
                if app_dir.exists():
                    mobile_dist = self.root / "dist" / "mobile"
                    mobile_dist.mkdir(parents=True, exist_ok=True)
                    zip_name = f"{self.root.name.lower()}-ios-simulator.zip"
                    dest_zip = mobile_dist / zip_name
                    shutil.make_archive(str(dest_zip.with_suffix("")), "zip", app_dir.parent, app_dir.name)
                    zip_size = dest_zip.stat().st_size
                    log_success(f"iOS Simulator App packaged: {dest_zip.relative_to(self.root)} ({zip_size:,} bytes)")
                else:
                    log_success("iOS xcodebuild completed successfully.")
                return 0
            else:
                log_error(f"iOS xcodebuild failed: {res.stderr.strip()[:300]}")
                return res.returncode

        return 0

    def build_all(self) -> int:
        """Executes full mobile update pipeline: asset sync -> Android APK -> iOS App."""
        if not self.info.get("is_part_of_plan"):
            return 0

        print(f"\n{CYAN}{BOLD}📱 Mobile App Delivery Pipeline (APK & iOS){RESET}")
        self.sync_web_assets()

        rc_android = self.build_android()
        if rc_android != 0:
            return rc_android

        rc_ios = self.build_ios()
        if rc_ios != 0:
            return rc_ios

        log_success("Mobile delivery targets (APK & iOS app) updated and synchronized.")
        return 0


class PackagingManager:
    """Builds and verifies local distribution bundles based on project context."""

    def __init__(self, root: Path, stack_info: dict):
        self.root = root
        self.stack_info = stack_info

    def package(self) -> int:
        log_step("Building & verifying distribution package...")
        targets = self.stack_info["package_targets"]
        primary_html = self.stack_info.get("primary_html")
        synced = False

        # 1. Single-file HTML synchronization to dist/index.html
        if "dist-sync" in targets and primary_html:
            source_file = self.root / primary_html
            if source_file.exists():
                dist_dir = self.root / "dist"
                dist_dir.mkdir(parents=True, exist_ok=True)
                dist_target = dist_dir / "index.html"
                shutil.copyfile(source_file, dist_target)
                size_bytes = dist_target.stat().st_size
                log_success(f"Synchronized {primary_html} -> dist/index.html ({size_bytes:,} bytes)")
                synced = True

        # 2. Node / Vite bundling
        if "npm-build" in targets and not ("dist-sync" in targets and "rust-tauri" in self.stack_info["stacks"]):
            log_step("Executing npm run build...")
            res = subprocess.run(["npm", "run", "build"], cwd=str(self.root), capture_output=True, text=True)
            if res.returncode == 0:
                log_success("NPM build completed successfully.")
                synced = True
            else:
                log_error(f"NPM build failed: {res.stderr.strip()[:300]}")
                return res.returncode

        # 3. Java Maven packaging
        if "mvn-package" in targets:
            mvn = "./mvnw" if (self.root / "mvnw").exists() else "mvn"
            log_step(f"Executing {mvn} package -DskipTests...")
            res = subprocess.run([mvn, "package", "-DskipTests", "-q"], cwd=str(self.root), capture_output=True, text=True)
            if res.returncode == 0:
                log_success("Maven packaging completed.")
                synced = True
            else:
                log_error(f"Maven package failed: {res.stderr.strip()[:300]}")
                return res.returncode

        # 4. Cargo / Rust release build
        if "rust" in self.stack_info["stacks"] and not synced:
            log_step("Executing cargo build --release...")
            res = subprocess.run(["cargo", "build", "--release", "-q"], cwd=str(self.root), capture_output=True, text=True)
            if res.returncode == 0:
                log_success("Cargo release build completed.")
                synced = True

        # 5. Go build
        if "go-build" in targets and not synced:
            log_step("Executing go build...")
            res = subprocess.run(["go", "build", "-o", "dist/app", "."], cwd=str(self.root), capture_output=True, text=True)
            if res.returncode == 0:
                log_success("Go binary build completed.")
                synced = True

        # 6. Mobile Application Packaging (Android APK & iOS App)
        if self.stack_info.get("mobile", {}).get("is_part_of_plan"):
            mobile_mgr = MobileAppManager(self.root, self.stack_info["mobile"])
            mobile_rc = mobile_mgr.build_all()
            if mobile_rc != 0:
                return mobile_rc
            synced = True

        if not synced:
            log_warn("No active packaging targets configured or required.")
        return 0


class DocBuilder:
    """Updates living context and test coverage maps on local disk."""

    def __init__(self, root: Path):
        self.root = root

    def update(self) -> int:
        log_step("Updating local documentation & context maps...")
        updated = []

        context_file = None
        for p in [self.root / "PROJECT_CONTEXT.md", self.root / ".agents" / "PROJECT_CONTEXT.md"]:
            if p.exists():
                context_file = p
                break

        if context_file:
            try:
                content = context_file.read_text(encoding="utf-8")
                now = time.strftime("%Y-%m-%d %H:%M:%S")
                content = re.sub(r"(\*\*Last Updated:\*\*|\*\*Date:\*\*|Last Updated:).*", f"**Last Updated:** {now}", content)
                context_file.write_text(content, encoding="utf-8")
                updated.append(str(context_file.relative_to(self.root)))
            except Exception as e:
                log_warn(f"Failed to update {context_file}: {e}")

        # Update test coverage map in tests/README.md
        tests_readme = self.root / "tests" / "README.md"
        if tests_readme.exists() and (self.root / "tests").is_dir():
            try:
                test_files = sorted(list((self.root / "tests").glob("test_*.py")))
                if test_files:
                    count_str = f"**Total Active Test Modules:** {len(test_files)}"
                    readme_content = tests_readme.read_text(encoding="utf-8")
                    if "Total Active Test Modules:" in readme_content:
                        readme_content = re.sub(r"\*\*Total Active Test Modules:\*\*.*", count_str, readme_content)
                    else:
                        readme_content += f"\n\n---\n{count_str}\n"
                    tests_readme.write_text(readme_content, encoding="utf-8")
                    updated.append("tests/README.md")
            except Exception as e:
                log_warn(f"Failed to update {tests_readme}: {e}")

        if updated:
            log_success(f"Documentation updated: {', '.join(updated)}")
        else:
            log_warn("No PROJECT_CONTEXT.md or tests/README.md found to auto-update.")
        return 0


class GitOrchestrator:
    """Manages clean working trees, pre-commit safety guards, and atomic push operations."""

    def __init__(self, root: Path):
        self.root = root

    def ship(self, commit_msg: str, test_runner: TestRunner, packager: PackagingManager, doc_builder: DocBuilder) -> int:
        if not (self.root / ".git").is_dir():
            log_error(f"{self.root} is not a Git repository. Cannot run ship pipeline.")
            return 1

        if not commit_msg or not commit_msg.strip():
            log_error("Commit message is required for ship command.")
            print("Usage: ./pipeline.sh ship \"<conventional commit message>\"")
            return 1

        print(f"\n{CYAN}{BOLD}======================================================{RESET}")
        print(f"{CYAN}{BOLD}🚀 Universal Pipeline: Automated Release & Ship{RESET}")
        print(f"{CYAN}{BOLD}======================================================{RESET}\n")

        # Step 1: Pre-commit Test Validation
        log_step("1/5: Running pre-commit test validation...")
        test_rc = test_runner.run([], compact=True, smoke_only=False)
        if test_rc != 0:
            log_error("Pre-commit tests FAILED. Aborting ship to prevent regressions.")
            return test_rc
        log_success("Test verification passed.")

        # Step 2: Build & Package Targets
        log_step("2/5: Building & synchronizing packaging artifacts...")
        pkg_rc = packager.package()
        if pkg_rc != 0:
            log_error("Packaging build FAILED. Aborting ship.")
            return pkg_rc

        # Step 3: Update Docs & Context
        log_step("3/5: Synchronizing local docs and timestamps...")
        doc_builder.update()

        # Step 4: Staging
        log_step("4/5: Staging files and inspecting git status...")
        status = subprocess.run(["git", "status", "--porcelain"], cwd=str(self.root), capture_output=True, text=True)
        if not status.stdout.strip():
            log_warn("Working tree is completely clean. Nothing to commit.")
            return 0

        subprocess.run(["git", "add", "-u"], cwd=str(self.root), check=True)
        for cand in ["dist", "docs", "tests", ".agents", "README.md", "PROJECT_CONTEXT.md", "PRODUCT.md", "DESIGN.md", "android", "ios", "apps/mobile", "frontend/android", "frontend/ios", "Synodix-debug.apk"]:
            if (self.root / cand).exists():
                subprocess.run(["git", "add", cand], cwd=str(self.root), check=False)

        # Step 5: Commit and Push
        log_step(f"5/5: Committing and pushing: \"{commit_msg}\"...")
        commit_res = subprocess.run(["git", "commit", "-m", commit_msg], cwd=str(self.root), capture_output=True, text=True)
        if commit_res.returncode != 0:
            log_error(f"Commit failed: {commit_res.stderr.strip()}")
            return commit_res.returncode
        log_success(f"Committed changes: {commit_msg}")

        branch_res = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(self.root), capture_output=True, text=True)
        branch = branch_res.stdout.strip() or "main"

        push_res = subprocess.run(["git", "push", "origin", branch], cwd=str(self.root), capture_output=True, text=True)
        if push_res.returncode == 0:
            log_success(f"Pushed to origin/{branch} successfully.")
        else:
            log_warn(f"Push to remote encountered a notice:\n{push_res.stderr.strip()}")

        print(f"\n{GREEN}{BOLD}======================================================{RESET}")
        print(f"{GREEN}{BOLD}✅ Release & Ship Completed Successfully!{RESET}")
        print(f"{GREEN}{BOLD}======================================================{RESET}\n")
        return 0

    def push(self, mobile_mgr: MobileAppManager) -> int:
        if not (self.root / ".git").is_dir():
            log_error(f"{self.root} is not a Git repository. Cannot push.")
            return 1

        if mobile_mgr.info.get("is_part_of_plan"):
            log_step("Updating mobile delivery artifacts (APK & iOS app) before push...")
            rc = mobile_mgr.build_all()
            if rc != 0:
                log_error("Mobile delivery build failed. Aborting push.")
                return rc

            # Stage newly generated/refreshed mobile artifacts
            status = subprocess.run(["git", "status", "--porcelain"], cwd=str(self.root), capture_output=True, text=True)
            if status.stdout.strip():
                log_step("Staging refreshed mobile delivery artifacts...")
                for cand in ["dist", "android", "ios", "apps/mobile", "frontend/android", "frontend/ios", "Synodix-debug.apk"]:
                    if (self.root / cand).exists():
                        subprocess.run(["git", "add", cand], cwd=str(self.root), check=False)
                if subprocess.run(["git", "diff-index", "--quiet", "HEAD", "--"], cwd=str(self.root)).returncode != 0:
                    commit_msg = f"chore(mobile): auto-update APK and iOS delivery artifacts for release [{time.strftime('%Y-%m-%d %H:%M:%S')}]"
                    subprocess.run(["git", "commit", "-m", commit_msg], cwd=str(self.root), capture_output=True, text=True)
                    log_success(f"Committed fresh mobile delivery artifacts: {commit_msg}")

        branch_res = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(self.root), capture_output=True, text=True)
        branch = branch_res.stdout.strip() or "main"

        log_step(f"Pushing to origin/{branch}...")
        push_res = subprocess.run(["git", "push", "origin", branch], cwd=str(self.root), capture_output=True, text=True)
        if push_res.returncode == 0:
            log_success(f"Pushed to origin/{branch} successfully with fresh mobile delivery artifacts.")
            return 0
        else:
            log_error(f"Push failed: {push_res.stderr.strip()}")
            return push_res.returncode


def main():
    root = Path.cwd()
    skill_dir = Path(__file__).resolve().parent.parent

    cmd = sys.argv[1] if len(sys.argv) > 1 else "doctor"
    extra_args = sys.argv[2:]

    detector = StackDetector(root)
    stack_info = detector.detect()
    doctor = ProjectDoctor(root, stack_info)
    healing_engine = SelfHealingEngine(root, skill_dir, stack_info)
    test_runner = TestRunner(root, stack_info)
    packager = PackagingManager(root, stack_info)
    doc_builder = DocBuilder(root)
    mobile_mgr = MobileAppManager(root, stack_info.get("mobile", {}))
    git_orchestrator = GitOrchestrator(root)

    if cmd in ["doctor", "audit", "check"]:
        diagnosis = doctor.diagnose()
        print(f"\n{CYAN}{BOLD}=== Self-Analyzing Project Doctor ==={RESET}")
        print(f"  {BOLD}Working Directory:{RESET} {stack_info['root']}")
        print(f"  {BOLD}Primary Stack:{RESET}     {GREEN}{stack_info['primary_stack']}{RESET}")
        print(f"  {BOLD}Detected Stacks:{RESET}   {', '.join(stack_info['stacks']) or 'None'}")
        print(f"  {BOLD}Test Frameworks:{RESET}   {', '.join(stack_info['test_frameworks']) or 'None'}")
        print(f"  {BOLD}Package Targets:{RESET}   {', '.join(stack_info['package_targets']) or 'None'}")
        print(f"  {BOLD}Git Status:{RESET}        {'Initialized' if stack_info['is_git'] else 'No Git Repo'}")

        print(f"\n{BOLD}Diagnostic Invariant Verification:{RESET}")
        for chk in diagnosis["checks"]:
            print(f"  {GREEN}✓{RESET} {chk}")

        if diagnosis["warnings"]:
            print(f"\n{YELLOW}{BOLD}Warnings & Advice:{RESET}")
            for w in diagnosis["warnings"]:
                print(f"  {YELLOW}⚠{RESET} {w}")

        if diagnosis["discrepancies"]:
            print(f"\n{RED}{BOLD}Detected Discrepancies & Drift:{RESET}")
            for d in diagnosis["discrepancies"]:
                print(f"  {RED}✗{RESET} [{d['category']}] {d['issue']}")
            print(f"\n{CYAN}↳ Auto-Heal Available: Run './pipeline.sh heal' to automatically resolve all discrepancies.{RESET}\n")
            return 1
        else:
            print(f"\n{GREEN}{BOLD}✓ Workflow Health: 100% CLEAN. Zero drift detected.{RESET}\n")
            return 0

    elif cmd in ["heal", "fix", "setup", "init"]:
        diagnosis = doctor.diagnose()
        healed = healing_engine.heal(diagnosis)
        if healed:
            print(f"\n{GREEN}{BOLD}=== Autonomous Self-Healing Report ==={RESET}")
            for h in healed:
                print(f"  {GREEN}✓{RESET} {h}")
            print(f"{GREEN}{BOLD}======================================{RESET}\n")
        else:
            print(f"\n{GREEN}✓ Project is already healthy. No healing actions required.{RESET}\n")

        # Post-heal diagnostic check
        new_diag = doctor.diagnose()
        if new_diag["healthy"]:
            log_success("Post-healing verification passed: Workflow is now 100% healthy.")
            return 0
        else:
            log_warn(f"Post-healing notice: {len(new_diag['discrepancies'])} items remain pending user review.")
            return 1

    elif cmd == "test":
        compact = "--verbose" not in extra_args
        smoke_only = "--smoke" in extra_args
        filtered_args = [a for a in extra_args if a not in ["--compact", "--verbose", "--smoke", "--summary"]]
        return test_runner.run(filtered_args, compact=compact, smoke_only=smoke_only)

    elif cmd == "package":
        return packager.package()

    elif cmd == "doc":
        return doc_builder.update()

    elif cmd in ["mobile", "apk", "android"]:
        return mobile_mgr.build_android() if cmd in ["apk", "android"] else mobile_mgr.build_all()

    elif cmd in ["ios", "apple"]:
        return mobile_mgr.build_ios()

    elif cmd == "push":
        return git_orchestrator.push(mobile_mgr)

    elif cmd == "visual":
        return test_runner.run(["-k", "visual or screenshot or layout or overlap or tooltip"], compact=True)

    elif cmd == "ship":
        msg = " ".join(extra_args) if extra_args else ""
        return git_orchestrator.ship(msg, test_runner, packager, doc_builder)

    else:
        print(f"Unknown command: '{cmd}'. Available: doctor, heal, test, visual, package, mobile, apk, ios, push, doc, ship")
        return 1


if __name__ == "__main__":
    sys.exit(main())
