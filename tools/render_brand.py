#!/usr/bin/env python3
"""Render brand SVGs to PNG with headless Chromium (run once after changing brand/*.svg).

Usage: python3 tools/render_brand.py
Writes: brand/wcw-icon-{32,180,512}.png, brand/wcw-lockup-white-1200.png, brand/wcw-lockup-navy-1200.png,
        brand/wcw-og.png and the social kit in brand/social/.
"""
import os, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
B = ROOT / "brand"
FONTS = (ROOT / "assets" / "fonts").as_uri()
NAVY = "#0b1a2b"
CSS = f"""<style>
@font-face{{font-family:'Archivo';font-weight:800;src:url({FONTS}/archivo-latin-800-normal.woff2)}}
@font-face{{font-family:'Archivo';font-weight:500;src:url({FONTS}/archivo-latin-500-normal.woff2)}}
html,body{{margin:0;padding:0;background:transparent}} svg{{display:block}}</style>"""

def shot(page, html, w, h, out, transparent=True):
    page.set_viewport_size({"width": w, "height": h})
    tmp = B / "_render.html"
    tmp.write_text(f"<!DOCTYPE html><html><head>{CSS}</head><body>{html}</body></html>")
    page.goto(tmp.as_uri())
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(200)
    page.screenshot(path=str(out), omit_background=transparent, clip={"x": 0, "y": 0, "width": w, "height": h})

def svg(name, w, h):
    return (B / name).read_text().replace("<svg ", f'<svg width="{w}" height="{h}" ', 1)

def lockup(dark, h):
    mark = "wcw-mark-white.svg" if dark else "wcw-mark.svg"
    col = "#FFFFFF" if dark else NAVY
    mw = int(h * 341 / 94)
    return (f'<div style="display:flex;align-items:center;gap:{int(h*0.32)}px">{svg(mark, mw, h)}'
            f'<span style="font:800 {int(h*0.52)}px Archivo;color:{col};letter-spacing:-.01em;white-space:nowrap">Water Capital Wire</span></div>')

with sync_playwright() as p:
    br = p.chromium.launch()
    pg = br.new_page()
    for n in (32, 180, 512):
        shot(pg, svg("wcw-icon.svg", n, n), n, n, B / f"wcw-icon-{n}.png", False)
    shot(pg, f'<div style="width:1200px;height:200px;display:flex;align-items:center">{lockup(True, 112)}</div>', 1200, 200, B / "wcw-lockup-white-1200.png")
    shot(pg, f'<div style="width:1200px;height:200px;display:flex;align-items:center">{lockup(False, 112)}</div>', 1200, 200, B / "wcw-lockup-navy-1200.png")
    os.makedirs(B / "social", exist_ok=True)
    for name, bg, ring in (("profile-navy", NAVY, "wcw-ring-white.svg"), ("profile-white", "#FFFFFF", "wcw-ring.svg")):
        shot(pg, f'<div style="width:800px;height:800px;background:{bg};display:flex;align-items:center;justify-content:center">{svg(ring, 520, 520)}</div>', 800, 800, B / "social" / f"{name}-800.png", False)
    def cover(w, h, lh, name, center=False, tagline=True):
        stripe = max(8, h // 50)
        tg = (f'<div style="font:500 {int(lh*0.36)}px Archivo;color:#c9d6e6;margin-top:{int(lh*0.28)}px">'
              'Water business news for decision makers</div>') if tagline else ""
        pos = "left:50%;transform:translate(-50%,-50%)" if center else f"left:{int(w*0.06)}px;transform:translateY(-50%)"
        html = (f'<div style="width:{w}px;height:{h}px;background:{NAVY};position:relative;overflow:hidden">'
                f'<div style="position:absolute;left:0;right:0;bottom:0;height:{stripe}px;background:linear-gradient(90deg,#2e9be6 0 40%,#7a3cc2 40% 70%,#8cc63f 70%)"></div>'
                f'<div style="position:absolute;top:50%;{pos}">{lockup(True, lh)}{tg}</div></div>')
        shot(pg, html, w, h, B / "social" / f"{name}.png", False)
    cover(1500, 500, 90, "x-header-1500x500")
    cover(1640, 624, 100, "facebook-cover-1640x624")
    cover(2256, 382, 90, "linkedin-cover-1128x191@2x", center=True, tagline=False)
    cover(1200, 630, 72, "og-1200x630")
    br.close()
os.replace(B / "social" / "og-1200x630.png", B / "wcw-og.png")
(B / "_render.html").unlink(missing_ok=True)
print("brand rendered")
