# Nordic Chase website

Race page prototypes for nordicchase.com (Squarespace 7.1) and the Squarespace Code Blocks they produce. Hosted with GitHub Pages from `main` at `https://sandgreg.github.io/nordic-chase-website/`. Prototype pages carry `noindex`.

## Layout

- `content/notion/*.md`: snapshots of Notion pages, GENERATED. Never edit by hand. Source of truth is Notion: "Website Content 2027" (https://app.notion.com/p/415e6622429d810f93dbdec72febad36) under Nordic Chase HQ. One row per chase in the "Race Info 2027" database (fields = facts, page body = schedule, chapters, landmarks, where to sleep, good to know), plus the pages "What's included (entry page)" and "Sleeping on the road (shared block)".
- `src/race-page.html`: full prototype page. Sections that are native Squarespace blocks on the live site are imitated here with `proto-` styles.
- `src/stats-block.html`, `src/story-block.html`: the two Code Blocks. Self-contained: one `<section class="nc-...">`, scoped CSS (every rule under the section class, `!important` on buttons against Squarespace's global styles), own script, data inlined as JSON.
- `build.py`: reads the snapshots and templates, writes `<slug>/index.html` and `<slug>/blocks/*.html`. Pure Python 3, no packages.
- `site.json`: which chases to build, live map URL, and whether the preview uses `map-preview/`.
- `map-preview/`: a copy of a built map page from the maps repo branch, so the preview works before that branch is merged. Remove it and set `use_preview_map` to false once the maps changes are on `main`.

## Refreshing from Notion

1. Fetch the chase's row and the two shared pages with the Notion MCP tools (read only, never write to Notion).
2. Overwrite the matching `content/notion/*.md` with the fetched `<properties>` JSON and `<content>` markdown, keeping the header comment.
3. `python3 build.py`, check the result in a browser at 1440 px and 390 px, commit and push.

Use the copy word for word. Do not invent facts, names, prices or dates. British English, no em dashes.

## How the route story talks to the map

The story block embeds `https://sandgreg.github.io/maps/<slug>.html?mode=story` in an iframe and sends `postMessage`: `{type:'nc:edition', edition}`, `{type:'nc:goto', km, toKm}`, `{type:'nc:landmarks', items:[{name, km}]}`. The map answers `{type:'nc:ready'}`. Landmark positions are worked out on the route from the km. The Road/Gravel toggle in the stats block broadcasts a `nc:edition` CustomEvent on `document`; the story block listens and forwards it.

## Decisions worth keeping

- Only interactive sections are Code Blocks, so Greg can edit everything else in Squarespace.
- Brand palette: dark olive `#2E3104`, sage `#B8BC80`, lime `#D6FF3F`, pale yellow `#FFFDC1`, cream `#FEFFE9`; Schibsted Grotesk. Map chase colours stay as set in the maps repo.
- The pinned map uses `position: sticky`; if a Squarespace wrapper has `overflow` set (which breaks sticky), the script pins it with a transform instead. A fixed site header is detected and the map sits below it.
