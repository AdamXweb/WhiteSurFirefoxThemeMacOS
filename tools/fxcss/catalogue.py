#!/usr/bin/env python3
"""Build a browsable directory of the UI parts this theme can style.

For each landmark it resolves the real element in a live Firefox, crops its
region out of a screenshot, records the styles actually in effect, and greps
the theme for the rules that target it. The result is an HTML page answering
"what is this bit called, what does it look like, and which file do I edit?".

Everything here is measured from a running browser rather than assumed, so it
stays honest as Firefox changes: an element that no longer exists is reported
as missing instead of silently documented.
"""

import html
import json
import re
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Curated because an exhaustive dump of every node in browser.xhtml would be
# noise. These are the parts a theme actually targets.
LANDMARKS = [
    # area, slug, selector, name, description
    ("Toolbars", "nav-bar", "#nav-bar", "Navigation toolbar",
     "The main toolbar holding back/forward, the address bar and the right-hand buttons."),
    ("Toolbars", "tabs-toolbar", "#TabsToolbar", "Tab strip toolbar",
     "Container for the row of tabs. WhiteSur moves this below the nav bar, Safari-style."),
    ("Toolbars", "personal-toolbar", "#PersonalToolbar", "Bookmarks toolbar",
     "The bookmarks bar, shown here with three sample bookmarks."),
    ("Toolbars", "toolbar-menubar", "#toolbar-menubar", "Menu bar",
     "Hidden by default on macOS; on Windows this is the File/Edit/View strip."),

    ("Address bar", "urlbar", "#urlbar", "Address bar container",
     "The whole address bar, including its background, border and rounding."),
    ("Address bar", "urlbar-input", "#urlbar-input", "Address bar text field",
     "The editable text itself. Colour problems with typed URLs live here."),
    ("Address bar", "identity-box", "#identity-box", "Site identity block",
     "Padlock / permissions area at the left of the address bar."),
    ("Address bar", "star-button", "#star-button-box", "Bookmark star",
     "The bookmark-this-page control at the right of the address bar."),
    ("Address bar", "urlbar-results", "#urlbar-results", "Address bar dropdown",
     "Suggestion list shown while typing. Rendered inside the window, so it is themeable."),

    ("Tabs", "tabbrowser-tabs", "#tabbrowser-tabs", "Tab container",
     "Wraps every tab plus the new-tab button."),
    ("Tabs", "selected-tab", ".tabbrowser-tab[selected]", "Selected tab",
     "The active tab. Most tab colour work targets this."),
    ("Tabs", "pinned-container", "#pinned-tabs-container", "Pinned tabs container",
     "Holds pinned tabs; spacing here affects the join with normal tabs."),
    ("Tabs", "tab-close", ".tab-close-button", "Tab close button",
     "Per-tab close control. The install script can move it to the left."),
    ("Tabs", "newtab-button", "#tabs-newtab-button", "New tab button",
     "The + at the end of the tab strip."),

    ("Toolbar buttons", "back-button", "#back-button", "Back button", "Navigation back."),
    ("Toolbar buttons", "reload-button", "#reload-button", "Reload button", "Reload / stop."),
    ("Toolbar buttons", "firefox-view", "#firefox-view-button", "Firefox View button",
     "The leftmost control on the tab strip."),
    ("Toolbar buttons", "appmenu-button", "#PanelUI-menu-button", "App menu button",
     "The hamburger. Its panel is a native OS window and cannot be screenshotted."),
    ("Toolbar buttons", "extensions-button", "#unified-extensions-button", "Extensions button",
     "Unified extensions control."),
    ("Toolbar buttons", "account-button", "#fxa-toolbar-menu-button", "Account button",
     "Firefox Account menu."),

    ("Find bar", "findbar", "findbar", "Find bar",
     "Docked at the bottom of the content area when you press Ctrl/Cmd+F."),

    ("Content", "browser-stack", "#browser", "Content area",
     "Where the page renders. Styled by userContent.css rather than userChrome.css."),
]

COMPUTED_PROPS = [
    "background-color", "color", "border-radius", "border-top-width",
    "border-top-color", "box-shadow", "font-size", "padding-top", "margin-inline-end",
    "height", "opacity",
]

RESOLVE = """
const [landmarks, props] = arguments;
const win = Services.wm.getMostRecentWindow("navigator:browser");
const doc = win.document;
const out = [];
for (const [slug, selector] of landmarks) {
  let el = null;
  try { el = doc.querySelector(selector); } catch (e) {}
  if (!el) { out.push({slug, found: false}); continue; }
  const r = el.getBoundingClientRect();
  const cs = win.getComputedStyle(el);
  const styles = {};
  for (const p of props) { styles[p] = cs.getPropertyValue(p); }
  out.push({
    slug, found: true,
    tag: el.localName,
    id: el.id || null,
    classes: (typeof el.className === "string" ? el.className : "") || null,
    rect: {x: r.x, y: r.y, w: r.width, h: r.height},
    visible: r.width > 0 && r.height > 0,
    styles,
  });
}
return out;
"""


def css_references(repo: Path, selector: str):
    """Find where the theme styles this selector.

    Matches on the id or class token rather than the literal selector string,
    since a rule is far more likely to read `#urlbar[focused]` or
    `#nav-bar > .foo` than to repeat the selector verbatim.
    """
    token = selector.lstrip(".#[").split("[")[0].split(">")[0].strip()
    if not token:
        return []
    pattern = re.compile(r"(?<![\w-])[.#]?" + re.escape(token) + r"(?![\w-])")
    hits = []
    for path in sorted((repo / "chrome").rglob("*.css")):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for n, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("/*"):
                continue
            if pattern.search(line):
                hits.append({
                    "file": str(path.relative_to(repo)),
                    "line": n,
                    "text": stripped[:160],
                })
    return hits


def annotate(overview: Image.Image, items, dpr):
    """Draw numbered boxes over the overview screenshot."""
    img = overview.convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")
    try:
        font = ImageFont.load_default(size=int(15 * dpr))
    except TypeError:
        font = ImageFont.load_default()

    for idx, item in enumerate(items, 1):
        if not item.get("visible"):
            continue
        r = item["rect"]
        box = [r["x"] * dpr, r["y"] * dpr, (r["x"] + r["w"]) * dpr, (r["y"] + r["h"]) * dpr]
        if box[2] - box[0] < 2 or box[3] - box[1] < 2:
            continue
        draw.rectangle(box, outline=(255, 0, 128, 255), width=max(2, int(dpr)))
        draw.rectangle([box[0], box[1], box[0] + 26 * dpr, box[1] + 18 * dpr],
                       fill=(255, 0, 128, 235))
        draw.text((box[0] + 5 * dpr, box[1] + 2 * dpr), str(idx), fill=(255, 255, 255), font=font)
    return img


def crop(overview: Image.Image, rect, dpr, pad=8):
    x0 = max(0, int((rect["x"] - pad) * dpr))
    y0 = max(0, int((rect["y"] - pad) * dpr))
    x1 = min(overview.width, int((rect["x"] + rect["w"] + pad) * dpr))
    y1 = min(overview.height, int((rect["y"] + rect["h"] + pad) * dpr))
    if x1 - x0 < 4 or y1 - y0 < 4:
        return None
    piece = overview.crop((x0, y0, x1, y1))
    if piece.width > 760:
        piece = piece.resize((760, round(piece.height * 760 / piece.width)), Image.LANCZOS)
    return piece


def build(session, repo: Path, outdir: Path):
    from core import capture_views  # noqa: F401  (kept import-light)

    outdir.mkdir(parents=True, exist_ok=True)
    session.setup_window()
    # The find bar is created lazily, so it does not exist as an element until
    # opened. Open it before measuring or it would be reported as missing.
    import core as _core
    session.m.script(_core.OPEN_FINDBAR)
    time.sleep(1.2)
    session.m.script(_core.FILL_FINDBAR, ["whitesur"])
    time.sleep(0.6)

    info = session.info()
    dpr = info["dpr"]

    entries = {}
    for mode in ("light", "dark"):
        session.set_dark(mode == "dark")
        time.sleep(2.0)
        mode_dir = outdir / mode
        mode_dir.mkdir(exist_ok=True)

        import io
        overview = Image.open(io.BytesIO(session.m.screenshot()))
        resolved = session.m.script(
            RESOLVE, [[[l[1], l[2]] for l in LANDMARKS], COMPUTED_PROPS])
        by_slug = {r["slug"]: r for r in resolved}

        ordered = [by_slug[l[1]] for l in LANDMARKS if l[1] in by_slug]
        annotate(overview, ordered, dpr).save(mode_dir / "overview.png", optimize=True)

        for area, slug, selector, name, desc in LANDMARKS:
            item = by_slug.get(slug, {"slug": slug, "found": False})
            entry = entries.setdefault(slug, {
                "area": area, "slug": slug, "selector": selector,
                "name": name, "description": desc,
                "references": css_references(repo, selector),
                "modes": {},
            })
            shot = None
            if item.get("visible"):
                piece = crop(overview, item["rect"], dpr)
                if piece:
                    shot = f"{mode}/{slug}.png"
                    piece.save(mode_dir / f"{slug}.png", optimize=True)
            entry["modes"][mode] = {
                "found": item.get("found", False),
                "visible": item.get("visible", False),
                "styles": item.get("styles", {}),
                "shot": shot,
                "tag": item.get("tag"),
            }
        print(f"  {mode}: {sum(1 for r in resolved if r.get('visible'))}"
              f"/{len(LANDMARKS)} landmarks visible", flush=True)

    catalogue = {"info": info, "entries": list(entries.values())}
    (outdir / "catalogue.json").write_text(json.dumps(catalogue, indent=2), encoding="utf-8")
    (outdir / "index.html").write_text(render_html(catalogue), encoding="utf-8")
    return catalogue


PAGE_CSS = """
:root { color-scheme: light dark; --bg:#fff; --fg:#1c1c1e; --muted:#6b6b70;
        --line:#e3e3e6; --card:#fafafa; --accent:#315bef; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#1c1c1e; --fg:#f2f2f7; --muted:#9a9aa0; --line:#38383c;
          --card:#232326; --accent:#6f8dff; }
}
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--fg); font:15px/1.55 -apple-system,
       BlinkMacSystemFont,'Segoe UI',sans-serif; }
.wrap { max-width: 1080px; margin: 0 auto; padding: 32px 20px 80px; }
h1 { font-size: 28px; margin: 0 0 6px; letter-spacing: -0.02em; }
h2 { font-size: 13px; text-transform: uppercase; letter-spacing: .08em;
     color: var(--muted); margin: 40px 0 12px; }
.lede { color: var(--muted); margin: 0 0 28px; }
img { max-width: 100%; border-radius: 8px; border: 1px solid var(--line); display:block; }
.overview { margin-bottom: 8px; }
.tabs { display:flex; gap:8px; margin: 0 0 12px; }
.tabs button { font: inherit; padding: 6px 14px; border-radius: 999px; cursor: pointer;
   border: 1px solid var(--line); background: var(--card); color: var(--fg); }
.tabs button[aria-selected=true] { background: var(--accent); color:#fff; border-color:transparent; }
.card { border:1px solid var(--line); border-radius:12px; padding:16px 18px;
        margin-bottom:14px; background:var(--card); }
.card h3 { margin:0 0 2px; font-size:17px; }
.card .sel { font: 13px ui-monospace,SFMono-Regular,Menlo,monospace; color: var(--accent); }
.card p { margin:8px 0 12px; color: var(--muted); }
.styles { display:flex; flex-wrap:wrap; gap:6px; margin:10px 0 0; }
.chip { font: 12px ui-monospace,SFMono-Regular,Menlo,monospace; background:var(--bg);
        border:1px solid var(--line); border-radius:6px; padding:3px 8px; }
.sw { display:inline-block; width:10px; height:10px; border-radius:2px; margin-right:5px;
      border:1px solid rgba(128,128,128,.5); vertical-align:-1px; }
details { margin-top:10px; }
summary { cursor:pointer; color:var(--muted); font-size:13px; }
table { border-collapse:collapse; width:100%; margin-top:8px; font-size:13px; }
td { border-top:1px solid var(--line); padding:5px 8px; vertical-align:top; }
td.loc { white-space:nowrap; font: 12px ui-monospace,Menlo,monospace; color:var(--accent); }
td.src { font: 12px ui-monospace,Menlo,monospace; color:var(--muted); }
.missing { opacity:.55; }
.badge { font-size:11px; border:1px solid var(--line); border-radius:5px;
         padding:1px 6px; color:var(--muted); margin-left:8px; }
"""

PAGE_JS = """
function showMode(m) {
  document.querySelectorAll('[data-mode]').forEach(function (el) {
    el.hidden = el.dataset.mode !== m;
  });
  document.querySelectorAll('.tabs button').forEach(function (b) {
    b.setAttribute('aria-selected', String(b.dataset.set === m));
  });
}
document.addEventListener('DOMContentLoaded', function () { showMode('light'); });
"""


def _swatch(value):
    v = (value or "").strip()
    if v.startswith(("rgb", "#")) and "0, 0, 0, 0" not in v:
        return f'<span class="sw" style="background:{html.escape(v)}"></span>'
    return ""


def render_html(catalogue):
    info = catalogue["info"]
    parts = [
        "<!doctype html><meta charset=utf-8>",
        "<meta name=viewport content='width=device-width,initial-scale=1'>",
        "<title>WhiteSur — themeable UI directory</title>",
        f"<style>{PAGE_CSS}</style><div class=wrap>",
        "<h1>Themeable UI directory</h1>",
        f"<p class=lede>Measured live in Firefox {html.escape(str(info.get('version')))} "
        f"on {html.escape(str(info.get('os')))}. Each entry shows what the part looks "
        "like, the styles in effect, and which files in this repo style it.</p>",
        "<div class=tabs>"
        "<button data-set=light onclick=\"showMode('light')\">Light</button>"
        "<button data-set=dark onclick=\"showMode('dark')\">Dark</button></div>",
    ]
    for mode in ("light", "dark"):
        parts.append(f"<div data-mode={mode} hidden>"
                     f"<img class=overview src='{mode}/overview.png' "
                     f"alt='Annotated {mode} browser window'></div>")

    by_area = {}
    for e in catalogue["entries"]:
        by_area.setdefault(e["area"], []).append(e)

    for area, items in by_area.items():
        parts.append(f"<h2>{html.escape(area)}</h2>")
        for e in items:
            any_found = any(m["found"] for m in e["modes"].values())
            cls = "card" if any_found else "card missing"
            parts.append(f"<div class='{cls}'>")
            badge = "" if any_found else "<span class=badge>not present in this Firefox</span>"
            parts.append(f"<h3>{html.escape(e['name'])}{badge}</h3>")
            parts.append(f"<div class=sel>{html.escape(e['selector'])}</div>")
            parts.append(f"<p>{html.escape(e['description'])}</p>")

            for mode in ("light", "dark"):
                m = e["modes"].get(mode, {})
                parts.append(f"<div data-mode={mode} hidden>")
                if m.get("shot"):
                    parts.append(f"<img src='{m['shot']}' alt='{html.escape(e['name'])}'>")
                elif any_found:
                    parts.append("<p class=sel>present but not visible in this layout</p>")
                chips = []
                for prop, val in (m.get("styles") or {}).items():
                    if not val or val in ("none", "0px", "auto", "normal", "rgba(0, 0, 0, 0)"):
                        continue
                    chips.append(f"<span class=chip>{_swatch(val)}"
                                 f"{html.escape(prop)}: {html.escape(val)}</span>")
                if chips:
                    parts.append("<div class=styles>" + "".join(chips) + "</div>")
                parts.append("</div>")

            refs = e["references"]
            if refs:
                parts.append(f"<details><summary>{len(refs)} rule"
                             f"{'s' if len(refs) != 1 else ''} in this repo</summary><table>")
                for r in refs[:60]:
                    parts.append(
                        f"<tr><td class=loc>{html.escape(r['file'])}:{r['line']}</td>"
                        f"<td class=src>{html.escape(r['text'])}</td></tr>")
                if len(refs) > 60:
                    parts.append(f"<tr><td class=loc>…</td><td class=src>"
                                 f"and {len(refs) - 60} more</td></tr>")
                parts.append("</table></details>")
            else:
                parts.append("<details><summary>no rules in this repo target it"
                             "</summary><p>Styled by Firefox defaults only.</p></details>")
            parts.append("</div>")

    parts.append(f"</div><script>{PAGE_JS}</script>")
    return "\n".join(parts)
