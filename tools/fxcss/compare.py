#!/usr/bin/env python3
"""Turn two sets of theme screenshots into before/after/diff images.

Reads a base/ and a head/ directory of PNGs produced by render.py, compares
each matching view, and writes one stacked comparison image per view that
changed, plus a summary.json describing what changed and by how much.

Views that render identically are reported but not drawn -- the point is to put
the reviewer's eye straight on the difference.

Usage:
    python3 compose.py --base base/ --head head/ --out out/ --platform macos
"""

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

# Width each panel is normalised to. GitHub renders comment images at roughly
# 800px, so this stays sharp without making the comment enormous.
PANEL_WIDTH = 960
LABEL_HEIGHT = 34
GAP = 10
# Per-channel difference below this is treated as noise (antialiasing, subpixel
# text rendering) rather than a real change.
NOISE_THRESHOLD = 24
HIGHLIGHT = (255, 0, 128)

FRIENDLY_NAMES = {
    "01-window": "Browser window",
    "02-urlbar": "Address bar focused",
    "03-findbar": "Find bar",
}


def load_font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # older Pillow: default font has no size argument
        return ImageFont.load_default()


def normalise(im, width=PANEL_WIDTH):
    im = im.convert("RGB")
    if im.width == width:
        return im
    height = round(im.height * width / im.width)
    return im.resize((width, height), Image.LANCZOS)


def diff_stats(base, head):
    """Return (changed_pixel_count, total, mask) ignoring sub-threshold noise."""
    delta = ImageChops.difference(base, head).convert("L")
    mask = delta.point(lambda v: 255 if v >= NOISE_THRESHOLD else 0)
    changed = mask.histogram()[255]
    return changed, base.width * base.height, mask


def render_diff_panel(base, mask):
    """Faded base image with changed regions painted in a hot highlight."""
    faded = Image.blend(base, Image.new("RGB", base.size, (255, 255, 255)), 0.72)
    overlay = Image.new("RGB", base.size, HIGHLIGHT)
    # Grow the mask slightly so single-pixel changes stay visible once scaled.
    from PIL import ImageFilter
    grown = mask.filter(ImageFilter.MaxFilter(5))
    return Image.composite(overlay, faded, grown)


def label_bar(width, text, bg, fg=(255, 255, 255)):
    bar = Image.new("RGB", (width, LABEL_HEIGHT), bg)
    draw = ImageDraw.Draw(bar)
    draw.text((12, LABEL_HEIGHT // 2), text, fill=fg, font=load_font(20), anchor="lm")
    return bar


def stack(panels, width):
    """Vertically stack (label, image) pairs onto one canvas."""
    height = sum(LABEL_HEIGHT + im.height + GAP for _, im in panels) + GAP
    canvas = Image.new("RGB", (width, height), (240, 241, 243))
    y = GAP
    for (text, bg), im in panels:
        canvas.paste(label_bar(width, text, bg), (0, y))
        y += LABEL_HEIGHT
        canvas.paste(im, (0, y))
        y += im.height + GAP
    return canvas


def compare_view(name, base_path, head_path, outdir):
    base = normalise(Image.open(base_path))
    head = normalise(Image.open(head_path))

    if base.size != head.size:
        # Different window heights between runs: pad the shorter one so the
        # comparison is still meaningful rather than failing outright.
        height = max(base.height, head.height)

        def pad(im):
            if im.height == height:
                return im
            padded = Image.new("RGB", (im.width, height), (255, 255, 255))
            padded.paste(im, (0, 0))
            return padded

        base, head = pad(base), pad(head)

    changed, total, mask = diff_stats(base, head)
    pct = 100.0 * changed / total if total else 0.0

    result = {
        "view": name,
        "title": FRIENDLY_NAMES.get(name.split("-", 1)[1], name),
        "mode": name.split("-", 1)[0],
        "changed_pixels": changed,
        "total_pixels": total,
        "percent": round(pct, 4),
        "image": None,
    }
    if changed == 0:
        return result

    comparison = stack(
        [
            (("BEFORE  ·  base branch", (90, 96, 104)), base),
            (("AFTER  ·  this PR", (32, 113, 62)), head),
            ((f"CHANGED  ·  {pct:.2f}% of pixels", (176, 21, 92)), render_diff_panel(base, mask)),
        ],
        base.width,
    )
    out_path = outdir / f"{name}.png"
    comparison.save(out_path, optimize=True)
    result["image"] = out_path.name
    return result


def run(base_dir: Path, head_dir: Path, out: Path, platform: str):
    out.mkdir(parents=True, exist_ok=True)

    base_shots = {p.stem: p for p in sorted(base_dir.glob("*.png"))}
    head_shots = {p.stem: p for p in sorted(head_dir.glob("*.png"))}
    shared = sorted(set(base_shots) & set(head_shots))

    summary = {
        "platform": platform,
        "views": [],
        "only_in_base": sorted(set(base_shots) - set(head_shots)),
        "only_in_head": sorted(set(head_shots) - set(base_shots)),
    }

    for name in shared:
        result = compare_view(name, base_shots[name], head_shots[name], out)
        summary["views"].append(result)
        state = "changed" if result["changed_pixels"] else "identical"
        print(f"  {name}: {state} ({result['percent']:.3f}%)", flush=True)

    # Always ship the head screenshots too, so a reviewer can see the whole UI
    # even when a change is subtle or when nothing differs at all.
    full_dir = out / "full"
    full_dir.mkdir(exist_ok=True)
    for name, path in head_shots.items():
        normalise(Image.open(path)).save(full_dir / f"{name}.png", optimize=True)

    summary["changed_views"] = [v for v in summary["views"] if v["changed_pixels"]]
    summary["any_change"] = bool(summary["changed_views"])

    src = head_dir / "render-info.json"
    if src.exists():
        summary["render_info"] = json.loads(src.read_text(encoding="utf-8"))

    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n{len(summary['changed_views'])} of {len(shared)} views changed on {platform}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", required=True, type=Path)
    ap.add_argument("--head", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--platform", required=True)
    args = ap.parse_args()
    return run(args.base, args.head, args.out, args.platform)


if __name__ == "__main__":
    sys.exit(main())
