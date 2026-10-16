"""
conftest.py — Universal Playwright Test Suite Fixtures
Provides shared, isolated browser contexts and console error tracking.
"""

import pathlib
import pytest
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

# Default target URL (can point to local single-file HTML or local dev server)
LOCAL_INDEX = pathlib.Path("index.html").resolve()
APP_URL = LOCAL_INDEX.as_uri() if LOCAL_INDEX.exists() else "http://localhost:3000"


@pytest.fixture(scope="session")
def event_loop_policy():
    import asyncio
    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture(scope="function")
async def page_with_data():
    """
    Launches headless Chromium, navigates to target local app,
    and captures console logs for error assertions.
    """
    console_errors = []
    async with async_playwright() as pw:
        browser: Browser = await pw.chromium.launch(headless=True)
        ctx: BrowserContext = await browser.new_context(
            viewport={"width": 1400, "height": 900}
        )
        page: Page = await ctx.new_page()

        # Capture console errors
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: console_errors.append(f"PAGE ERROR: {e}"))

        await page.goto(APP_URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(300)

        page._console_errors = console_errors

        yield page

        await browser.close()


@pytest.fixture(scope="function")
async def blank_page():
    """
    Launches headless Chromium for testing uninitialized or first-run empty states.
    """
    console_errors = []
    async with async_playwright() as pw:
        browser: Browser = await pw.chromium.launch(headless=True)
        ctx: BrowserContext = await browser.new_context(
            viewport={"width": 1400, "height": 900}
        )
        page: Page = await ctx.new_page()

        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: console_errors.append(f"PAGE ERROR: {e}"))

        await page.goto(APP_URL, wait_until="domcontentloaded")
        page._console_errors = console_errors

        yield page

        await browser.close()
