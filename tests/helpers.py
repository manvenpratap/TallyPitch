"""
helpers.py — Universal Playwright Visual Regression & UI Testing Engine
Local machine assertions, bounding box collision checks, screenshot persistence,
console error interception, and offline visual catalog generator.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional

DEFAULT_SCREENSHOT_DIR = "tests/screenshots"


def get_bounding_boxes(page, selectors: List[str]) -> List[Dict[str, Any]]:
    """
    Retrieve rendered bounding client rects for a list of CSS selectors.
    Filters out hidden or zero-dimension elements.
    """
    return page.evaluate("""(selectors) => {
        const results = [];
        for (const sel of selectors) {
            const elements = document.querySelectorAll(sel);
            elements.forEach((el, index) => {
                const style = window.getComputedStyle(el);
                if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
                    return;
                }
                const rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    results.push({
                        selector: sel,
                        index: index,
                        id: el.id || '',
                        className: el.className || '',
                        x: rect.x,
                        y: rect.y,
                        left: rect.left,
                        top: rect.top,
                        right: rect.right,
                        bottom: rect.bottom,
                        width: rect.width,
                        height: rect.height,
                        zIndex: parseInt(style.zIndex, 10) || 0
                    });
                }
            });
        }
        return results;
    }""", selectors)


def check_element_overlaps(page, selectors: List[str], allowed_overlap_tolerance_px: float = 2.0) -> List[Dict[str, Any]]:
    """
    Detects if any visible floating UI elements (tooltips, modals, HUD overlays)
    overlap each other unexpectedly.
    Returns a list of detected overlaps with exact coordinates and intersection areas.
    """
    boxes = get_bounding_boxes(page, selectors)
    overlaps = []

    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            b1 = boxes[i]
            b2 = boxes[j]

            # Calculate overlap rectangle
            x_overlap = max(0.0, min(b1["right"], b2["right"]) - max(b1["left"], b2["left"]))
            y_overlap = max(0.0, min(b1["bottom"], b2["bottom"]) - max(b1["top"], b2["top"]))

            if x_overlap > allowed_overlap_tolerance_px and y_overlap > allowed_overlap_tolerance_px:
                area = x_overlap * y_overlap
                overlaps.append({
                    "element1": f"{b1['selector']} (id: {b1['id']})",
                    "element2": f"{b2['selector']} (id: {b2['id']})",
                    "box1": b1,
                    "box2": b2,
                    "overlapWidth": x_overlap,
                    "overlapHeight": y_overlap,
                    "overlapArea": area
                })

    return overlaps


def check_no_horizontal_overflow(page) -> bool:
    """
    Ensure the rendered page does not horizontally overflow the viewport.
    Returns True if clean, False if unexpected horizontal scrolling exists.
    """
    return page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth + 2")


def wait_for_scene_ready(page, timeout_ms: int = 500):
    """
    Wait for animations, WebGL, 2D Canvas, or SVG graph rendering to settle.
    """
    page.wait_for_timeout(timeout_ms)


def save_screenshot(page, name: str, base_dir: Optional[str] = None) -> str:
    """
    Saves a full viewport screenshot to the local machine directory.
    Never uploads to external cloud storage.
    """
    target_dir = Path(base_dir or DEFAULT_SCREENSHOT_DIR)
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{name}.png" if not name.endswith(".png") else name
    file_path = target_dir / filename

    page.screenshot(
        path=str(file_path),
        full_page=False,
        timeout=5000,
        animations="disabled"
    )

    # Regenerate local HTML gallery
    catalog_screenshots(str(target_dir))
    return str(file_path)


def catalog_screenshots(screenshot_dir: str = DEFAULT_SCREENSHOT_DIR) -> str:
    """
    Generates a zero-cloud local HTML gallery of all captured screenshots for local visual review.
    """
    p = Path(screenshot_dir)
    if not p.is_dir():
        return ""

    pngs = sorted(list(p.glob("*.png")))
    html_lines = [
        "<!DOCTYPE html>",
        "<html lang='en'><head><meta charset='utf-8'><title>Local Visual Regression Gallery</title>",
        "<style>",
        "body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }",
        "h1 { font-size: 20px; margin-bottom: 20px; font-weight: 600; }",
        ".grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }",
        ".card { background: #1e293b; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; overflow: hidden; padding: 12px; }",
        ".card img { width: 100%; height: auto; border-radius: 4px; display: block; border: 1px solid #334155; }",
        ".card .title { margin-top: 8px; font-size: 13px; font-weight: 500; word-break: break-all; }",
        "</style></head><body>",
        f"<h1>Local Visual Regression Gallery ({len(pngs)} captures)</h1>",
        "<div class='grid'>"
    ]

    for png in pngs:
        html_lines.append(f"<div class='card'><a href='{png.name}' target='_blank'><img src='{png.name}' alt='{png.stem}'></a><div class='title'>{png.name}</div></div>")

    html_lines.extend(["</div></body></html>"])
    gallery_path = p / "index.html"
    gallery_path.write_text("\n".join(html_lines), encoding="utf-8")
    return str(gallery_path)


def assert_no_critical_errors(page, custom_keywords: Optional[List[str]] = None):
    """
    Asserts that no uncaught JavaScript errors or critical exceptions occurred during test run.
    """
    default_keywords = [
        "TypeError", "ReferenceError", "SyntaxError", "Uncaught",
        "Cannot read property", "is not a function"
    ]
    keywords = custom_keywords or default_keywords
    errors = getattr(page, "_console_errors", [])
    hits = [e for e in errors if any(kw.lower() in e.lower() for kw in keywords)]
    assert not hits, f"Critical JS errors detected:\n" + "\n".join(hits)
