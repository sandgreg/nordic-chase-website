# Nordic Chase website

Prototypes of the race pages on nordicchase.com, and the Squarespace Code Blocks that come out of them. Served with GitHub Pages so previews can be shared.

| Page | Preview | How to put it on Squarespace |
| --- | --- | --- |
| Chase 4 · Copenhagen → Stockholm | https://sandgreg.github.io/nordic-chase-website/cph-sto/ | [cph-sto/README.md](cph-sto/README.md) |

Copy and race facts live in Notion: [Website Content 2027](https://app.notion.com/p/415e6622429d810f93dbdec72febad36). Route maps live in [sandgreg/maps](https://github.com/sandgreg/maps).

## Update a page

1. Edit the copy in Notion.
2. Ask Claude to refresh the page from Notion (it rewrites `content/notion/*.md` and runs `python3 build.py`).
3. Commit and push to `main`. The preview updates in a minute or two.
