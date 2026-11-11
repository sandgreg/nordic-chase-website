#!/usr/bin/env python3
"""Build the Nordic Chase race page prototypes from the Notion snapshot.

Usage:  python3 build.py [slug ...]        (default: every chase in site.json)

Reads:
  content/notion/<slug>.md                 the chase's row in Notion "Race Info 2027" (generated, do not edit)
  content/notion/whats-included.md         shared "What's included" page (generated)
  content/notion/sleeping-on-the-road.md   shared "Sleeping on the road" page (generated)
  src/*.html                               page and block templates
  site.json                                map URLs and which chases to build

Writes, per chase:
  <slug>/index.html                        the full prototype page (preview only, noindex)
  <slug>/blocks/02-stats.html              Squarespace Code Block: stats bar + Road/Gravel toggle
  <slug>/blocks/04-route-story.html        Squarespace Code Block: scroll story with the map

Pure Python 3, no packages needed.
"""
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
NOTION = ROOT / "content" / "notion"


# ---------- Notion markdown snapshot -> data ----------

def read_snapshot(path):
    src = path.read_text(encoding="utf-8")
    props = {}
    m = re.search(r"<properties>\s*(\{.*?\})\s*</properties>", src, re.S)
    if m:
        props = json.loads(m.group(1))
    body = re.search(r"<content>\n?(.*?)</content>", src, re.S).group(1)
    return props, parse_blocks(body)


def parse_blocks(body):
    """Split Notion-flavoured markdown into sections: {heading: [blocks]}; '' holds text before the first heading.
    A block is ("p", text) | ("ul", [items]) | ("table", [[cells], ...])."""
    sections, cur = {"": []}, ""
    lines = body.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith("## "):
            cur = strip_tags(line[3:]).strip()
            sections[cur] = []
        elif line.startswith("<table"):
            j = i
            while not lines[j].startswith("</table>"):
                j += 1
            sections[cur].append(("table", parse_html_table("\n".join(lines[i:j + 1]))))
            i = j
        elif line.startswith("| "):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split(" | ")]
                if not all(set(c) <= set("-: ") for c in cells):
                    rows.append(cells)
                i += 1
            sections[cur].append(("table", rows))
            continue
        elif line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(lines[i][2:].strip())
                i += 1
            sections[cur].append(("ul", items))
            continue
        elif line.strip() and line.strip() != "<p />":
            sections[cur].append(("p", line.strip()))
        i += 1
    return sections


def parse_html_table(src):
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", src, re.S):
        rows.append([c.strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)])
    return rows


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


def inline(s):
    """Notion inline markdown -> safe HTML (bold, links, escapes)."""
    s = s.replace("\\~", "~").replace("\\|", "|")
    out = html.escape(s, quote=False)
    out = re.sub(r"&lt;(/?)b&gt;", r"<\1strong>", out)
    out = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                 lambda m: f'<a href="{html.escape(m.group(2))}" target="_blank" rel="noopener">{m.group(1)}</a>', out)
    return out.strip().rstrip(",").strip()


def km_range(s):
    m = re.match(r"\s*(\d+)\s*[–-]\s*(\d+)", s or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def num_or_none(s):
    s = (s or "").strip()
    return int(s) if s.isdigit() else None


def long_date(iso):
    d = date.fromisoformat(iso)
    return f"{d.strftime('%A')} {d.day} {d.strftime('%B')} {d.year}"


def fmt_int(n):
    return f"{int(n):,}" if n is not None else ""


# ---------- data model ----------

def chase_data(slug):
    props, sec = read_snapshot(NOTION / f"{slug}.md")
    editions = [e.lower() for e in props.get("Editions", ["Road"])]
    field = props.get("Field size", "")

    def field_for(ed):
        m = re.search(r"(\d+)\s*" + ed, field, re.I)
        return f"{m.group(1)} riders" if m else field

    stats = {}
    for ed in editions:
        E = ed.capitalize()
        stats[ed] = {
            "distance": f"{fmt_int(props.get(f'{E} km'))} km",
            "elevation": f"{fmt_int(props.get(f'{E} elevation m'))} m",
            "high": f"{fmt_int(props.get(f'{E} high point m'))} m",
            "ferries": str(fmt_int(props.get(f"Ferries {ed}"))),
            "cutoff": f"{fmt_int(props.get('Cut-off h'))} h",
            "field": field_for(ed),
        }

    chapters = []
    for row in next((b[1] for b in sec.get("Chapters", []) if b[0] == "table"), [])[1:]:
        no, title, road, gravel, text = row
        chapters.append({"no": int(no), "title": strip_tags(title), "text": inline(text),
                         "km": {"road": km_range(road), "gravel": km_range(gravel)}})

    landmarks = []
    lm_key = next((k for k in sec if k.startswith("Landmarks")), None)
    for row in next((b[1] for b in sec.get(lm_key, []) if b[0] == "table"), [])[1:]:
        landmarks.append({"name": strip_tags(row[0]).replace("\\|", "|"),
                          "km": {"road": num_or_none(row[1]), "gravel": num_or_none(row[2]) if len(row) > 2 else None}})

    title_parts = props["Chase"].split(" · ", 1)
    return {
        "slug": slug, "props": props, "sections": sec, "editions": editions,
        "tag": title_parts[0], "name": title_parts[-1],
        "stats": stats, "chapters": chapters, "landmarks": landmarks,
    }


# ---------- rendering ----------

def render_blocks(blocks):
    out = []
    for kind, val in blocks:
        if kind == "p":
            out.append(f"<p>{inline(val)}</p>")
        elif kind == "ul":
            out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in val) + "</ul>")
        elif kind == "table":
            head, *rows = val
            out.append('<div class="proto-table"><table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in head)
                       + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
                       + "</tbody></table></div>")
    return "\n".join(out)


def fill(tpl, **kw):
    for k, v in kw.items():
        tpl = tpl.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{[a-z_]+\}\}", tpl)
    assert not left, f"unfilled placeholders: {left}"
    return tpl


def build(slug, site):
    c = chase_data(slug)
    p = c["props"]
    inc_props, inc = read_snapshot(NOTION / "whats-included.md")
    _, sleep = read_snapshot(NOTION / "sleeping-on-the-road.md")

    stats_data = {"editions": c["editions"], "stats": c["stats"]}
    story_data = {
        "slug": slug, "editions": c["editions"],
        "chapters": [{"no": ch["no"], "km": ch["km"]} for ch in c["chapters"]],
        "landmarks": c["landmarks"],
    }

    chapter_cards = "\n".join(
        f'''      <article class="nc-story-card" data-i="{i}">
        <p class="nc-story-no">Chapter {ch["no"]}</p>
        <h3>{html.escape(ch["title"])}</h3>
        <p class="nc-story-km" data-road="{'km %d–%d' % ch['km']['road'] if ch['km'].get('road') else ''}" data-gravel="{'km %d–%d' % ch['km']['gravel'] if ch['km'].get('gravel') else ''}">{'km %d–%d' % ch['km'][c['editions'][0]]}</p>
        <p class="nc-story-text">{ch["text"]}</p>
        <ul class="nc-story-lm"></ul>
      </article>''' for i, ch in enumerate(c["chapters"]))

    tpl_stats = (ROOT / "src" / "stats-block.html").read_text(encoding="utf-8")
    tpl_story = (ROOT / "src" / "story-block.html").read_text(encoding="utf-8")
    tpl_page = (ROOT / "src" / "race-page.html").read_text(encoding="utf-8")

    first = c["stats"][c["editions"][0]]
    stats_block = fill(tpl_stats, data=json.dumps(stats_data, ensure_ascii=False),
                       toggle_hidden="" if len(c["editions"]) > 1 else " hidden",
                       **{f"s_{k}": html.escape(v) for k, v in first.items()})

    def story_block(map_base):
        return fill(tpl_story, data=json.dumps(story_data, ensure_ascii=False),
                    map_src=html.escape(f"{map_base}{slug}.html?mode=story"),
                    name=html.escape(c["name"]), cards=chapter_cards)

    # shared copy
    sleep_html = render_blocks(sleep[""])
    included_short = next((b for b in inc.get("Short version (for route pages)", []) if b[0] == "ul"), ("ul", []))
    inc_hook = next((strip_tags(t).replace("Hook:", "").strip() for k, t in inc[""] if k == "p" and "Hook:" in t), "")
    inc_intro = next((inline(strip_tags(t).replace("Intro:", "").strip()) for k, t in inc[""] if k == "p" and "Intro:" in t), "")

    page = fill(
        tpl_page,
        title=html.escape(f"{c['tag']}: {c['name']} | Nordic Chase (prototype)"),
        tag=html.escape(c["tag"]),
        name_from=html.escape(c["name"].split(" → ")[0]),
        name_to=html.escape(c["name"].split(" → ")[-1]),
        briefing=html.escape(long_date(p["date:Rider briefing:start"])) if p.get("date:Rider briefing:start") else "",
        start=html.escape(long_date(p["date:Race start:start"])),
        start_venue=html.escape(p.get("Start venue", "")),
        finish=html.escape(p.get("Finish", "")),
        hook=html.escape(p.get("Hook", "")),
        intro=html.escape(p.get("Intro", "")),
        schedule=render_blocks(c["sections"].get("Schedule", [])),
        stats_block=stats_block,
        story_block=story_block(site["map_base_preview"] if site.get("use_preview_map") else site["map_base_live"]),
        sleep=render_blocks(c["sections"].get("Where to sleep", [])),
        sleep_shared=sleep_html,
        good_to_know=render_blocks(c["sections"].get("Good to know", [])),
        inc_hook=html.escape(inc_hook),
        inc_intro=inc_intro,
        inc_list=render_blocks([included_short]),
        inc_extras=render_blocks(inc.get("Optional extras", [])),
        inc_not=render_blocks(inc.get("Not included", [])),
        notion_url=html.escape(p.get("url", "https://app.notion.com/p/415e6622429d810f93dbdec72febad36")),
    )

    out = ROOT / slug
    (out / "blocks").mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page, encoding="utf-8")
    header = "<!-- Nordic Chase {what}. Paste this whole file into a Squarespace Code Block.\n     Generated by build.py from Notion; edit the copy in Notion, not here. -->\n"
    (out / "blocks" / "02-stats.html").write_text(header.format(what="stats bar + Road/Gravel toggle") + stats_block, encoding="utf-8")
    (out / "blocks" / "04-route-story.html").write_text(header.format(what="route story (scroll + map)") + story_block(site["map_base_live"]), encoding="utf-8")
    print(f"{slug}: {len(c['chapters'])} chapters, {len(c['landmarks'])} landmarks, editions {', '.join(c['editions'])} -> {slug}/")


def main():
    site = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
    for slug in sys.argv[1:] or site["chases"]:
        build(slug, site)


if __name__ == "__main__":
    main()
