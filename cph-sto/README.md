# CPH–STO race page: how to put it on Squarespace

Preview: https://sandgreg.github.io/nordic-chase-website/cph-sto/ (not indexed by Google).

The page has seven sections. Two are Code Blocks; the rest are normal Squarespace blocks, so you can edit them like any page.

| # | Section | Build it with | Copy comes from (Notion) |
| --- | --- | --- | --- |
| 1 | Hero | Image block + text block + button block (Register → /register) | Race Info 2027: Chase, Hook, Rider briefing, Race start, Start venue, Finish |
| 2 | Stats bar + Road/Gravel toggle | **Code Block**: paste `blocks/02-stats.html` | Race Info 2027 fields (km, elevation, high point, ferries, cut-off, field size) |
| 3 | Intro + schedule | Two text blocks side by side | Intro field; Schedule section in the page body |
| 4 | Route story (scroll + map) | **Code Block**: paste `blocks/04-route-story.html` | Chapters and Landmarks tables in the page body |
| 5 | Where to sleep | Accordion block, item 1 | Where to sleep table + the "Sleeping on the road" page |
| 6 | Good to know | Accordion block, item 2 | Good to know section |
| 7 | What's included | Text blocks + button block; background colour pale yellow `#FFFDC1` | "What's included" page: hook, intro, short version, optional extras, not included |

## Pasting the Code Blocks

1. Give sections 2 and 4 their own Squarespace section each, and set both to full width.
2. Add a Code Block, set it to HTML, turn off "Display source", paste the whole file.
3. Paste section 2 above section 4. The toggle in section 2 switches the route story too. Each block also works on its own (Road by default).

Before pasting `04-route-story.html`, the maps branch `gravel-and-story` must be merged in the maps repo. The block loads the map from `https://sandgreg.github.io/maps/cph-sto.html`, and the story controls only exist after that merge.

## Changing the text

- Edit Notion, then ask Claude to "refresh the CPH–STO page from Notion". That rebuilds the preview and both block files; paste the changed block files again.
- Chapter text sits inside `04-route-story.html`, one `<article class="nc-story-card">` per chapter, if you ever need a quick fix directly in Squarespace. The next rebuild from Notion overwrites it, so fix Notion too.
- Native sections (1, 3, 5, 6, 7) you edit directly in Squarespace. Keep Notion in step so the next page build matches.

## Colours

Dark olive `#2E3104`, sage `#B8BC80`, lime `#D6FF3F`, pale yellow `#FFFDC1`, cream `#FEFFE9`. Font: Schibsted Grotesk (site-wide). The map keeps its own dark basemap and orange route.
