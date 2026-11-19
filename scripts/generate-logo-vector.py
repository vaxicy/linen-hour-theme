#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Linen Hour Theme — flat vector logo candidates (SVG, headless Chromium).

Style: **flat** — solid fills only, no gradients, no highlights, no outlines.
Two or three geometric shapes per mark; no plants, no ornaments.

The palette is four near-greys with almost no saturation, so a deep ink anchor
`#38332A` carries each composition and the palette tones only fill it. That is
the only way an icon stays legible on both the greige frame and the page.

Playwright screenshots each SVG cell with omit_background=True (true
transparency); PIL only composes the contact sheets, the inline strip and the
official logo/logo.png exported from SELECTED.

Colours come from manifest.json. Change SELECTED and re-run; never hand-copy PNGs.
"""
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
os.chdir(str(ROOT))                      # relative paths only (non-ASCII path safety)

SIZE = 128
CELL = 512
PREVIEW = 256
SELECTED = "01"
CAND_DIR = Path("logo/candidates")
LOGO_OUT = Path("logo/logo.png")

with open("manifest.json", "r", encoding="utf-8") as f:
    _m = json.load(f)
_C, _P = _m["theme"]["colors"], _m["theme"]["properties"]


def hx(vals):
    return "#%02X%02X%02X" % tuple(vals)


INK = hx(_C["ntp_text"])                           # #38332A
GREIGE = hx(_C["frame"])                           # #B7B09E
SAND = hx(_C["toolbar"])                           # #CFC6B1
LINEN = hx(_C["button_background"])                # #DED6C1
PARCHMENT = hx(_C["ntp_background"])               # #EBE2CC
BROWN = hx(_C["ntp_link"])                         # #6A5B48


def svg_open(body, defs=""):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
            'viewBox="0 0 256 256">%s<g transform="translate(128 128) scale(0.94) '
            'translate(-128 -128)">%s</g></svg>' % (CELL, CELL, defs, body))


def circle(cx, cy, r, fill):
    return '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r, fill)


def rrect(x, y, w, h, r, fill):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="%s"/>'
            % (x, y, w, h, r, fill))


# ------------------------------------------------------------------ candidates
SVG_01 = svg_open("""
%s
%s
""" % (rrect(52, 52, 152, 152, 18, INK),
       '<path d="M52 52 H204 L52 204 Z" fill="%s"/>' % PARCHMENT))

SVG_02 = svg_open("""
%s
%s
%s
""" % ('<path d="M48 60 H208 L140 130 L208 200 H48 L116 130 Z" fill="%s"/>' % INK,
       '<path d="M62 68 H128 L128 124 Z" fill="%s"/>' % LINEN,
       '<path d="M194 192 H128 L128 136 Z" fill="%s"/>' % SAND))

SVG_03 = svg_open("""
%s
%s
%s
%s
""" % (rrect(56, 56, 144, 144, 14, LINEN),
       rrect(68, 102, 120, 24, 8, INK),
       rrect(68, 150, 120, 24, 8, INK),
       '<path d="M104 62 H128 V194 H104 Z M156 62 H180 V194 H156 Z" fill="%s"/>' % GREIGE))

SVG_04 = svg_open("""
%s
%s
%s
%s
""" % (rrect(56, 150, 144, 44, 10, INK),
       rrect(68, 118, 120, 40, 10, GREIGE),
       rrect(80, 86, 96, 40, 10, LINEN),
       rrect(92, 54, 72, 40, 10, PARCHMENT)))

SVG_05 = svg_open("""
%s
%s
%s
""" % (circle(128, 128, 96, INK),
       '<path d="M32 150 a96 96 0 0 1 192 0 Z" fill="%s"/>' % PARCHMENT,
       rrect(32, 150, 192, 22, 0, SAND)))

SVG_06 = svg_open("""
%s
%s
""" % (circle(128, 128, 96, GREIGE),
       '<path d="M128 40 A88 88 0 0 1 216 128 L128 128 Z" fill="%s"/>' % PARCHMENT))

CANDIDATES = [
    ("01", "folded-sheet", "A folded square — one diagonal crease", SVG_01),
    ("02", "hourglass", "Hourglass silhouette with two palette fills", SVG_02),
    ("03", "weave", "Crossed bands like a linen weave", SVG_03),
    ("04", "paper-stack", "Four offset sheets, dark to light", SVG_04),
    ("05", "quiet-horizon", "Dark disc with a pale horizon and a sand line", SVG_05),
    ("06", "folded-disc", "A disc folded into two tones", SVG_06),
]


def font(size, bold=False):
    for name in (("segoeuib.ttf", "seguisb.ttf") if bold else ("segoeui.ttf", "segoeuisl.ttf")):
        p = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", name)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def render_cells():
    cells = "".join('<div id="cell%s" style="width:%dpx;height:%dpx">%s</div>' % (num, CELL, CELL, svg)
                    for num, _n, _d, svg in CANDIDATES)
    html = ('<!doctype html><html><head><meta charset="utf-8"><style>'
            'html,body{margin:0;padding:0;background:transparent}'
            '#grid{display:flex;flex-wrap:wrap;width:%dpx}div[id^=cell]{display:block}'
            '</style></head><body><div id="grid">%s</div></body></html>' % (CELL * 3, cells))
    out = {}
    with sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception:
            # bundled headless shell may be missing after a Playwright update
            b = p.chromium.launch(channel="chrome")
        pg = b.new_page(viewport={"width": CELL * 3, "height": CELL * 2})
        pg.set_content(html)
        for num, name, _d, _svg in CANDIDATES:
            path = CAND_DIR / ("%s-%s.png" % (num, name))
            pg.locator("#cell" + num).screenshot(path=str(path), omit_background=True)
            img = Image.open(path).convert("RGBA").resize((PREVIEW, PREVIEW), Image.LANCZOS)
            img.save(path)
            bbox = img.split()[3].getbbox()
            assert bbox, "candidate %s rendered empty" % name
            assert bbox[0] > 6 and bbox[1] > 6 and bbox[2] < PREVIEW - 6 and bbox[3] < PREVIEW - 6, \
                "candidate %s touches the canvas edge: %s" % (name, bbox)
            out[num] = img
            print("candidate %s %s -> alpha bbox %s" % (num, name, bbox))
        b.close()
    return out


def contact_sheet(rendered, bg, txt, sub, path, title):
    cols, rows = 3, 2
    cw, ch = 384, 374
    gap, margin = 28, 40
    W = margin * 2 + cols * cw + (cols - 1) * gap
    H = margin * 2 + 34 + rows * ch + (rows - 1) * gap
    sheet = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(sheet)
    f_title, f_name, f_desc, f_file = font(24, True), font(21, True), font(15), font(14)
    d.text((margin, margin), title, font=f_title, fill=txt)
    y0 = margin + 34
    for i, (num, name, desc, _svg) in enumerate(CANDIDATES):
        r, c = divmod(i, cols)
        x = margin + c * (cw + gap)
        y = y0 + r * (ch + gap)
        big = rendered[num].resize((220, 220), Image.LANCZOS)
        sheet.paste(big, (x + (cw - 220) // 2, y + 14), big)
        d.text((x + 18, y + 250), "%s · %s" % (num, name), font=f_name, fill=txt)
        d.text((x + 18, y + 280), desc, font=f_desc, fill=sub)
        thumb = rendered[num].resize((32, 32), Image.LANCZOS)
        sheet.paste(thumb, (x + 18, y + 330), thumb)
        d.text((x + 60, y + 339), "%s.png  256x256" % name, font=f_file, fill=sub)
        assert y + 300 <= y + 322, "text block collides with the thumbnail row"
    sheet.save(path)
    print("saved:", path, sheet.size)


def inline_strip(rendered, path):
    n, cell, gap, margin = len(CANDIDATES), 108, 22, 30
    W = margin * 2 + n * cell + (n - 1) * gap
    H = margin * 2 + cell + 30
    strip = Image.new("RGB", (W, H), PARCHMENT)
    d = ImageDraw.Draw(strip)
    f = font(15, True)
    for i, (num, _n, _d, _s) in enumerate(CANDIDATES):
        x = margin + i * (cell + gap)
        img = rendered[num].resize((cell, cell), Image.LANCZOS)
        strip.paste(img, (x, margin), img)
        d.text((x + cell // 2 - 8, margin + cell + 8), num, font=f, fill=INK)
    strip.save(path)
    print("saved:", path, strip.size)


def main():
    CAND_DIR.mkdir(parents=True, exist_ok=True)
    rendered = render_cells()
    contact_sheet(rendered, PARCHMENT, INK, (120, 110, 92),
                  CAND_DIR / "contact-light.png", "Linen Hour — flat candidates (parchment)")
    contact_sheet(rendered, GREIGE, INK, (90, 82, 68),
                  CAND_DIR / "contact-dark.png", "Linen Hour — candidates on the greige frame")
    inline_strip(rendered, CAND_DIR / "inline-strip.png")
    sel = [c for c in CANDIDATES if c[0] == SELECTED][0]
    icon = rendered[sel[0]].resize((SIZE, SIZE), Image.LANCZOS)
    icon.save(LOGO_OUT)
    print("official icon from SELECTED=%s (%s):" % (sel[0], sel[1]), LOGO_OUT, icon.size)


if __name__ == "__main__":
    main()
