"""Check an explainer page: horizontal overflow at 375/768/1280px, console errors,
and touch target size of the first [data-widget] control at 375px.

Usage:
  uv run --with playwright python check_page.py path/to/index.html
  uv run --with playwright python check_page.py --self-test
First run once: uv run --with playwright playwright install chromium
"""
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

WIDTHS = (375, 768, 1280)
MIN_TOUCH_PX = 44


def check(path: Path) -> list[str]:
    url = path.resolve().as_uri()
    bad = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for w in WIDTHS:
            page = browser.new_page(viewport={"width": w, "height": 900}, color_scheme="light",
                                    has_touch=w == 375, is_mobile=w == 375)
            page.on("console", lambda m, w=w: m.type == "error" and bad.append(f"@{w} console: {m.text}"))
            page.on("pageerror", lambda e, w=w: bad.append(f"@{w} pageerror: {e}"))
            page.goto(url, wait_until="load")
            page.wait_for_timeout(300)
            sw, iw = page.evaluate("[document.documentElement.scrollWidth, innerWidth]")
            if sw > iw:
                bad.append(f"@{w} horizontal overflow {sw}>{iw}")
            if w == 375:
                ctl = page.locator("[data-widget] :is(button, input, select, [role=button]):visible").first
                if ctl.count() == 0:
                    bad.append("@375 no visible control inside [data-widget]")
                else:
                    box = ctl.bounding_box()
                    if box["width"] < MIN_TOUCH_PX or box["height"] < MIN_TOUCH_PX:
                        bad.append(f"@375 first [data-widget] control {box['width']:.0f}x{box['height']:.0f}px < {MIN_TOUCH_PX}px")
                    ctl.tap()
                    page.wait_for_timeout(200)
            page.close()
        browser.close()
    return bad


GOOD = """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>ok</title></head>
<body><div data-widget><button style="min-width:44px;min-height:44px">재생</button></div></body></html>"""

BAD = """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>bad</title></head>
<body><div style="width:2000px">wide</div><div data-widget><button style="font-size:8px;padding:0">x</button></div>
<script>console.error("boom")</script></body></html>"""


def self_test() -> None:
    with tempfile.TemporaryDirectory() as d:
        good, bad = Path(d, "good.html"), Path(d, "bad.html")
        good.write_text(GOOD, encoding="utf-8")
        bad.write_text(BAD, encoding="utf-8")
        assert check(good) == [], check(good)
        found = check(bad)
        for needle in ("@375 horizontal overflow", "@768 horizontal overflow", "@1280 horizontal overflow",
                       "console: boom", "< 44px"):
            assert any(needle in f for f in found), (needle, found)
    print("self-test OK")


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        self_test()
        sys.exit(0)
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    problems = check(Path(sys.argv[1]))
    print("\n".join(problems) or "OK")
    sys.exit(1 if problems else 0)
