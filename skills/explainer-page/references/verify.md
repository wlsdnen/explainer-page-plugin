# 검증

필요한 도구: [uv](https://docs.astral.sh/uv/), Node(계산 로직이 있을 때). 서버를 띄웠다면 직접 띄운 것만 PID로 끈다. 이름 패턴으로 `pkill` 하지 않는다.

## 1. 기본 검사: check_page.py

skill 폴더의 `scripts/check_page.py`가 확인하는 것:

- 375·768·1280px 라이트에서 가로 넘침 없음.
- 콘솔 에러·페이지 에러 0.
- 375px 터치 환경에서 첫 `[data-widget]` 안의 첫 조작부가 44×44px 이상이고, 탭해도 에러가 나지 않음.

```sh
uv run --with playwright playwright install chromium            # 처음 한 번
uv run --with playwright python <skill-dir>/scripts/check_page.py <page-dir>/index.html
uv run --with playwright python <skill-dir>/scripts/check_page.py --self-test   # 스크립트 자체 확인
```

`<skill-dir>`는 이 SKILL.md가 있는 폴더다. 통과하면 `OK`를 찍고 0으로 끝나며, 실패하면 항목을 찍고 1로 끝난다.

## 2. 모든 조작부와 애니메이션

check_page.py는 첫 조작부만 누른다. 나머지는 스크래치 디렉터리에 Playwright 스크립트를 따로 써서 확인한다.

- 보이는 버튼을 모두 누르고, 슬라이더를 최소·최대로 옮기고(`input`/`change` 이벤트 발생), select의 마지막 항목을 고른 뒤 콘솔 에러와 가로 넘침을 다시 본다.
예시 스크립트(`drive.py`, 스크래치 디렉터리에 두고 `uv run --with playwright python drive.py <page-dir>/index.html`):

```python
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

url = Path(sys.argv[1]).resolve().as_uri()
bad = []
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    for w in (1280, 390):
        page = browser.new_page(viewport={"width": w, "height": 900}, color_scheme="light")
        page.on("console", lambda m: m.type == "error" and bad.append(f"@{w} console: {m.text}"))
        page.on("pageerror", lambda e: bad.append(f"@{w} pageerror: {e}"))
        page.goto(url, wait_until="load")
        page.wait_for_timeout(500)
        for b in page.locator("button:visible").all():
            b.click()
            page.wait_for_timeout(100)
        for r in page.locator("input[type=range]:visible").all():
            for v in ("min", "max"):
                r.evaluate(f"e => {{ e.value = e.{v}; e.dispatchEvent(new Event('input', {{bubbles: true}})); e.dispatchEvent(new Event('change', {{bubbles: true}})); }}")
        for s in page.locator("select:visible").all():
            s.select_option(index=s.locator("option").count() - 1)
        page.wait_for_timeout(500)
        sw, iw = page.evaluate("[document.documentElement.scrollWidth, innerWidth]")
        if sw > iw:
            bad.append(f"@{w} horizontal overflow {sw}>{iw}")
        page.close()
    browser.close()
print("\n".join(bad) or "OK")
sys.exit(1 if bad else 0)
```

- 애니메이션이 실제로 움직이는지, 재생/일시정지·처음으로가 먹는지, 슬라이더를 옮기면 그림이 바뀌는지는 상태(예: SVG 속성)를 두 번 읽어 비교하거나 스크린샷으로 눈으로 본다.
- `prefers-reduced-motion`에서 멈춘 채 시작하는지는 `browser.new_page(reduced_motion="reduce")`로 확인한다.

## 3. check.mjs (계산 로직이 있을 때만)

- 수식·시뮬레이션이 `<script id="core">`에 있으면 페이지 폴더에 `check.mjs`를 둔다. 정규식으로 core를 떼어 `new Function`으로 평가하고, 검사할 함수 이름 목록(`NAMES`)의 함수가 있는지와 값을 `node:assert/strict`로 확인한다. 실패하면 0이 아닌 코드로 끝난다.

```js
import { readFileSync } from "node:fs";
import assert from "node:assert/strict";
const html = readFileSync(new URL("./index.html", import.meta.url), "utf8");
const core = html.match(/<script id="core">([\s\S]*?)<\/script>/)[1];
const NAMES = ["softmax"];
const lib = new Function(`${core}; return { ${NAMES.join(", ")} };`)();
for (const n of NAMES) assert.equal(typeof lib[n], "function", n);
assert.ok(Math.abs(lib.softmax([1, 1]).reduce((a, b) => a + b) - 1) < 1e-9);
console.log("check OK");
```

- 실행: `node <page-dir>/check.mjs`.
- core에 DOM 참조를 넣거나 태그 id를 바꾸면 check가 깨진다. check가 다룰 함수를 core에 더하면 `NAMES`에도 더한다.
- 계산 로직이 없는 페이지에는 만들지 않는다.

## 4. 배포 전

- 배포 폴더에서 `CLAUDE.md`, `check.mjs`, 원본 영상(`media/`)을 뺀다.
- CDN 링크가 정확한 버전으로 고정되어 있고 열리는지, vendoring했다면 상대 경로가 맞는지 확인한다.
