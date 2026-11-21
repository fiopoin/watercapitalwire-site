#!/usr/bin/env python3
"""Build watercapitalwire.com from content/*.json.

Usage: python3 tools/build.py   (the newest edition becomes the homepage)
Writes: index.html, archive/<date>.html, archive/index.html, method.html, privacy.html,
        feed.xml, sitemap.xml, robots.txt, llms.txt,
        social/<date>[-afternoon|-evening][-story].png, captions and social/today.json
"""
import json, glob, os, html, hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
from jinja2 import Environment, FileSystemLoader
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
env = Environment(loader=FileSystemLoader("templates"), autoescape=True)

editions = sorted(p for p in glob.glob("content/*.json") if os.path.basename(p)[:4].isdigit())
if not editions:
    raise SystemExit("no content files")
data = [json.load(open(p)) for p in editions]
latest = data[-1]
CFG = json.load(open("site.json")) if os.path.exists("site.json") else {}
_ga = "https://www.googletagmanager.com https://*.google-analytics.com https://*.analytics.google.com" if CFG.get("ga_id") else ""
CSP = (f"default-src 'self'; script-src 'self' {('https://www.googletagmanager.com' if _ga else '')}; style-src 'self' 'unsafe-inline'; "
       f"img-src 'self' data: {_ga}; font-src 'self'; connect-src 'self' {_ga}; object-src 'none'; "
       "base-uri 'self'; form-action 'self' mailto:; upgrade-insecure-requests").replace("  ", " ").replace(" ;", ";")
V = hashlib.md5("".join(open(f).read() for f in ["assets/style.css", "assets/app.js", "assets/ga.js"]).encode()).hexdigest()[:8]
os.makedirs("archive", exist_ok=True)
os.makedirs("social", exist_ok=True)

SITE = "https://watercapitalwire.com/"
NAME = "Water Capital Wire"
DESC = "A free daily read on the business of water for managers, investors and operators: capital, companies, technology, infrastructure and water security, with every fact sourced and dated."
ORG = {"@type": "NewsMediaOrganization", "@id": SITE + "#org", "name": NAME, "url": SITE,
       "logo": {"@type": "ImageObject", "url": SITE + "brand/wcw-icon-512.png", "width": 512, "height": 512},
       "description": DESC, "sameAs": CFG.get("same_as", [])}

def published(d):
    return datetime.strptime(d["date"] + " " + CFG.get("publish_time", "04:17"), "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo("America/Chicago")).isoformat()
def summary(d):
    t = d.get("social", {}).get("caption", "").split("\n")[0].strip() or d["lead"]["dek"]
    if len(t) > 300:
        t = t[:300].rsplit(". ", 1)[0] + "."
    return t
def page_url(d, archived):
    return SITE + (f"archive/{d['date']}.html" if archived else "")
def ld_for(d, archived):
    url = page_url(d, archived)
    art = {"@type": "NewsArticle", "@id": url + "#article", "headline": d["lead"]["headline"][:110],
           "description": summary(d), "url": url, "mainEntityOfPage": url,
           "image": [SITE + f"social/{d['date']}.png"], "datePublished": published(d), "dateModified": published(d),
           "inLanguage": "en-US", "isAccessibleForFree": True,
           "articleSection": [d["lead"]["kicker"]] + [b["sector"] for b in d.get("briefs", [])],
           "author": {"@id": SITE + "#org"}, "publisher": {"@id": SITE + "#org"}}
    graph = [ORG, art]
    ld = d.get("spotlight", {}).get("leader")
    if ld:
        graph.append({"@type": "Person", "name": ld["name"], "jobTitle": ld["role"]})
    if not archived:
        graph.append({"@type": "WebSite", "@id": SITE + "#site", "name": NAME, "url": SITE, "publisher": {"@id": SITE + "#org"}, "inLanguage": "en-US"})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False).replace("</", "<\\/")

page = env.get_template("page.html.j2")
common = dict(v=V, cfg=CFG, csp=CSP, site=SITE)
open("index.html", "w").write(page.render(d=latest, root="", archived=False, url=SITE, published=published(latest), desc=summary(latest), ld=ld_for(latest, False), **common))
for d in data:
    open(f"archive/{d['date']}.html", "w").write(page.render(d=d, root="../", archived=True, url=page_url(d, True), published=published(d), desc=summary(d), ld=ld_for(d, True), **common))

def simple(title, desc, canonical, body, root=""):
    hdr = env.get_template("header.html.j2").render(root=root)
    ftr = env.get_template("footer.html.j2").render(root=root, cfg=CFG)
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Content-Security-Policy" content="{CSP}"><meta name="referrer" content="strict-origin-when-cross-origin">
<title>{html.escape(title)} | {NAME}</title><meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{canonical}"><meta name="robots" content="index, follow"><meta name="theme-color" content="#0b1a2b"><link rel="icon" type="image/svg+xml" href="{root}brand/wcw-icon.svg"><link rel="stylesheet" href="{root}assets/style.css?v={V}"></head>
<body>{hdr}<main id="main" class="page"><div class="wrap">{body}</div></main>{ftr}</body></html>"""

items = "\n".join(f'<li><a href="{d["date"]}.html">{html.escape(d["date_long"])}</a><br><span>{html.escape(d["lead"]["headline"])}</span></li>' for d in reversed(data))
open("archive/index.html", "w").write(simple("Past editions", "Every Water Capital Wire edition, kept so readers can check what we reported against what happened.", SITE + "archive/",
    f'<h1>Past editions</h1><p class="intro">Every edition, kept so you can check what we reported against what happened next.</p><ul class="archive-list">{items}</ul>', root="../"))

open("method.html", "w").write(simple("How we work", "How Water Capital Wire sources news, data and profiles.", SITE + "method.html", """<div class="prose"><h1>How we work</h1>
<p>Water Capital Wire is a free daily edition on the business of water, written for managers, investors and operators. It covers water across every industry: utilities, industry and manufacturing, energy and produced water, agriculture, mining, semiconductors and data centers, along with the capital, technology, regulation and security questions that run through all of them.</p>
<h2>Down the pipe</h2><p>Every lead story is traced through the water cycle: source, treatment, use, reuse and discharge, because a contract or a rule rarely stops at one stage.</p>
<h2>Spotlights</h2><p>Each week we profile a company, a leader, a chemicals or technology supplier, an innovation and an investor, from filings, company statements and dated reporting. Profiles are not endorsements.</p>
<h2>Capital desk and watchlist</h2><p>Deals are listed with the date, the parties and the value when it is disclosed, each linked to its source. The watchlist names the listed companies and funds we follow. We show a price only when a source gives a dated close.</p>
<h2>The water atlas</h2><p>Water stress, demand, infrastructure needs, emerging sectors and security data come from public sources such as the World Resources Institute, the United Nations, the US EPA and the World Bank. Each figure is labeled with its source and refreshed when new data is published.</p>
<h2>Calculator and Water Pulse</h2><p>The project calculator runs in your browser; nothing you enter is sent anywhere. Its starting cases are illustrative inputs, not benchmarks. The Water Pulse self check and poll also run on your device only.</p>
<h2>Standards</h2><p>Every fact is linked to a dated source. We paraphrase and quote sparingly. Outlook lines are our reading and are labeled. Corrections are made in the archive. This is general information, not investment, legal or tax advice.</p></div>"""))

_ga_text = ("""<h2>Analytics</h2><p>We use Google Analytics 4 to count visits and learn which pages are useful. It records pages viewed, the referring site, general location and device type, and uses cookies to tell new visitors from returning ones.</p>"""
    if CFG.get("ga_id") else "<h2>Analytics</h2><p>We do not run analytics or tracking on this site. If we add visitor analytics, this page will say so first.</p>")
open("privacy.html", "w").write(simple("Privacy", "How Water Capital Wire handles visitor data.", SITE + "privacy.html",
    f"""<div class="prose"><h1>Privacy</h1><p>Last updated {latest['date_long']}.</p><p>Water Capital Wire is free to read. You do not need an account, and we do not sell, rent or share personal information.</p>{_ga_text}
<h2>Tools on the page</h2><p>The calculator, the Water Pulse self check and the poll run in your browser. The poll remembers your pick on your own device and sends nothing to us. The feedback box opens your own email app; we only see what you choose to send.</p>
<h2>Hosting</h2><p>The site is hosted on GitHub Pages, which keeps standard server logs, including IP addresses, for security. See <a href="https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages#data-collection">GitHub's note on data collection</a>.</p></div>"""))

def rfc822(ds):
    return datetime.strptime(ds, "%Y-%m-%d").replace(hour=10, minute=17).strftime("%a, %d %b %Y %H:%M:%S +0000")
entries = "".join(f"""<item><title>{html.escape(d['lead']['headline'])}</title><link>{page_url(d, True)}</link><guid>{page_url(d, True)}</guid>
<pubDate>{rfc822(d['date'])}</pubDate><description>{html.escape(summary(d))}</description><enclosure url="{SITE}social/{d['date']}.png" type="image/png" length="0"/></item>""" for d in reversed(data[-30:]))
open("feed.xml", "w").write(f"""<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{NAME}</title><link>{SITE}</link>
<description>{html.escape(DESC)}</description>{entries}</channel></rss>""")

urls = [(SITE, latest["date"], "daily", "1.0"), (SITE + "method.html", latest["date"], "monthly", "0.5"), (SITE + "archive/", latest["date"], "daily", "0.6")] \
    + [(page_url(d, True), d["date"], "monthly", "0.7") for d in reversed(data)] + [(SITE + "privacy.html", latest["date"], "yearly", "0.2")]
open("sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "\n".join(f"<url><loc>{u}</loc><lastmod>{m}</lastmod><changefreq>{c}</changefreq><priority>{p}</priority></url>" for u, m, c, p in urls) + "\n</urlset>\n")
bots = ["Googlebot", "Bingbot", "Applebot", "DuckDuckBot", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User",
        "anthropic-ai", "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended", "meta-externalagent", "Meta-ExternalFetcher",
        "FacebookBot", "CCBot", "Amazonbot", "cohere-ai"]
open("robots.txt", "w").write("# Water Capital Wire welcomes search engines and AI assistants.\n# Quote and link freely; please credit Water Capital Wire and link to watercapitalwire.com.\n\n"
    + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n")
L = [f"# {NAME}", "", f"> {DESC} Each edition has a lead story traced through the water cycle (source, treatment, use, reuse, discharge), briefs across the water economy, weekly spotlights on a company, a leader, a supplier, an innovation and an investor, a capital desk of deals and firms, a water atlas on stress, demand, infrastructure, emerging sectors and security, a watchlist of water equities, a project calculator and an events calendar. General information, not investment advice.", "",
     "## Today's edition", f"- [{latest['lead']['headline']}]({SITE}): {latest['date_long']}. {summary(latest)}"]
L += [f"- [{b['sector']}: {b['headline']}]({SITE}#{b['id']})" for b in latest.get("briefs", [])]
L += ["", "## About", f"- [How we work]({SITE}method.html)", f"- [Past editions]({SITE}archive/)", f"- [RSS feed]({SITE}feed.xml)", f"- [Sitemap]({SITE}sitemap.xml)", "", "## Recent editions"]
L += [f"- [{d['date_long']}: {d['lead']['headline']}]({page_url(d, True)})" for d in list(reversed(data))[:30]]
open("llms.txt", "w").write("\n".join(L) + "\n")

# Social graphics
NAVY, PAPER, MUTE, LINE = (11, 26, 43), (240, 245, 250), (160, 178, 198), (40, 62, 88)
BLUE, PURPLE, GREEN, ORANGE = (46, 155, 230), (154, 98, 220), (140, 198, 63), (233, 162, 59)
def F(name, s): return ImageFont.truetype(f"tools/fonts/{name}.ttf", s)
SERIF, SANS, SANSM, SANSB, SANSX = "newsreader-latin-700-normal", "archivo-latin-400-normal", "archivo-latin-600-normal", "archivo-latin-700-normal", "archivo-latin-800-normal"
lock = Image.open("brand/wcw-lockup-white-1200.png").convert("RGBA")
lock = lock.crop(lock.getbbox())
STAGES = (("SOURCE", "source", BLUE), ("TREAT", "treat", BLUE), ("USE", "use", PURPLE), ("REUSE", "reuse", PURPLE), ("DISCHARGE", "discharge", GREEN))

def wrap(dr, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if dr.textlength(t, font=font) <= width: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur)
    return lines

def card(d, s, W, H, path, pad=0, lead=False):
    im = Image.new("RGB", (W, H), NAVY); dr = ImageDraw.Draw(im); M = 84
    x0 = 0
    for frac, col in ((0.4, BLUE), (0.3, PURPLE), (0.3, GREEN)):
        dr.rectangle((x0, 0, x0 + int(W * frac), 14), fill=col); x0 += int(W * frac)
    lg = lock.resize((620, int(620 * lock.height / lock.width)), Image.LANCZOS); im.paste(lg, (M, M), lg)
    y = M + lg.height + 60 + pad
    dr.text((M, y), s["kicker"].upper(), font=F(SANSX, 34), fill=ORANGE); y += 64
    hf = F(SERIF, 96 if H > W * 1.5 else 86)
    if len(wrap(dr, s["headline"], hf, W - 2 * M)) > 3:
        hf = F(SERIF, 72)
    for line in wrap(dr, s["headline"], hf, W - 2 * M):
        dr.text((M, y), line, font=hf, fill=PAPER); y += int(hf.size * 1.06)
    y += 34
    seg = (W - 2 * M) // 5
    on = d["lead"].get("stages", []) if lead else []
    for i, (lab, key, col) in enumerate(STAGES):
        xs = M + i * seg
        dr.rectangle((xs, y, xs + seg - (10 if i < 4 else 0), y + 10), fill=col if (not lead or key in on) else LINE)
        dr.text((xs, y + 20), lab, font=F(SANSB, 22), fill=MUTE)
    y += 80
    pf = F(SANSM, 42)
    for p in s["points"]:
        dr.ellipse((M, y + 16, M + 18, y + 34), fill=BLUE)
        for line in wrap(dr, p, pf, W - 2 * M - 50):
            dr.text((M + 44, y), line, font=pf, fill=PAPER); y += 56
        y += 20
    if s.get("watch"):
        y += 14
        dr.text((M, y), "WHAT TO WATCH", font=F(SANSX, 30), fill=BLUE); y += 44
        wf = F(SANS, 37)
        for line in wrap(dr, s["watch"], wf, W - 2 * M):
            dr.text((M, y), line, font=wf, fill=PAPER); y += 50
    end = y
    foot = H - M - 96
    dr.line((M, foot, W - M - 136, foot), fill=LINE, width=2)
    dr.text((M, H - M - 70), d["date_long"], font=F(SANS, 28), fill=MUTE)
    dr.text((M, H - M - 32), "watercapitalwire.com", font=F(SANSB, 36), fill=PAPER)
    ring = Image.open("brand/wcw-icon-512.png").convert("RGBA").resize((112, 112), Image.LANCZOS)
    im.paste(ring, (W - M - 112, H - M - 108), ring)
    im.save(path, optimize=True)
    return end

def render_slot(d, s, base, lead=False):
    card(d, s, 1080, 1350, f"social/{base}.png", lead=lead)
    end = card(d, s, 1080, 1920, f"social/{base}-story.png", lead=lead)
    free = (1920 - 84 - 300) - end
    if free > 80:
        card(d, s, 1080, 1920, f"social/{base}-story.png", pad=free // 2, lead=lead)

for d in data:
    if "social" not in d: continue
    if d is latest or not os.path.exists(f"social/{d['date']}.png"):
        render_slot(d, d["social"], d["date"], lead=True)
        open(f"social/{d['date']}.txt", "w").write(d["social"]["caption"] + "\n")
        for slot, ss in d.get("social_slots", {}).items():
            render_slot(d, ss, f"{d['date']}-{slot}")
            open(f"social/{d['date']}-{slot}.txt", "w").write(ss["caption"] + "\n")

slots = {"morning": {"image": f"{SITE}social/{latest['date']}.png", "story": f"{SITE}social/{latest['date']}-story.png", "caption": latest["social"]["caption"]}}
for slot, ss in latest.get("social_slots", {}).items():
    slots[slot] = {"image": f"{SITE}social/{latest['date']}-{slot}.png", "story": f"{SITE}social/{latest['date']}-{slot}-story.png", "caption": ss["caption"]}
json.dump({"date": latest["date"], "slots": slots}, open("social/today.json", "w"), indent=1)
Image.open(f"social/{latest['date']}.png").save("social/latest.png")
print("built", latest["date"], "editions:", len(data))
