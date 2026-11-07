# explainer-page

A Claude Code plugin with one skill, `explainer-page`: turn a paper, lecture video, code repository, or tech blog into an interactive, self-contained HTML explainer page.

The skill covers source checking, a reader-level interview, page structure, writing, visuals (SVG / canvas / three.js animations), video clips with subtitles, and verification. Output is a single `index.html` with inline CSS/JS and no build step; external libraries are either pinned CDN URLs or vendored files.

Default output language is **Korean**. Ask for another language (or set it in a project `CLAUDE.md`) and the skill adapts `lang`, fonts, and tone while keeping all other rules.

## Install

This folder is its own marketplace (`.claude-plugin/marketplace.json`).

```
/plugin marketplace add wlsdnen/explainer-page-plugin
/plugin install explainer-page@explainer-page-marketplace
```

Then ask, e.g., "이 논문 해설 페이지 만들어줘" or "make an interactive explainer page for this paper, in English".

## Requirements

- [uv](https://docs.astral.sh/uv/) for the page checker (Playwright is pulled in on demand).
- `ffmpeg` only if you cut video clips; Node only if a page has a `check.mjs`.

```sh
uv run --with playwright playwright install chromium
uv run --with playwright python skills/explainer-page/scripts/check_page.py --self-test
uv run --with playwright python skills/explainer-page/scripts/check_page.py path/to/index.html
```

## Layout

```
.claude-plugin/plugin.json        plugin manifest
.claude-plugin/marketplace.json   single-plugin marketplace
skills/explainer-page/SKILL.md    workflow and core rules
skills/explainer-page/references/ writing, visuals, style, verify
skills/explainer-page/scripts/check_page.py
```

## License

MIT. See [LICENSE](LICENSE).
