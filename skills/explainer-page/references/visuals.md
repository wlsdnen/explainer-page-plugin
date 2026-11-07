# 시각화와 영상 클립 규칙

## 무엇을 그리나

- 그림은 섹션의 주장을 독자가 직접 확인하게 하는 것이다. 장식용 그림은 넣지 않는다. 섹션당 그림 수 제한은 없다.
- 기본 표현은 자동 재생 애니메이션이고, 버튼은 재생/일시정지와 처음으로 두 개만 둔다.
- 슬라이더는 독자가 값을 바꿔 봐야 이해되는 경우에만 쓰고, 핵심 변수 1~2개로 제한한다.
- 구조도·흐름도 같은 정적 그림도 쓴다.
- 조작부가 있으면 기본값은 현상이 바로 보이는 값으로 둔다. 그림 아래에 "~하면 ~가 ~한다" 형식의 한 줄 안내를 단다.

## 기술 선택

| 대상 | 기술 |
|---|---|
| 일반 2D 그림 | 인라인 SVG |
| 마크가 수천 개 이상 | canvas |
| 공간·기하·고차원 구조(임베딩 공간, 텐서 모양, 손실 곡면) | three.js, 적극 사용 |

- 외부 라이브러리는 둘 중 하나로 부른다.
  - CDN: cdnjs 등에서 정확한 버전으로 고정한다(`three@latest` 같은 떠다니는 버전 금지).
  - Vendoring: 같은 버전 파일을 페이지 폴더 `vendor/`에 넣고 상대 경로로 부른다. 오프라인 열람이나 CDN 차단 환경이면 이쪽을 쓴다.
- three.js 예(ES 모듈, cdnjs). 쓰기 전에 그 URL이 HTTP 200인지 확인한다. cdnjs 배포본에는 `OrbitControls` 같은 addons가 없을 수 있으니, 회전 조작이 필요하면 포인터 이벤트로 카메라를 직접 돌리거나 addons를 vendoring한다.

```html
<script type="module">
import * as THREE from "https://cdnjs.cloudflare.com/ajax/libs/three.js/0.170.0/three.module.min.js";
</script>
```

- 색과 글자는 페이지의 CSS 변수에서만 가져온다. SVG 글자색도 CSS(`svg text`)로 변수를 쓰고 리터럴 색을 쓰지 않는다.
- 값을 담지 않은 장식, 그림자, 그라디언트는 쓰지 않는다.
- 375px에서 글자가 읽혀야 한다. 넓은 viewBox의 SVG는 폰 폭에서 절반 크기로 줄어드니 미디어 쿼리로 글자를 키운다.

## 애니메이션 기본형

`requestAnimationFrame` 루프에 재생/일시정지·처음으로 버튼을 붙이고, `prefers-reduced-motion`이면 멈춘 채 시작한다.

```html
<div data-widget><button id="play">일시정지</button> <button id="restart">처음으로</button></div>
<script>
const DURATION = 4000; // ms per loop
let t = 0, last = 0, playing = !matchMedia("(prefers-reduced-motion: reduce)").matches;
function draw(p) { /* p in [0, 1): update the SVG/canvas */ }
function frame(now) {
  if (playing) t = (t + (last ? now - last : 0)) % DURATION;
  last = now; draw(t / DURATION); requestAnimationFrame(frame);
}
const play = document.getElementById("play");
const sync = () => { play.textContent = playing ? "일시정지" : "재생"; };
play.onclick = () => { playing = !playing; sync(); };
document.getElementById("restart").onclick = () => { t = 0; };
sync(); requestAnimationFrame(frame);
</script>
```

## 영상 클립

- 이 절은 영상 자료에만 해당한다. 영상 소스가 있으면 설명 구간마다 클립을 잘라 해당 섹션에 넣는다.
- 출력 언어와 다른 영상은 출력 언어 자막(예: `.ko.vtt`)을 기본으로 표시한다. 번역은 원문 자막(`.en.vtt`)의 cue 번호·타이밍을 그대로 유지한다.
- ffmpeg로 자른다. 원본은 `media/`, 결과는 `clips/`에 둔다.

```sh
# 구간 클립 (재인코딩: 정확한 시작점, 웹 재생용)
ffmpeg -ss 00:12:30 -to 00:13:45 -i media/lecture.mp4 \
  -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k -movflags +faststart clips/s2-attention.mp4
# 포스터 이미지 (클립 첫 프레임)
ffmpeg -i clips/s2-attention.mp4 -frames:v 1 -q:v 3 clips/s2-attention.jpg
# 원본 자막(.srt)에서 같은 구간을 VTT로 잘라내기 (타임스탬프는 0부터 다시 시작)
ffmpeg -ss 00:12:30 -to 00:13:45 -i media/lecture.en.srt clips/s2-attention.en.vtt
```

  - `-ss`를 `-i` 앞에 두면 빠르게 찾아가고, 재인코딩하므로 시작점도 정확하다.
  - `.ko.vtt`는 `.en.vtt`를 복사해 cue 텍스트만 번역한다.
- 페이지에서는 `<video>`와 `<track>`을 직접 쓴다.

```html
<video controls preload="none" poster="clips/s2-attention.jpg" src="clips/s2-attention.mp4">
  <track kind="subtitles" srclang="ko" label="한국어" src="clips/s2-attention.ko.vtt" default>
  <track kind="subtitles" srclang="en" label="English" src="clips/s2-attention.en.vtt">
</video>
```

- mp4는 크기가 커서 git에 넣지 않는 편이 낫다(`.gitignore`에 `*.mp4`). 배포 때는 정적 호스팅이나 객체 스토리지에 올리고 `src`를 그 URL로 바꾼다. 영상 저작권과 재배포 허락을 먼저 확인한다.
