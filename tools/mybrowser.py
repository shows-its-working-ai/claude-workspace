"""Claude's own browser. Everything (binary + profile/cookies) lives in this folder.

Never point this at the owner's Chrome/Edge profile or executable.

    tools\\venv\\Scripts\\python.exe tools\\mybrowser.py <url> [screenshot.png] [--show]
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
CHROME = ROOT / "browser" / "chromium" / "chrome-win64" / "chrome.exe"
PROFILE = ROOT / "browser" / "profile"   # Claude's cookies/logins live here only


def open_browser(p, show=False):
    # cycle 124: tests (run_all sets CW_EPHEMERAL=1) get a throwaway profile: no cookies, and several can run at once.
    import os
    if os.environ.get("CW_EPHEMERAL") == "1":
        b = p.chromium.launch(executable_path=str(CHROME), headless=not show)
        return b.new_context(viewport={"width": 1280, "height": 800})
    return p.chromium.launch_persistent_context(
        str(PROFILE), executable_path=str(CHROME), headless=not show,
        viewport={"width": 1280, "height": 800})


def shard(items):
    # cycle 225: run_all splits the three whole-site checks (canvases, links, masher: 469 of 1,002 summed seconds)
    # into shards via CW_SHARD="i/n"; each shard takes every n-th item. Unset = everything (the mutation run uses
    # that). A shard that gets NOTHING fails, so a bad split can't pass by checking nothing.
    import os
    s = os.environ.get("CW_SHARD")
    if not s: return items
    i, n = map(int, s.split("/")); part = items[i::n]
    print(f"shard {i}/{n}: {len(part)} of {len(items)}")
    if not part: sys.exit(f"shard {i}/{n} got no items: nothing would be checked")
    return part


def open_touch(p, width=390, height=800):
    # cycle 212: a throwaway phone-sized context with a touchscreen, for testing real taps (no profile, ever).
    b = p.chromium.launch(executable_path=str(CHROME), headless=True)
    return b.new_context(viewport={"width": width, "height": height}, has_touch=True, is_mobile=True)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--show"]
    url = args[0] if args else "https://example.com"
    shot = args[1] if len(args) > 1 else None
    with sync_playwright() as p:
        ctx = open_browser(p, show="--show" in sys.argv)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(url, timeout=60000)
        print("title:", page.title())
        print("browser:", ctx.browser.version if ctx.browser else "persistent ctx")
        if shot:
            page.screenshot(path=shot)
            print("saved", shot)
        if "--show" in sys.argv:
            print("window open - close it when finished")
            page.wait_for_event("close", timeout=0)
        ctx.close()
