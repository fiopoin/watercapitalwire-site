#!/usr/bin/env python3
"""Make QR codes for the social profiles listed in site.json "follow" (and the site itself).

Usage: python3 tools/make_qr.py   -> brand/qr/<key>.svg and brand/qr/<key>.png (1000 px, print ready)
"""
import json, os, segno
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
cfg = json.load(open("site.json"))
dark = cfg.get("qr_dark", "#111111")
os.makedirs("brand/qr", exist_ok=True)
items = list(cfg.get("follow", [])) + [{"key": "website", "name": "Website", "url": cfg["site_url"]}]
for it in items:
    q = segno.make(it["url"], error="q")
    q.save(f"brand/qr/{it['key']}.svg", scale=10, border=2, dark=dark, light="#FFFFFF", xmldecl=False, svgns=True, title=f"{it['name']} QR code")
    q.save(f"brand/qr/{it['key']}.png", scale=max(1, 1000 // (q.symbol_size(border=2)[0])), border=2, dark=dark, light="#FFFFFF")
    print(it["key"], it["url"])
