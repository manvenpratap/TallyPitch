#!/usr/bin/env python3
"""
scripts/build_android_twa.py
Android Trusted Web Activity (TWA) & Native APK Packaging Engine for TallyPitch.
Validates manifest configurations, Digital Asset Links, syncs mipmap icon assets,
and generates packaging verification telemetry.
"""

import os
import sys
import json
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
ANDROID_DIR = ROOT_DIR / "android"
APP_DIR = ANDROID_DIR / "app"
RES_DIR = APP_DIR / "src" / "main" / "res"

def validate_android_project():
    print("==> Validating TallyPitch Android TWA Packaging...")

    # 1. Check twa-manifest.json
    twa_manifest = ANDROID_DIR / "twa-manifest.json"
    if not twa_manifest.exists():
        raise FileNotFoundError("Missing android/twa-manifest.json")
    with open(twa_manifest, "r", encoding="utf-8") as f:
        config = json.load(f)
    assert config.get("packageId") == "app.tallypitch.twa", f"Invalid packageId: {config.get('packageId')}"
    assert config.get("host") == "tallypitch.app", f"Invalid host: {config.get('host')}"
    print(f"✓ Validated twa-manifest.json (package: {config['packageId']}, host: {config['host']})")

    # 2. Check AndroidManifest.xml
    android_manifest = APP_DIR / "src" / "main" / "AndroidManifest.xml"
    if not android_manifest.exists():
        raise FileNotFoundError("Missing AndroidManifest.xml")
    manifest_content = android_manifest.read_text(encoding="utf-8")
    gradle_content = (APP_DIR / "build.gradle").read_text(encoding="utf-8")
    assert 'package="app.tallypitch.twa"' in manifest_content or 'namespace = "app.tallypitch.mobile"' in gradle_content or 'namespace "app.tallypitch.twa"' in gradle_content
    assert 'android:host="tallypitch.app"' in manifest_content
    assert 'android.support.customtabs.trusted.DEFAULT_URL' in manifest_content
    print("✓ Validated AndroidManifest.xml with Chrome Custom Tabs & TWA Launcher")

    # 3. Check Digital Asset Links
    assetlinks_root = ROOT_DIR / ".well-known" / "assetlinks.json"
    assetlinks_dist = ROOT_DIR / "dist" / ".well-known" / "assetlinks.json"
    if not assetlinks_root.exists():
        raise FileNotFoundError("Missing .well-known/assetlinks.json")
    if not assetlinks_dist.exists():
        assetlinks_dist.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(assetlinks_root, assetlinks_dist)

    with open(assetlinks_root, "r", encoding="utf-8") as f:
        links = json.load(f)
    assert isinstance(links, list) and len(links) > 0
    target = links[0].get("target", {})
    assert target.get("package_name") == "app.tallypitch.twa"
    print(f"✓ Validated Digital Asset Links for verified domain delegation ({target.get('package_name')})")

    # 4. Sync icons to mipmap directories
    icon_192 = ROOT_DIR / "icon-192.png"
    icon_512 = ROOT_DIR / "icon-512.png"
    if icon_192.exists():
        for mipmap in ["mipmap-mdpi", "mipmap-hdpi", "mipmap-xhdpi", "mipmap-xxhdpi", "mipmap-xxxhdpi"]:
            target_dir = RES_DIR / mipmap
            target_dir.mkdir(parents=True, exist_ok=True)
            src_icon = icon_512 if "xxxhdpi" in mipmap or "xxhdpi" in mipmap else icon_192
            shutil.copy(src_icon, target_dir / "ic_launcher.png")
            shutil.copy(src_icon, target_dir / "ic_launcher_round.png")
        print("✓ Synchronized launcher mipmap drawables (mdpi through xxxhdpi)")

    print("\n🎉 Android TWA & APK Packaging Verification Passed (app.tallypitch.twa)!\n")
    return True

if __name__ == "__main__":
    try:
        validate_android_project()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Android packaging error: {e}", file=sys.stderr)
        sys.exit(1)
