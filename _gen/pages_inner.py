#!/usr/bin/env python3
"""Inner page builders: service, services index, areas, about, contact, legal."""
from __future__ import annotations
import re
from mdutil import (
    AREA_META, BRAND, BRAND_MARK, CITY, PHONE_DISPLAY, PHONE_TEL, NAV_SERVICES, phone_nowrap_html,
    esc, inline_md, paragraphs, find_section, extract_faqs, checklist_from_blocks,
    parse_ol_steps, all_list_items, first_paragraph, blocks_to_html, phone_sub,
)
from chrome import (
    shell_page, trust_strip, faq_section, cta_band, contact_section,
    placeholder, process_section, location_hero, related_services,
)

DETAIL_FILES = [
    "shared-detail-extraction",
    "shared-detail-removal",
    "shared-detail-disinfect",
    "shared-detail-drying",
]

CARD_MAP = {
    "sewage-backup-cleanup": "shared-card-backup",
    "emergency-sewage-cleanup": "shared-card-emergency",
    "toilet-overflow-cleanup": "shared-card-toilet",
}


def build_service(doc: dict, meta: dict, url: str) -> str:
    page = url.strip("/").replace("/", "-") or "service"
    sections, faqs = extract_faqs(doc["sections"])
    title = doc["title"] or meta.get("title_tag", "Service")
    intro_paras = paragraphs(doc["intro"])
    lead = ""
    for p in intro_paras:
        if len(p) > 60 and (not p.strip().startswith("**") or p.count("**") >= 2):
            lead = re.sub(r"^\*\*[^*]+\*\*\s*", "", p)
            if len(lead) > 40:
                break
    if not lead and intro_paras:
        lead = re.sub(r"^\*\*[^*]+\*\*\s*", "", intro_paras[-1])

    short = title.split(" in ")[0] if " in " in title else title
    hero = location_hero(
        title, lead or (intro_paras[0] if intro_paras else ""),
        [("/", "Home"), ("/services/", "Services"), ("", short)],
        "Category 3 sewage cleanup", page,
    )

    about_sec = sections[0] if sections else None
    about_blocks = about_sec["blocks"] if about_sec else doc["intro"]
    about_h2 = about_sec["heading"] if about_sec else f"Understanding {short}"
    about_paras = paragraphs(about_blocks) or intro_paras
    checks = checklist_from_blocks(about_blocks, 4) or [
        "Containment & PPE", "Full extraction", "EPA-registered disinfection", "Structural drying",
    ]
    about_html = f'''<section class="section about-section">
      <div class="shell split-layout">
        <div class="image-stack">{placeholder("Service detail photo", "shared-portrait", page, f"{title} work in progress", "4:5", "420px")}<div class="image-caption">Careful work. Honest options.</div></div>
        <div class="section-copy">
          <span class="eyebrow"><span></span> About this service</span>
          <h2>{esc(about_h2)}</h2>
          <p class="lead">{inline_md(about_paras[0] if about_paras else lead)}</p>
          {"".join(f"<p>{inline_md(p)}</p>" for p in about_paras[1:3])}
          <ul class="check-list">{"".join(f'<li><span>✓</span> <span class="check-text">{inline_md(c)}</span></li>' for c in checks)}</ul>
          <div class="signature-row signature-row-cta"><a class="button button-primary" href="tel:{PHONE_TEL}" style="margin:0;">Call <span class="phone-nowrap">{PHONE_DISPLAY}</span> <span>→</span></a></div>
        </div>
      </div>
    </section>'''

    includes_sec = find_section(sections, "includes") or find_section(sections, "what our") or find_section(sections, "signs")
    include_items = []
    if includes_sec:
        include_items = parse_ol_steps(includes_sec["blocks"])
        if not include_items:
            for it in all_list_items(includes_sec["blocks"])[:6]:
                m = re.match(r"\*\*([^*]+)\*\*:?\s*(.*)", it)
                include_items.append((m.group(1), m.group(2) or m.group(1)) if m else (it[:50], it))
    if not include_items:
        for sec in sections[1:3]:
            include_items = parse_ol_steps(sec["blocks"]) or [(it[:50], it) for it in all_list_items(sec["blocks"])[:4]]
            if include_items:
                includes_sec = sec
                break
    why_html = ""
    if include_items:
        cards = "".join(
            f'<article><span class="benefit-number">{i:02d}</span><div class="mini-icon">✓</div><h3>{inline_md(n)}</h3><p>{inline_md(d)}</p></article>'
            for i, (n, d) in enumerate(include_items[:6], 1)
        )
        why_html = f'''<section class="section why-section">
      <div class="shell">
        <div class="section-heading centered"><span class="eyebrow"><span></span> What's included</span><h2>{esc(includes_sec["heading"] if includes_sec else "What's Included")}</h2><p>Clear steps so you know what happens on site.</p></div>
        <div class="benefit-grid">{cards}</div>
      </div>
    </section>'''

    proc_sec = find_section(sections, "process") or find_section(sections, "how") or find_section(sections, "before we")
    steps = parse_ol_steps(proc_sec["blocks"]) if proc_sec else []
    if not steps:
        steps = [
            ("Inspect & map moisture", "Find the full spread under floors and inside walls."),
            ("Contain & extract", "Seal the zone and remove standing sewage."),
            ("Remove & disinfect", "Pull porous materials and sanitize what remains."),
            ("Dry & restore", "Dry to target moisture, then rebuild as needed."),
        ]
    process_html = process_section(proc_sec["heading"] if proc_sec else "How This Service Works", steps[:5], page)

    detail_secs = [s for s in sections if s is not about_sec and s is not includes_sec and s is not proc_sec]
    details_html = ""
    if detail_secs:
        rows = []
        for i, sec in enumerate(detail_secs[:3]):
            paras = paragraphs(sec["blocks"])
            reverse = " city-service-row-reverse" if i % 2 else ""
            rows.append(
                f'<article class="city-service-row{reverse}"><div class="city-service-media">'
                f'{placeholder(sec["heading"], DETAIL_FILES[i % 4], page, sec["heading"], "16:9", "280px")}</div>'
                f'<div><span class="eyebrow"><span></span> Details</span><h3>{esc(sec["heading"])}</h3>'
                f'{"".join(f"<p>{inline_md(p)}</p>" for p in paras[:3])}'
                f'<a class="text-link" href="tel:{PHONE_TEL}">Book this service →</a></div></article>'
            )
        details_html = f'<section class="section city-service-details"><div class="shell"><div class="section-heading"><span class="eyebrow"><span></span> Deeper detail</span><h2>What you should know</h2></div>{"".join(rows)}</div></section>'

    problems_html = ""
    cause_sec = find_section(sections, "cause") or find_section(sections, "why speed") or find_section(sections, "common")
    if cause_sec and cause_sec is not includes_sec:
        items = []
        for b in cause_sec["blocks"]:
            if b["type"] == "p" and b["text"].startswith("**"):
                m = re.match(r"\*\*([^*]+)\*\*\s*(.*)", b["text"])
                if m:
                    items.append((m.group(1), m.group(2)))
        if not items:
            for it in all_list_items(cause_sec["blocks"])[:4]:
                items.append((it[:60], it))
        if items:
            arts = "".join(
                f'<article><span>{i:02d}</span><div><h3>{esc(t)}</h3><p>{inline_md(d)}</p></div><b>↗</b></article>'
                for i, (t, d) in enumerate(items[:4], 1)
            )
            problems_html = f'''<section class="problems-section"><div class="shell problems-grid"><div class="problems-intro"><span class="eyebrow eyebrow-light"><span></span> Problems we solve</span><h2>{esc(cause_sec["heading"])}</h2><p>Local patterns we see across North Richland Hills.</p><a class="button button-primary" href="tel:{PHONE_TEL}">Ask a pro <span>→</span></a></div><div class="problem-list">{arts}</div></div></section>'''

    body = "\n".join(filter(None, [
        hero, about_html, why_html, process_html, details_html, problems_html, faq_section(faqs),
        related_services(url),
        cta_band(f"Need {short}?", f"Call {PHONE_DISPLAY} any time for Category 3 cleanup in {CITY}."),
        contact_section(),
    ]))
    return shell_page(meta, url, body)


def build_services_index(doc: dict, meta: dict) -> str:
    url = "/services/"
    page = "services"
    sections, faqs = extract_faqs(doc["sections"])
    title = doc["title"] or "Sewage Cleanup Services"
    lead = first_paragraph(doc["intro"]) or "Find the right sewage cleanup service for your situation."
    hero = location_hero(title, lead, [("/", "Home"), ("", "Services")], "Full service list", page)

    all_svcs = [
        ("/sewage-backup-cleanup/", "Sewage Backup Cleanup"),
        ("/emergency-sewage-cleanup/", "Emergency Sewage Cleanup"),
        ("/toilet-overflow-cleanup/", "Toilet Overflow Cleanup"),
        ("/black-water-cleanup/", "Black Water Cleanup"),
        ("/sewage-water-extraction/", "Sewage Water Extraction"),
        ("/crawl-space-sewage-cleanup/", "Crawl Space Sewage Cleanup"),
        ("/sewage-disinfection-sanitization/", "Disinfection & Sanitization"),
        ("/sewage-odor-removal/", "Sewage Odor Removal"),
        ("/sewage-damage-restoration/", "Damage Restoration"),
        ("/sewage-cleanup-process/", "Cleanup Process"),
        ("/sewage-cleanup-cost/", "Cleanup Cost"),
        ("/sewage-backup-insurance-claims/", "Insurance Claims"),
    ]
    feat = []
    for i, (href, label) in enumerate(all_svcs[:3]):
        slug = href.strip("/").split("/")[-1]
        card_file = CARD_MAP.get(slug, "shared-process")
        feat.append(f'''<article class="service-card{' service-card-featured' if i==0 else ''}" style="min-height:220px;">
          {placeholder(label, card_file, page, label, "4:3", "100%")}
          <div class="service-overlay"><span>NRH</span><h3>{esc(label)}</h3><p>Category 3 sewage cleanup in North Richland Hills.</p><a href="{href}">Explore <b>→</b></a></div>
        </article>''')

    table_html = ""
    for sec in sections:
        for b in sec["blocks"]:
            if b["type"] == "table":
                table_html = blocks_to_html([b])
                break
    guide = ""
    if table_html:
        guide = f'''<section class="section about-section"><div class="shell"><div class="section-heading"><span class="eyebrow"><span></span> Match the problem</span><h2>Find the Right Service for Your Situation</h2></div><div class="prose-content">{table_html}</div></div></section>'''

    grid = f'''<section class="section section-ivory"><div class="shell"><div class="section-heading centered"><span class="eyebrow"><span></span> What we do</span><h2>All Sewage Cleanup Services</h2><p>If you are not sure which you need, call <span class="phone-nowrap">{PHONE_DISPLAY}</span> and describe what you see.</p></div><div class="service-grid">{"".join(feat)}</div><div class="service-list">{"".join(f'<a href="{h}"><span>{i:02d}</span><strong>{esc(l)}</strong><small>Available 24/7 in {CITY}</small><b>↗</b></a>' for i,(h,l) in enumerate(all_svcs,1))}</div></div></section>'''

    steps = [
        ("Inspect", "Find where the sewage went, including hidden moisture."),
        ("Contain & extract", "Stop the spread and remove standing wastewater."),
        ("Remove, disinfect & dry", "Pull what cannot be saved, sanitize, and dry the structure."),
        ("Restore", "Rebuild drywall, flooring, and finishes as needed."),
    ]
    body = "\n".join(filter(None, [
        hero, trust_strip(), guide, grid,
        process_section("How Every Job Works", steps, page),
        f'''<section class="section why-section"><div class="shell"><div class="section-heading heading-split"><div><span class="eyebrow"><span></span> Our standard</span><h2>One call, the right scope</h2></div><p>Most jobs include extraction, removal, disinfection, drying, and odor control in one visit.</p></div>
        <div class="benefit-grid">
          <article><span class="benefit-number">01</span><div class="mini-icon">☎</div><h3>Not sure which service?</h3><p>Call <span class="phone-nowrap">{PHONE_DISPLAY}</span>. Most calls start as sewage backup cleanup.</p></article>
          <article><span class="benefit-number">02</span><div class="mini-icon">◎</div><h3>Available any hour</h3><p>All cleanup services run 24/7. Rebuild follows after drying.</p></article>
          <article><span class="benefit-number">03</span><div class="mini-icon">⌂</div><h3>Homes & businesses</h3><p>Every service is available for any property inside North Richland Hills.</p></article>
        </div></div></section>''',
        faq_section(faqs),
        cta_band("Ready for sewage cleanup?", f"Call {PHONE_DISPLAY} for any sewage cleanup service in NRH."),
        contact_section(),
    ]))
    return shell_page(meta, url, body)


def build_areas_index(doc: dict, meta: dict) -> str:
    url = "/areas/"
    page = "areas"
    sections, faqs = extract_faqs(doc["sections"])
    title = doc["title"] or "Areas We Serve"
    lead = first_paragraph(doc["intro"]) or f"Sewage cleanup across every {CITY} neighborhood."
    hero = location_hero(title, lead, [("/", "Home"), ("", "Areas")], "Service Areas", page)

    region_html = []
    for sec in sections:
        if "frequently" in sec["heading"].lower():
            continue
        items = all_list_items(sec["blocks"])
        paras = paragraphs(sec["blocks"])
        links = []
        for it in items:
            m = re.search(r"\[([^\]]+)\]\(([^)]+)\)", it)
            if m:
                links.append((m.group(2), m.group(1)))
        if links:
            lis = "".join(f'<li><a href="{esc(h)}">{esc(n)}</a></li>' for h, n in links)
            region_html.append(f'<div><h3>{esc(sec["heading"])}</h3><p>{inline_md(paras[0]) if paras else ""}</p><ul>{lis}</ul></div>')
        elif paras:
            region_html.append(f'<div><h3>{esc(sec["heading"])}</h3>{"".join(f"<p>{inline_md(p)}</p>" for p in paras[:3])}</div>')

    areas_sec = f'''<section class="section area-section"><div class="shell"><div class="section-heading"><span class="eyebrow"><span></span> Neighborhoods</span><h2>Pick your part of NRH</h2><p>Neighborhoods vary a lot—older clay lines near Loop 820 differ from newer PVC near North Tarrant Parkway.</p></div>
    <div class="area-columns" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:2rem;">{"".join(region_html)}</div>
    <div class="zip-grid" style="margin-top:2rem;"><span>76180</span><span>76182</span><span>76148</span><span>76117</span></div>
    </div></section>'''

    why = f'''<section class="section why-section"><div class="shell"><div class="section-heading heading-split"><div><span class="eyebrow"><span></span> Why it matters</span><h2>Why Neighborhood Matters for Sewage Cleanup</h2></div><p>Age of the sewer line, foundation type, and mature trees change how backups start—and how we clean them.</p></div>
    <div class="benefit-grid">
      <article><span class="benefit-number">01</span><div class="mini-icon">①</div><h3>Age of the sewer line</h3><p>Clay and cast iron fail differently from PVC. Roots and corrosion vs. grease, wipes, and sags.</p></article>
      <article><span class="benefit-number">02</span><div class="mini-icon">②</div><h3>Foundation type</h3><p>Slab homes show backups at the lowest drain. Pier and beam can hide sewage in the crawl space.</p></article>
      <article><span class="benefit-number">03</span><div class="mini-icon">③</div><h3>Trees & soil</h3><p>Mature trees drive root intrusion; North Texas clay moves lines with wet and dry seasons.</p></article>
    </div></div></section>'''

    body = "\n".join([
        hero, trust_strip(), areas_sec, why, faq_section(faqs),
        cta_band("In North Richland Hills city limits?", f"We serve you. Call {PHONE_DISPLAY} with your address."),
        contact_section(),
    ])
    return shell_page(meta, url, body)


def build_area(doc: dict, meta: dict, url: str) -> str:
    page = url.strip("/").replace("/", "-")
    sections, faqs = extract_faqs(doc["sections"])
    title = doc["title"] or "Area"
    name = title.replace("Sewage Cleanup in ", "").replace(", North Richland Hills", "").strip()
    intro_paras = paragraphs(doc["intro"])
    lead = intro_paras[1] if len(intro_paras) > 1 else (intro_paras[0] if intro_paras else "")

    snapshot = f'''<aside class="local-snapshot">
          <div class="snapshot-top"><span class="snapshot-pin">{BRAND_MARK}</span><div><small>Primary service hub</small><strong>{esc(name)}</strong></div></div>
          <dl><div><dt>Emergency service</dt><dd>24/7</dd></div><div><dt>Market</dt><dd>NRH, TX</dd></div><div><dt>Focus</dt><dd>Category 3</dd></div></dl>
          <p><span class="status-dot"></span> Technicians serving {esc(name)} today</p>
        </aside>'''

    hero = location_hero(
        title, lead, [("/", "Home"), ("/areas/", "Areas"), ("", name)],
        f"Your local {name} sewage cleanup team", page, snapshot=snapshot,
    )
    trust = f'''<section class="location-trust"><div class="shell location-trust-inner">
      <div><strong>24/7</strong><span>Emergency service</span></div>
      <div><strong>NRH</strong><span>City focus only</span></div>
      <div><strong>Cat 3</strong><span>Sewage cleanup standard</span></div>
      <p>Licensed · Upfront scope · Clean work areas · Photo documentation</p>
    </div></section>'''

    story = " ".join(intro_paras[1:3]) if len(intro_paras) > 1 else (intro_paras[0] if intro_paras else "")
    first_sec = sections[0] if sections else None
    note = paragraphs(first_sec["blocks"])[0] if first_sec and paragraphs(first_sec["blocks"]) else f"{name} is part of our North Richland Hills service area."
    authority = f'''<section class="section city-authority" id="why-local">
      <div class="shell city-authority-layout">
        <div class="city-intro"><h2>Why Choose Our {esc(name)} Crew?</h2></div>
        <div class="city-story"><p class="drop-cap">{inline_md(story)}</p><a class="text-link" href="#services">Explore {esc(name)} services →</a></div>
        <div class="city-note"><p>{inline_md(note)}</p><strong>{esc(BRAND)}</strong></div>
      </div>
    </section>'''

    svc_sec = find_section(sections, "service")
    svc_links = []
    if svc_sec:
        for it in all_list_items(svc_sec["blocks"]):
            m = re.search(r"\[([^\]]+)\]\(([^)]+)\)", it)
            if m:
                svc_links.append((m.group(2), m.group(1)))
    if not svc_links:
        svc_links = NAV_SERVICES[:4]
    services_html = f'''<section class="section location-services" id="services"><div class="shell">
      <div class="section-heading"><span class="eyebrow"><span></span> Local services</span><h2>Services {esc(name)} Residents Use Most</h2></div>
      <div class="service-list">{"".join(f'<a href="{h}"><span>{i:02d}</span><strong>{esc(n)}</strong><small>Sewage cleanup in {esc(name)}</small><b>↗</b></a>' for i,(h,n) in enumerate(svc_links[:6],1))}</div>
    </div></section>'''

    detail_html_parts = []
    for i, sec in enumerate(sections[:4]):
        if sec is svc_sec:
            continue
        paras = paragraphs(sec["blocks"])
        lists = all_list_items(sec["blocks"])
        detail_html_parts.append(f'''<article class="city-service-row{' city-service-row-reverse' if i%2 else ''}">
          <div class="city-service-media">{placeholder(sec["heading"], DETAIL_FILES[i % 4], page, f"{name}: {sec['heading']}", "16:9", "260px")}</div>
          <div><span class="eyebrow"><span></span> In {esc(name)}</span><h3>{esc(sec["heading"])}</h3>
          {"".join(f"<p>{inline_md(p)}</p>" for p in paras[:3])}
          {"<ul class='check-list'>" + "".join(f'<li><span>✓</span> <span class="check-text">{inline_md(x)}</span></li>' for x in lists[:5]) + "</ul>" if lists else ""}
          <a class="text-link" href="tel:{PHONE_TEL}">Call for help →</a></div></article>''')
    details = f'''<section class="section city-service-details"><div class="shell"><div class="section-heading"><span class="eyebrow"><span></span> Local detail</span><h2>What we see in {esc(name)}</h2></div>{"".join(detail_html_parts)}</div></section>''' if detail_html_parts else ""

    others = [a for a in AREA_META if a["url"].rstrip("/") != url.rstrip("/")][:6]
    nearby = f'''<section class="nearby-section"><div class="shell"><div class="section-heading centered"><span class="eyebrow"><span></span> Nearby</span><h2>Other NRH neighborhoods we serve</h2></div>
      <div class="area-columns"><ul>{"".join(f'<li><a href="{a["url"]}">{esc(a["name"])}</a></li>' for a in others[:3])}</ul>
      <ul>{"".join(f'<li><a href="{a["url"]}">{esc(a["name"])}</a></li>' for a in others[3:6])}</ul></div>
      <p style="text-align:center;margin-top:1.5rem;"><a class="text-link" href="/areas/">All service areas →</a></p>
    </div></section>'''

    cta = f'''<section class="location-cta"><div class="shell cta-inner"><div><span class="eyebrow eyebrow-light"><span></span> {esc(name)}</span><h2>{esc(name)} sewage cleanup, 24/7</h2></div><p>Call <span class="phone-nowrap">{PHONE_DISPLAY}</span> any time.</p><a class="button button-light" href="tel:{PHONE_TEL}">Call Now <span>→</span></a></div></section>'''

    body = "\n".join(filter(None, [
        hero, trust, authority, services_html, details, nearby, faq_section(faqs, f"FAQs for {name}"),
        cta, contact_section(f"Sewage problem in {name}? Call {PHONE_DISPLAY}—a real person answers 24/7."),
    ]))
    return shell_page(meta, url, body)


def build_about(doc: dict, meta: dict) -> str:
    url = "/about/"
    page = "about"
    sections, faqs = extract_faqs(doc["sections"])
    title = doc["title"] or "About Us"
    lead = first_paragraph(doc["intro"]) or ""
    hero = location_hero(title, lead, [("/", "Home"), ("", "About")], "Our story", page)

    checks = []
    for sec in sections:
        checks.extend(all_list_items(sec["blocks"]))
    checks = checks[:5] or [
        "NRH-only service area", "IICRC S500 Category 3 process",
        "Honest save-vs-remove advice", "Photo & moisture documentation", "Cleanup through rebuild",
    ]
    about_paras = paragraphs(doc["intro"]) + (paragraphs(sections[0]["blocks"]) if sections else [])
    about_html = f'''<section class="section about-section"><div class="shell split-layout">
      <div class="image-stack">{placeholder("About team / truck", "shared-portrait", page, "Sewage Fix Pros crew and response vehicle", "4:5", "420px")}<div class="image-caption">One city. One specialty.</div></div>
      <div class="section-copy">
        <span class="eyebrow"><span></span> Who we are</span>
        <h2>{esc(sections[0]["heading"] if sections else "Why We Only Work in NRH")}</h2>
        <p class="lead">{inline_md(about_paras[0] if about_paras else lead)}</p>
        {"".join(f"<p>{inline_md(p)}</p>" for p in about_paras[1:4])}
        <ul class="check-list">{"".join(f'<li><span>✓</span> <span class="check-text">{inline_md(c)}</span></li>' for c in checks)}</ul>
        <div class="signature-row"><div class="signature">{esc(BRAND)}</div><div><strong>{esc(BRAND)}</strong><small>North Richland Hills, TX</small></div></div>
      </div>
    </div></section>'''

    why_cards = []
    for i, sec in enumerate(sections[:3], 1):
        paras = paragraphs(sec["blocks"])
        why_cards.append(f'<article><span class="benefit-number">{i:02d}</span><div class="mini-icon">✓</div><h3>{esc(sec["heading"])}</h3><p>{inline_md(paras[0] if paras else "")}</p></article>')
    why = f'''<section class="section why-section"><div class="shell"><div class="section-heading centered"><span class="eyebrow"><span></span> How we work</span><h2>Our Promise</h2></div><div class="benefit-grid">{"".join(why_cards)}</div></div></section>''' if why_cards else ""

    body = "\n".join(filter(None, [
        hero, trust_strip(), about_html, why, faq_section(faqs),
        cta_band("Need help now?", f"Call {PHONE_DISPLAY}."),
        contact_section(),
    ]))
    return shell_page(meta, url, body)


def build_contact(doc: dict, meta: dict) -> str:
    url = "/contact/"
    page = "contact"
    sections, faqs = extract_faqs(doc["sections"])
    title = doc["title"] or "Contact Us"
    lead = f"Phone is the fastest way to get help. We answer 24 hours a day at {PHONE_DISPLAY}."  # wrapped via location_hero/inline_md
    hero = location_hero(title, lead, [("/", "Home"), ("", "Contact")], "Call anytime", page)

    steps = []
    for sec in sections:
        if "happens" in sec["heading"].lower() or "when you call" in sec["heading"].lower():
            steps = parse_ol_steps(sec["blocks"])
    ready = find_section(sections, "ready") or find_section(sections, "have this")
    ready_items = all_list_items(ready["blocks"]) if ready else []

    contact_body = f'''<section class="section contact-section" id="contact"><div class="shell contact-layout contact-layout-solo">
      <div class="contact-copy">
        <span class="eyebrow"><span></span> Call first</span>
        <h2>Call <span class="phone-nowrap">{PHONE_DISPLAY}</span></h2>
        <p>There are no forms to fill out and no waiting for a callback. A real person who understands sewage cleanup answers.</p>
        <div class="contact-details">
          <a href="tel:{PHONE_TEL}"><small>Phone</small><strong class="phone-nowrap">{PHONE_DISPLAY}</strong></a>
          <div><small>Address</small><strong>6200 Rufe Snow Dr, North Richland Hills, TX 76180</strong></div>
          <div><small>Hours</small><strong>Open 24 hours · 7 days a week</strong></div>
        </div>
        {"<h3 style='margin-top:2rem;'>What happens when you call</h3><ol style='padding-left:1.25rem;'>" + "".join(f"<li style='margin-bottom:0.75rem;'><strong>{inline_md(n)}</strong> {inline_md(d)}</li>" for n,d in steps) + "</ol>" if steps else ""}
        {"<h3 style='margin-top:2rem;'>Have this ready if you can</h3><ul class='check-list'>" + "".join(f'<li><span>✓</span> <span class="check-text">{inline_md(x)}</span></li>' for x in ready_items) + "</ul>" if ready_items else ""}
      </div>
    </div></section>'''

    body = "\n".join([
        hero, trust_strip(), contact_body, faq_section(faqs),
        cta_band("Sewage spreading now?", f"Call {PHONE_DISPLAY}—we dispatch as soon as you call."),
    ])
    return shell_page(meta, url, body)


def build_legal(doc: dict, meta: dict, url: str) -> str:
    page = url.strip("/").replace("/", "-")
    title = doc["title"] or meta.get("title_tag", "Legal")
    parts = list(doc["intro"])
    for sec in doc["sections"]:
        parts.append({"type": "heading", "level": 2, "text": sec["heading"]})
        parts.extend(sec["blocks"])
    prose = blocks_to_html(parts)
    hero = location_hero(title, phone_sub(meta.get("meta_description", "")), [("/", "Home"), ("", title)], "Legal", page, show_actions=False)
    body = hero + f'<section class="section"><div class="shell prose-content">{prose}</div></section>' + cta_band("Questions?", f"Call {PHONE_DISPLAY}.")
    return shell_page(meta, url, body)
