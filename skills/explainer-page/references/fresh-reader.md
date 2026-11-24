# Fresh Reader 점검

작성자와 문맥을 공유하지 않는 리뷰어가 페이지를 처음 읽는 독자로서 읽는다. 작성자가 스스로 점검하면 머릿속 맥락이 빈틈을 메워 버려 못 찾는다.

## 실행

1. 렌더링된 본문을 텍스트로 뽑는다. 닫힌 `<details>`도 읽히게 모두 연다. 그림은 텍스트에 캡션·안내 문장·조작부 이름으로만 남으니, 아래 스크립트가 함께 찍는 375px 전체 스크린샷도 리뷰어에게 준다.

   ```sh
   uv run --with playwright python - <<'PY' <폴더>/index.html <스크래치>/reader.png > <스크래치>/reader.txt
   import sys, pathlib
   from playwright.sync_api import sync_playwright
   with sync_playwright() as p:
       b = p.chromium.launch(); pg = b.new_page()
       pg.goto(pathlib.Path(sys.argv[1]).resolve().as_uri()); pg.wait_for_timeout(500)
       pg.eval_on_selector_all("details", "els => els.forEach(e => e.open = true)")
       print(pg.inner_text("body"))
       pg.set_viewport_size({"width": 375, "height": 800})
       pg.screenshot(path=sys.argv[2], full_page=True); b.close()
   PY
   ```

2. 작성 문맥을 넘기지 않는 새 서브에이전트를 띄운다. 독자 관점 리뷰어 타입(예: `egm:egm-comprehension`)이 있으면 그것을, 없으면 general-purpose를 쓴다. 프롬프트에는 아래 "리뷰어에게 주는 지시"와 `reader.txt`·`reader.png` 경로, 폴더 `CLAUDE.md`의 `## 독자 수준` 섹션 내용만 넣는다. 작성 의도·구성안·자료 요약은 주지 않는다.
3. 지적마다 고치거나, 고치지 않는 이유를 한 줄로 남긴다. 수정 뒤 1~2를 한 번 더 한다(최대 2회). 남은 지적은 최종 보고에 적는다.

## 리뷰어에게 주는 지시

당신은 아래 '독자 수준'에 적힌 지식만 가진 독자다. 페이지를 위에서부터 한 번 읽으며, 읽는 도중 멈칫한 곳을 모두 적는다. 문체 취향이나 칭찬은 적지 않는다.

찾을 것:

- 정의 전에 쓰인 용어, 또는 '모름' 개념인데 본문에서 풀리지 않은 것.
- 앞 문장에서 다음 문장으로 넘어갈 때 빠진 단계("그래서 왜?"가 떠오르는 곳).
- 왜 그 값인지 설명 없는 숫자, 꼬리표(`논문`/`계산`/`예시` 등)가 없는 숫자.
- 그림 안내만 읽고는 무엇을 보고 무엇을 조작해야 할지 모르는 곳.
- 섹션 제목(주장)이 섹션 내용으로 실제로 보여지지 않는 곳.
- 같은 개념을 다른 이름으로 불러 헷갈리는 곳.

형식: 한 줄에 하나. `[심각도: 막힘|헷갈림|사소] 위치(섹션 제목 또는 인용 몇 단어) — 무엇이 문제인지 — 독자로서 필요했던 것`. 마지막 줄에 "이 페이지를 다 읽고 한 문장으로 요약하면: …"을 쓴다. 요약이 페이지 첫 줄 요약과 다르면 그것도 지적이다.
