#!/usr/bin/env python3
"""Home page builder."""
from __future__ import annotations
import re
from mdutil import (
    AREA_META, BRAND, BRAND_MARK, CITY, PHONE_DISPLAY, PHONE_TEL, IMAGE_SLOTS, phone_nowrap_html,
    esc, inline_md, paragraphs, find_section, extract_faqs, checklist_from_blocks,
    parse_ol_steps,
)
from chrome import (
    shell_page, trust_strip, faq_section, cta_band, contact_section,
    placeholder, process_section,
)


def build_home(doc: dict, meta: dict) -> str:
    url = "/"
    page = "home"
    sections, faqs = extract_faqs(doc["sections"])
    title = doc["title"] or f"Sewage Cleanup in {CITY}, TX"
    intro_paras = paragraphs(doc["intro"])
    hero_p = intro_paras[1] if len(intro_paras) > 1 else (intro_paras[0] if intro_paras else "")

    why_backups = find_section(sections, "why", "backup") or find_section(sections, "why sewage")
    process_sec = find_section(sections, "process") or find_section(sections, "cleanup process")
    who_sec = find_section(sections, "who we")
    do_sec = find_section(sections, "what to do")

    IMAGE_SLOTS.append({"slot": "home-hero-crew", "page": page, "subject": "Sewage cleanup crew / NRH emergency response", "aspect": "21:9", "suggested": "assets/images/home-hero-crew.webp"})
    hero = f'''<section class="hero">
    <div class="hero-media img-placeholder" data-image-slot="home-hero-crew" data-image-path="assets/images/home-hero-crew.webp" role="img" aria-label="Sewage cleanup crew">
      <div>Hero: sewage cleanup crew / NRH<small>Image needed · 21:9 · assets/images/home-hero-crew.webp</small></div>
    </div>
    <div class="hero-shade"></div>
    <div class="shell hero-layout">
      <div class="hero-copy">
        <span class="eyebrow eyebrow-light"><span></span> Your trusted local team</span>
        <h1>{esc(title)}</h1>
        <p>{inline_md(hero_p)}</p>
        <div class="hero-actions">
          <a class="button button-primary" href="tel:{PHONE_TEL}">Call <span class="phone-nowrap">{PHONE_DISPLAY}</span> <span>→</span></a>
          <a class="text-link text-link-light" href="tel:{PHONE_TEL}">Need help now? Call 24/7</a>
        </div>
        <div class="hero-proof">
          <div><strong>24/7</strong><span><small>Emergency response</small></span></div>
          <div><strong>60<sup>min</sup></strong><span><small>Typical arrival window</small></span></div>
        </div>
      </div>
      <div class="request-card">
        <div class="request-heading"><span class="request-icon">↗</span><div><small>Fast dispatch</small><h2>Request service today</h2></div></div>
        <p>Tell us what is happening. A local dispatcher will confirm your visit shortly.</p>
        <a class="button button-primary button-full" href="tel:{PHONE_TEL}">Call Now <span class="phone-nowrap">{PHONE_DISPLAY}</span> <span>→</span></a>
        <small class="form-note">No spam. No obligation. Just practical help.</small>
      </div>
    </div>
  </section>'''

    about_checks = ["IICRC S500 Category 3 standards", "24/7 local NRH dispatch", "Extraction, disinfection & restoration"]
    about_lead = intro_paras[2] if len(intro_paras) > 2 else (intro_paras[-1] if intro_paras else "")
    about_extra = paragraphs(who_sec["blocks"])[0] if who_sec else "We work for homeowners, renters, landlords, property managers, HOAs, and businesses across North Richland Hills."
    about1 = f'''<section class="section about-section" id="about">
    <div class="shell split-layout">
      <div class="image-stack">
        {placeholder("About: tech inspecting sewage damage", "home-about-stack", page, "Technician inspecting sewage damage in NRH home", "4:5", "420px")}
        <div class="image-caption">Real technicians. Real accountability.</div>
      </div>
      <div class="section-copy">
        <span class="eyebrow"><span></span> Built for better service</span>
        <h2>Trusted Sewage Cleanup in North Richland Hills</h2>
        <p class="lead">{inline_md(about_lead)}</p>
        <p>{inline_md(about_extra)}</p>
        <ul class="check-list">{"".join(f'<li><span>✓</span> <span class="check-text">{inline_md(c)}</span></li>' for c in about_checks)}</ul>
        <div class="signature-row">
          <div class="signature">{esc(BRAND)}</div>
          <div><strong>{esc(BRAND)}</strong><small>Locally focused · NRH only</small></div>
          <a class="circle-link" href="/about/" aria-label="Read our story">↗</a>
        </div>
      </div>
    </div>
  </section>'''

    featured = [
        ("/sewage-backup-cleanup/", "Sewage Backup Cleanup", "Most requested", "Waste coming up through drains, tubs and toilets when the line is blocked."),
        ("/emergency-sewage-cleanup/", "Emergency Sewage Cleanup", "Available 24/7", "Day or night response, including weekends and holidays."),
        ("/toilet-overflow-cleanup/", "Toilet Overflow Cleanup", "Fast containment", "Overflows that spread past the bathroom floor into walls and adjacent rooms."),
    ]
    list_svcs = [
        ("04", "/black-water-cleanup/", "Black Water Cleanup", "Any Category 3 water, including sewage mixed with storm or flood water."),
        ("05", "/sewage-water-extraction/", "Sewage Water Extraction", "Standing sewage removed fast with truck-mounted and portable pumps."),
        ("06", "/crawl-space-sewage-cleanup/", "Crawl Space Sewage Cleanup", "Pier and beam homes where a broken line drains under the house."),
        ("07", "/sewage-disinfection-sanitization/", "Disinfection & Sanitization", "Killing the germs that stay behind after the water is gone."),
        ("08", "/sewage-odor-removal/", "Sewage Odor Removal", "Getting rid of the smell for good—not covering it."),
        ("09", "/sewage-damage-restoration/", "Damage Restoration", "Replacing drywall, flooring, baseboards and cabinets after cleanup."),
    ]
    feat_cards = []
    for i, (href, name, badge, desc) in enumerate(featured):
        slot = f"home-service-{i+1}"
        feat_cards.append(f'''<article class="service-card{' service-card-featured' if i==0 else ''}">
          {placeholder(name, slot, page, f"{name} in NRH", "4:3", "100%")}
          <div class="service-overlay"><span>{esc(badge)}</span><h3>{esc(name)}</h3><p>{esc(desc)}</p><a href="{href}">Explore <b>→</b></a></div>
        </article>''')
    list_html = "".join(
        f'<a href="{href}"><span>{num}</span><strong>{esc(name)}</strong><small>{esc(desc)}</small><b>↗</b></a>'
        for num, href, name, desc in list_svcs
    )
    services_blk = f'''<section class="section section-ivory" id="services">
    <div class="shell">
      <div class="section-heading centered">
        <span class="eyebrow"><span></span> What we do</span>
        <h2>Sewage Cleanup Services in NRH</h2>
        <p>Every sewage job is different. From a toilet overflow to a main-line backup, we extract, remove, disinfect, dry, and restore—following Category 3 standards.</p>
      </div>
      <div class="service-grid">{"".join(feat_cards)}</div>
      <div class="service-list">{list_html}</div>
      <p style="text-align:center;margin-top:2rem;"><a class="text-link" href="/services/">See all services →</a></p>
    </div>
  </section>'''

    brand_strip = ''

    why = f'''<section class="section why-section">
    <div class="shell">
      <div class="section-heading heading-split">
        <div><span class="eyebrow"><span></span> Our standard</span><h2>Why Choose Our Sewage Cleanup Team?</h2></div>
        <p>We focus only on North Richland Hills, so crews stay close to Davis Boulevard, Rufe Snow Drive, and Precinct Line Road when every minute matters.</p>
      </div>
      <div class="benefit-grid">
        <article><span class="benefit-number">01</span><div class="mini-icon">⌂</div><h3>NRH-Only Focus</h3><p>No Metroplex-wide queue. Our trucks stay inside North Richland Hills so arrival windows stay short when sewage is spreading.</p></article>
        <article><span class="benefit-number">02</span><div class="mini-icon">◎</div><h3>Category 3 Process</h3><p>We follow IICRC S500 steps: inspect, contain, extract, remove, disinfect, dry, and restore—so the space is safe, not just dry-looking.</p></article>
        <article><span class="benefit-number">03</span><div class="mini-icon">$</div><h3>Clear Documentation</h3><p>Photos, moisture readings, and a written scope help you and your adjuster understand the loss and what was done.</p></article>
      </div>
    </div>
  </section>'''

    problems_items = []
    if why_backups:
        for b in why_backups["blocks"]:
            if b["type"] == "p" and b["text"].startswith("**"):
                m = re.match(r"\*\*([^*]+)\*\*\s*(.*)", b["text"])
                if m:
                    problems_items.append((m.group(1), m.group(2)))
    if not problems_items:
        problems_items = [
            ("Older clay & cast iron lines", "Southern NRH homes often have original lines prone to roots and scale."),
            ("North Texas clay soil", "Swell/shrink movement cracks and sags sewer laterals over time."),
            ("Heavy rain backups", "Storms push water into the system and out the lowest drain."),
        ]
    prob_articles = "".join(
        f'<article><span>{i:02d}</span><div><h3>{esc(t)}</h3><p>{inline_md(d)}</p></div><b>↗</b></article>'
        for i, (t, d) in enumerate(problems_items[:4], 1)
    )
    problems = f'''<section class="problems-section">
    <div class="shell problems-grid">
      <div class="problems-intro"><span class="eyebrow eyebrow-light"><span></span> Call before it gets worse</span><h2>Why Sewage Backups Happen in NRH</h2><p>Property age, soil, and storms shape the backups we see across North Richland Hills.</p><a class="button button-primary" href="tel:{PHONE_TEL}">Ask a pro <span>→</span></a></div>
      <div class="problem-list">{prob_articles}</div>
    </div>
  </section>'''

    matter_paras = paragraphs(do_sec["blocks"]) if do_sec else []
    matter_lead = matter_paras[0] if matter_paras else "If sewage is coming into your property, first steps protect your family and your floors."
    matter_checks = checklist_from_blocks(do_sec["blocks"] if do_sec else [], 5) or [
        "Stop using water", "Keep people and pets out", "Do not touch sewage with bare hands",
        "Turn off power to wet areas if safe", f"Call {PHONE_DISPLAY}",
    ]
    about2 = f'''<section class="section about-section">
    <div class="shell split-layout">
      <div class="image-stack">
        {placeholder("What matters: containment setup", "home-what-matters", page, "Containment and PPE during sewage cleanup", "4:5", "420px")}
        <div class="image-caption">Stop the spread. Then clean it right.</div>
      </div>
      <div class="section-copy">
        <span class="eyebrow"><span></span> Act fast</span>
        <h2>What To Do Right Now</h2>
        <p class="lead">{inline_md(matter_lead)}</p>
        <ul class="check-list">{"".join(f'<li><span>✓</span> <span class="check-text">{inline_md(c)}</span></li>' for c in matter_checks)}</ul>
        <div class="signature-row signature-row-cta"><a class="button button-primary" href="tel:{PHONE_TEL}" style="margin:0;">Call <span class="phone-nowrap">{PHONE_DISPLAY}</span> <span>→</span></a></div>
      </div>
    </div>
  </section>'''

    steps = parse_ol_steps(process_sec["blocks"]) if process_sec else []
    if not steps:
        steps = [
            ("Inspection", "Find where sewage went with moisture meters and thermal imaging."),
            ("Containment", "Seal off the area so contamination does not travel."),
            ("Extraction", "Pump out standing sewage and haul it away properly."),
            ("Removal", "Cut out porous materials that cannot be saved."),
            ("Disinfection", "Scrub and treat remaining surfaces with EPA-registered disinfectant."),
        ]
    process_html = process_section("Our Cleanup Process", steps[:5], page, "home-process")

    emergency = f'''<section class="emergency-banner">
    {placeholder("Emergency banner background", "home-emergency-banner", page, "Emergency sewage response vehicle / crew", "21:9", "100%")}
    <div class="shell emergency-inner">
      <div class="emergency-card">
        <span class="eyebrow eyebrow-light"><span></span> 24/7 emergency response</span>
        <h2>Need Immediate Sewage Cleanup in NRH?</h2>
        <p>Sewage spreads fast. Call now and we will give you an arrival window while the crew heads your way.</p>
        <div><a class="button button-primary" href="tel:{PHONE_TEL}">Call <span class="phone-nowrap">{PHONE_DISPLAY}</span> <span>→</span></a><small>Average callback under 5 minutes</small></div>
      </div>
    </div>
  </section>'''

    half = (len(AREA_META) + 1) // 2
    col1 = "".join(f'<li><a href="{a["url"]}">{esc(a["name"])}</a></li>' for a in AREA_META[:half])
    col2 = "".join(f'<li><a href="{a["url"]}">{esc(a["name"])}</a></li>' for a in AREA_META[half:])
    map_labels = "".join(f'<span class="map-label label-slot-{i}">{esc(a["name"])}</span>' for i, a in enumerate(AREA_META[:4], 1))
    areas_html = f'''<section class="section area-section" id="service-area">
    <div class="shell area-layout">
      <div class="area-copy">
        <span class="eyebrow"><span></span> Local by design</span>
        <h2>Areas We Cover Inside NRH</h2>
        <p>We serve every part of North Richland Hills—from HomeTown and Smithfield to Iron Horse, Diamond Loch, Thornbridge, and Forest Glenn.</p>
        <div class="area-columns"><ul>{col1}</ul><ul>{col2}</ul></div>
        <div class="zip-grid" style="margin-top:1.5rem;"><span>76180</span><span>76182</span><span>76148</span></div>
        <p class="zip-check"><strong>Not sure you're in range?</strong> Call with your address—if it says North Richland Hills, we serve you.</p>
      </div>
      <div class="service-map" aria-label="Illustrated service area map">
        <div class="map-water"><span>NORTH RICHLAND<br>HILLS</span></div>
        <div class="road road-one"></div><div class="road road-two"></div><div class="road road-three"></div>
        {map_labels}
        <span class="map-pin pin-one">{BRAND_MARK}</span><span class="map-pin pin-two">{BRAND_MARK}</span><span class="map-pin pin-three">{BRAND_MARK}</span><span class="map-pin pin-four">{BRAND_MARK}</span><span class="map-pin pin-five">{BRAND_MARK}</span>
        <div class="map-legend"><span></span> Primary service zone</div>
      </div>
    </div>
  </section>'''

    faq_html = faq_section(faqs, "Frequently Asked Questions", "Common questions about sewage cleanup in North Richland Hills.")
    newsletter = '''<section class="newsletter-section">
    <div class="shell newsletter-inner"><div><span class="newsletter-icon">✦</span><p><strong>Practical home-care notes.</strong><small>One useful tip each month on water emergencies. No clutter.</small></p></div>
    <form id="newsletter-form" onsubmit="event.preventDefault();this.querySelector('button').textContent='Thanks—call us anytime.';"><label class="sr-only" for="newsletter-email">Email address</label><input id="newsletter-email" type="email" placeholder="Email address" required><button type="submit">Send me the tips →</button></form></div>
  </section>'''

    body = "\n".join([
        hero, trust_strip(), about1, services_blk, why, problems, about2,
        process_html, emergency, areas_html, faq_html,
        cta_band("Sewage problem in North Richland Hills?", f"Call {PHONE_DISPLAY} any time, day or night."),
        contact_section(), newsletter,
    ])
    return shell_page(meta, url, body)
