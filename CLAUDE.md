# watercapitalwire.com: Water Capital Wire

Static site on GitHub Pages (repo fiopoin/watercapitalwire-site, branch main, custom domain watercapitalwire.com via GoDaddy DNS). Same process as fiopoin.com, carbonenergynexus.com and uticamidstream.com.

## Who it is for
Managers and above, investors and operators who need a high level, sourced read on the business of water across every industry: utilities, industry and manufacturing, energy and produced water, agriculture, mining, semiconductors and data centers. Plain, direct, human prose; no hype.

## Build
- One JSON file per edition in `content/YYYY-MM-DD.json` (America/Chicago date); the newest becomes the homepage. Copy the latest file and replace every field that changed.
- `python3 tools/build.py` writes index.html, archive/, method.html, privacy.html, feed.xml, sitemap.xml, robots.txt, llms.txt and the social graphics (social/<date>.png, -story.png, -afternoon, -evening, captions, social/today.json). Never hand edit generated files; never block crawlers.
- Needs jinja2 and Pillow. Fonts: web fonts in assets/fonts (Archivo, Newsreader, OFL), TTF copies for graphics in tools/fonts. `tools/render_brand.py` re-renders brand PNGs (Playwright) only when brand SVGs change. `tools/make_qr.py` makes QR codes once social handles exist in site.json "follow".
- The CSP blocks inline scripts. Page behavior (countdown, calculator, Water Pulse, poll, feedback) lives in assets/app.js.

## Content schema
date, date_long, edition,
lead{kicker, stages[] subset of source|treat|use|reuse|discharge the story touches, headline (under 110 chars), dek, body[3], pipe{source,treat,use,reuse,discharge}, use[4]{who,text}, sources[]{name,url}},
briefs[4 to 6]{id, sector (Capital, Utilities, Industrial, Energy, Agriculture, Mining, Technology, Desalination, Reuse, Regulation, Security...), region, headline, text, why, sources[]}. Brief id "money" must exist; "world" should be a non-US story.
spotlight{company, leader, supplier, innovation, investor}:
  company/innovation/investor{week_of, name, headline, figs[2]{v,l}, body, sources[]};
  leader{week_of, name, role, figs[2], body, sources[]};
  supplier{week_of, name, kicker (what they sell), headline, figs[2], body[3], split[]{l,v} optional, why, sources[]}.
capital{intro, intro_source{name,url}, deals[6 to 8]{date, deal, who, value, source}, firm{name, type, base, headline, figs[2]{v,l}, body, sources[]} (one firm in focus)},
watchlist[]{ticker, name, seg, note} (feeds the rolling ticker under the masthead; keep notes under about 60 chars),
place{week_of, name, location, art (file in assets/art), headline, body[2], facts[3]{v,l}, visit, why, sources[]},
atlas{stress{title, intro, regions_label, regions[]{name,pct,note}, facts[3]{v,l}, hotspots, sources[]},
      demand{title, intro, pop[]{y,v}, facts[3]{v,l}, sources[]},
      infra{title, items[4]{v,l,s{name,url}}, note},
      sectors[4]{name, fig, l, line, s},
      security[3]{headline, text, s}},
events[]{when, year, name, where, url, pws? (true for Produced Water Society events), start? (ISO date, only on the first event for the countdown)},
social{kicker "Morning: the wire", headline, points[3], watch, caption},
social_slots{afternoon{kicker "Afternoon: the capital", ...}, evening{kicker "Evening: the world", ...}}.

## Daily rules
- Coverage: water across all industries, investment and capital (M&A, PE, VC, project finance, utility rate cases), innovation (academia and companies), applications (municipal, industrial, energy, agriculture, mining, chips, data centers, produced water), challenges (scarcity, PFAS and contaminants, aging pipes, workforce, floods and drought), water equities and funds, regulation (EPA, state agencies, EU, Gulf and Asian water authorities), desalination and reuse, water security and transboundary water. Global, with a US decision maker in mind.
- Prefer the most consequential and most read stories among equally solid ones. Every fact needs a dated, linked, reliable source. Never invent or estimate a number; leave out anything you cannot confirm. Paraphrase; at most one short quote per source.
- Spotlight cadence: company changes on Mondays, leader and supplier on Wednesdays, innovation on Thursdays, investor on Fridays (or the first edition after). Keep each unchanged until its day. Supplier is one chemicals or technology provider profiled in depth, never a list of names. Profiles come from public, sourced facts; no photos of people.
- Firm in focus (capital.firm): one VC, PE or infrastructure investor profiled in depth, changes on Fridays with the investor spotlight; never a list.
- Water place of the week (place): a notable water site, landmark or water tourism destination anywhere in the world; changes on Mondays. Art is an original SVG illustration drawn by us in assets/art (never copied photos). Facts from the operator or government sources.
- Capital desk: newest deals first; keep 6 to 8; drop items older than about six months when newer ones exist.
- Watchlist: keep the core names; update the "on our radar" note when news moves a name. Show prices only if a source gives a dated close (the template does not show prices yet).
- Atlas: evergreen reference data. Refresh a figure only when its source publishes new data (WRI Aqueduct, UN WWDR and WPP, EPA needs surveys, World Bank, IDRA, LBNL). Review monthly.
- Events: keep upcoming water events in date order, drop past ones, add new ones when announced (official site first). List every Produced Water Society event published on producedwatersociety.com/calendar (all regional editions) with pws: true. Put the ISO start date on the first event for the countdown.
- No em or en dashes as punctuation. Politically neutral. General information, not investment advice.
- Social: headline under 60 chars, points under 45, caption under 600 with 4 to 6 hashtags; caption first paragraph is the page description (under 300 chars). Morning post is the lead story for US decision makers; afternoon is the capital or company story; evening is the global story for the Middle East and Asia waking up.

## Brand
Navy masthead #0b1a2b, water blue #2E9BE6 (ink #1F6FD1), reclaimed purple #7A3CC2, green #8CC63F (ink #4F8F1F), orange accent #E9A23B. Logo (chosen by Raj, Nov 20, 2026): lowercase "wcw" in the style of the fiopoin ring logo; the first w blue, the second w green, the c a split ring (white or navy on top, blue below) with a blue drop inside and an orange dot at the opening. Profile picture is the ring alone. Files in brand/, social kit in brand/social/. Headline type Newsreader, everything else Archivo.

## Schedule (America/Chicago)
- Daily edition: 04:17.
- Social (three posts a day, planned Nov 20, 2026; handles to be created by Raj): morning "the wire" 08:02, afternoon "the capital" 15:12, evening "the world" 20:07.
- All four brands keep at least 60 minutes apart. Daily order: 05:37 CEN midday, 06:42 FIOPO morning, 08:02 WCW morning, 09:27 Utica, 11:42 FIOPO midday, 12:47 Utica, 13:47 CEN evening, 15:12 WCW afternoon, 16:37 Utica, 17:42 FIOPO evening, 20:07 WCW evening, 22:32 CEN morning.

## Publish and verify
Commit as user "fiopoin" (noreply@fiopoin.com) and push to main. Verify the live site (desktop and phone) after every update before reporting done.

## Search engines
- After every published edition is verified live, notify search engines with IndexNow: WebFetch https://api.indexnow.org/indexnow?url=https://watercapitalwire.com/&key=e019ee25d0dd7e28c5bb93051c3967f6 and then the same with url=https://watercapitalwire.com/archive/<date>.html. The key file `e019ee25d0dd7e28c5bb93051c3967f6.txt` at the site root must stay in place. A 200 or 202 reply means accepted; a failure here never blocks publishing.
- Google Search Console and Bing Webmaster Tools verification codes go in site.json (google_site_verification, bing_site_verification); the template prints them.
- The homepage title leads with the brand name; archive pages lead with the headline. Footers link the sister sites (FIOPO Intelligence, Carbon Energy Nexus, Utica Midstream).

- Never name the owner or FIOPO LLC anywhere on the site.
