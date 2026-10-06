#!/usr/bin/env python3
"""Shared header/footer/sections for NRH site."""
from __future__ import annotations
import html
import re
from mdutil import (
    AREA_META, BRAND, BRAND_MARK, BRAND_TAGLINE, ADDRESS, CITY, STATE,
    PHONE_DISPLAY, PHONE_TEL, NAV_SERVICES, TRUST_ITEMS, IMAGE_SLOTS,
    esc, inline_md, phone_sub, phone_nowrap_html, asset_prefix, blocks_to_html,
)


def placeholder(label: str, slot: str, page: str, subject: str, aspect: str = "16:9", min_h: str = "280px", extra_class: str = "") -> str:
    IMAGE_SLOTS.append({
        "slot": slot, "page": page, "subject": subject,
        "aspect": aspect, "suggested": f"assets/images/{slot}.webp",
    })
    cls = f"img-placeholder {extra_class}".strip()
    return (
        f'<div class="{cls}" data-image-slot="{esc(slot)}" data-image-path="assets/images/{esc(slot)}.webp" '
        f'style="min-height:{min_h};" role="img" aria-label="{esc(subject)}">'
        f'<div>{esc(label)}<small>Image needed · {esc(aspect)} · assets/images/{esc(slot)}.webp</small></div></div>'
    )


def header_html() -> str:
    svc_links = "".join(f'<a href="{href}">{esc(label)}</a>' for href, label in NAV_SERVICES)
    area_links = "".join(f'<a href="{a["url"]}">{esc(a["name"])}</a>' for a in AREA_META[:8])
    return f'''<header class="site-header">
    <div class="utility-bar">
      <div class="shell utility-inner">
        <p><span class="status-dot"></span> Licensed, insured &amp; ready 24/7</p>
        <div><span>Open 24 hours · 7 days a week</span></div>
      </div>
    </div>
    <nav class="main-nav shell" aria-label="Main navigation">
      <a class="brand" href="/" aria-label="{esc(BRAND)} home">
        <span class="brand-mark">{BRAND_MARK}</span>
        <span>{esc(BRAND)}<small>{BRAND_TAGLINE}</small></span>
      </a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-menu">
        <span></span><span></span><span></span><span class="sr-only">Toggle menu</span>
      </button>
      <div class="nav-links" id="site-menu">
        <a href="/">Home</a>
        <span class="nav-dd">
        <a href="/services/">Services <span class="nav-dd-caret">▾</span></a>
        <div class="nav-dd-panel">{svc_links}<a class="nav-dd-all" href="/services/">All services →</a></div>
      </span>
        <span class="nav-dd">
        <a href="/areas/">Areas <span class="nav-dd-caret">▾</span></a>
        <div class="nav-dd-panel">{area_links}<a class="nav-dd-all" href="/areas/">All service areas →</a></div>
      </span>
        <a href="/about/">About</a>
        <a href="/contact/">Contact</a>
      </div>
      <a class="nav-call" href="tel:{PHONE_TEL}"><span class="phone-icon">↗</span><span><small>Talk to a pro</small>{PHONE_DISPLAY}</span></a>
    </nav>
  </header>'''


def footer_html() -> str:
    svc_links = "".join(f'<a href="{href}">{esc(label)}</a>' for href, label in NAV_SERVICES[:6])
    maps_q = html.escape(ADDRESS, quote=True).replace(" ", "%20")
    return f'''<footer class="site-footer">
    <div class="shell footer-main">
      <div class="footer-brand">
        <a class="brand brand-light" href="/"><span class="brand-mark">{BRAND_MARK}</span><span>{esc(BRAND)}<small>{BRAND_TAGLINE}</small></span></a>
        <p>Category 3 sewage cleanup for North Richland Hills homes and businesses—delivered by a local crew that shows up fast.</p>
        <a class="footer-phone" href="tel:{PHONE_TEL}"><span class="phone-nowrap">{PHONE_DISPLAY}</span></a>
      </div>
      <div><h3>Services</h3>{svc_links}</div>
      <div>
        <h3>Company</h3>
        <a href="/about/">Our story</a>
        <a href="/services/">Services</a>
        <a href="/areas/">Service areas</a>
        <a href="/contact/">Contact us</a>
        <a href="/privacy-policy/">Privacy</a>
        <a href="/terms/">Terms</a>
      </div>
      <div>
        <h3>Visit</h3>
        <a class="footer-address" href="https://maps.google.com/?q={maps_q}" target="_blank" rel="noopener"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"></path><circle cx="12" cy="10" r="3"></circle></svg><span>{esc(ADDRESS)}</span></a>
        <p><a class="phone-nowrap" href="tel:{PHONE_TEL}" style="color:inherit;">{PHONE_DISPLAY}</a></p>
        <p>Open 24 hours · 7 days a week</p>
      </div>
    </div>
    <div class="shell footer-map-wrap">
      <iframe class="footer-map" title="{esc(BRAND)} on Google Maps" src="https://maps.google.com/maps?q={maps_q}&amp;t=&amp;z=14&amp;ie=UTF8&amp;iwloc=B&amp;output=embed" width="100%" height="240" loading="lazy" referrerpolicy="no-referrer-when-downgrade" style="border:0;"></iframe>
    </div>
    <div class="shell footer-bottom">
      <span>© 2026 {esc(BRAND)}</span>
      <div><a href="/privacy-policy/">Privacy</a><a href="/terms/">Terms</a><a href="/contact/">Contact</a></div>
      <span>Licensed &amp; insured</span>
    </div>
  </footer>
<div id="sticky-call-button-container">
  <a class="sticky-call" href="tel:{PHONE_TEL}"><span>↗</span><div><small>Emergency?</small><strong>Call <span class="phone-nowrap">{PHONE_DISPLAY}</span></strong></div></a>
</div>'''


def shell_page(meta: dict, url: str, body: str) -> str:
    prefix = asset_prefix(url)
    title = phone_sub(meta.get("title_tag", BRAND))
    desc = phone_sub(meta.get("meta_description", ""))
    return f'''<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
  <meta name="author" content="{esc(BRAND)}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{esc(url if url != "/" else "/")}">
  <link rel="stylesheet" href="{prefix}/global.css">
</head>
<body>
{header_html()}
{body}
{footer_html()}
<script src="{prefix}/js/main.js" defer></script>
</body>
</html>
'''


def trust_strip() -> str:
    cells = "".join(
        f"<div><span>{n}</span><p><strong>{esc(t)}</strong>{esc(d)}</p></div>"
        for n, t, d in TRUST_ITEMS
    )
    return f'<section class="trust-strip" aria-label="Service guarantees"><div class="shell trust-grid">{cells}</div></section>'


def faq_section(faqs: list[dict], heading: str = "Frequently Asked Questions", intro: str = "") -> str:
    if not faqs:
        return ""
    items = []
    for i, f in enumerate(faqs, 1):
        ans = blocks_to_html(f["a"]) if f["a"] else "<p></p>"
        items.append(
            f'<article><button type="button" aria-expanded="false"><span>{i:02d}</span><strong>{inline_md(f["q"])}</strong><b>+</b></button>'
            f'<div class="accordion-panel">{ans}</div></article>'
        )
    intro_p = f"<p>{inline_md(intro)}</p>" if intro else ""
    return f'''<section class="section faq-section">
    <div class="shell faq-layout">
      <div class="faq-intro"><span class="eyebrow"><span></span> Good questions</span><h2>{esc(heading)}</h2>{intro_p}<a class="text-link" href="tel:{PHONE_TEL}"><span class="phone-nowrap">{PHONE_DISPLAY}</span> →</a></div>
      <div class="accordion">{"".join(items)}</div>
    </div>
  </section>'''


def cta_band(h2: str, p: str) -> str:
    return f'''<section class="cta-band">
    <div class="shell cta-inner"><div><span class="eyebrow eyebrow-light"><span></span> Ready when you are</span><h2>{esc(h2)}</h2></div><p>{inline_md(p)}</p><a class="button button-light" href="tel:{PHONE_TEL}">Call Now <span>→</span></a></div>
  </section>'''


def contact_section(copy: str | None = None) -> str:
    p = copy or f"Call {PHONE_DISPLAY} for sewage cleanup in {CITY}. A real person answers 24/7—no forms, no waiting for a callback."
    return f'''<section class="section contact-section" id="contact">
    <div class="shell contact-layout contact-layout-solo">
      <div class="contact-copy">
        <span class="eyebrow"><span></span> Request help now</span>
        <h2>Get in Touch with Us</h2>
        <p>{inline_md(p)}</p>
        <div class="contact-details">
          <a href="tel:{PHONE_TEL}"><small>Call anytime</small><strong class="phone-nowrap">{PHONE_DISPLAY}</strong></a>
          <div><small>Service area</small><strong>{esc(CITY)}, {STATE}</strong></div>
          <div><small>Office hours</small><strong>Open 24 hours · 7 days a week</strong></div>
        </div>
      </div>
    </div>
  </section>'''


def location_hero(h1: str, lead: str, crumbs: list, eyebrow: str, page: str, slot: str, show_actions: bool = True, snapshot: str = "") -> str:
    IMAGE_SLOTS.append({"slot": slot, "page": page, "subject": f"Hero: {h1}", "aspect": "21:9", "suggested": f"assets/images/{slot}.webp"})
    crumb_html = []
    for i, (href, label) in enumerate(crumbs):
        if i:
            crumb_html.append("<span>/</span>")
        if href:
            crumb_html.append(f'<a href="{href}">{esc(label)}</a>')
        else:
            crumb_html.append(f"<strong>{esc(label)}</strong>")
    actions = ""
    if show_actions:
        actions = f'''<div class="location-hero-actions">
            <a class="button button-primary" href="tel:{PHONE_TEL}">Get a free quote <span>→</span></a>
            <a class="location-call-link" href="tel:{PHONE_TEL}"><small>Talk to a pro</small><strong class="phone-nowrap">{PHONE_DISPLAY}</strong></a>
          </div>'''
    return f'''<section class="location-hero">
      <div class="location-hero-image img-placeholder" data-image-slot="{esc(slot)}" data-image-path="assets/images/{esc(slot)}.webp" style="min-height:100%;" role="img" aria-label="{esc(h1)}">
        <div>Hero: {esc(h1)}<small>Image needed · 21:9 · assets/images/{esc(slot)}.webp</small></div>
      </div>
      <div class="location-hero-overlay"></div>
      <div class="shell location-hero-inner">
        <div class="location-hero-copy">
          <nav class="breadcrumbs" aria-label="Breadcrumb">{"".join(crumb_html)}</nav>
          <span class="eyebrow eyebrow-light"><span></span> {esc(eyebrow)}</span>
          <h1>{esc(h1)}</h1>
          <p>{inline_md(lead)}</p>
          {actions}
        </div>
        {snapshot}
      </div>
    </section>'''


def process_section(title: str, steps: list, page: str, slot: str) -> str:
    if not steps:
        return ""
    articles = []
    for i, (name, desc) in enumerate(steps):
        active = ' class="active"' if i == 0 else ""
        plain = re.sub(r"<[^>]+>", "", inline_md(desc))
        articles.append(
            f'<article{active}><button type="button" data-process="{i}" data-title="{esc(name)}" data-desc="{esc(plain)}">'
            f'<span>{i+1:02d}</span><strong>{inline_md(name)}</strong></button><p>{inline_md(desc)}</p></article>'
        )
    first_name, first_desc = steps[0]
    pct = 100 / max(len(steps), 1)
    ph = placeholder("Process: crew at work", slot, page, "Technicians performing sewage cleanup", "4:3", "480px")
    return f'''<section class="section process-section" id="process">
    <div class="shell process-layout">
      <div class="process-copy">
        <span class="eyebrow"><span></span> From call to complete</span>
        <h2>{esc(title)}</h2>
        <div class="process-list">{"".join(articles)}</div>
      </div>
      <div class="process-visual">
        {ph}
        <div class="process-card"><small id="process-step">STEP 01</small><strong id="process-title">{esc(first_name)}</strong><p id="process-description">{inline_md(first_desc)}</p></div>
        <div class="process-meter"><span style="width:{pct:.2f}%"></span></div>
      </div>
    </div>
  </section>'''


def related_services(current_url: str, limit: int = 6) -> str:
    cards = []
    n = 0
    for href, label in NAV_SERVICES:
        if href.rstrip("/") == current_url.rstrip("/"):
            continue
        n += 1
        if n > limit:
            break
        cards.append(f'<a href="{href}"><span>{n:02d}</span><strong>{esc(label)}</strong><small>Category 3 sewage cleanup in {CITY}</small><b>↗</b></a>')
    return f'''<section class="section section-ivory">
    <div class="shell">
      <div class="section-heading centered"><span class="eyebrow"><span></span> Related</span><h2>Other sewage cleanup services</h2><p>Every job follows the same Category 3 standard—inspect, contain, extract, remove, disinfect, dry, and restore.</p></div>
      <div class="service-list">{"".join(cards)}</div>
    </div>
  </section>'''
