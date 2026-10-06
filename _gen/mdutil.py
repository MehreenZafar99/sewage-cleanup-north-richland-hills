#!/usr/bin/env python3
"""Markdown parsing utilities for NRH site generator."""
from __future__ import annotations
import html
import re
from pathlib import Path

PHONE_DISPLAY = "(817) 204-3891"
PHONE_TEL = "8172043891"
PHONE_TEL_PLUS = "+18172043891"
BRAND = "Sewage Fix Pros"
BRAND_MARK = "S"
BRAND_TAGLINE = "SEWAGE CLEANUP"
ADDRESS = "6200 Rufe Snow Dr, North Richland Hills, TX 76180"
CITY = "North Richland Hills"
STATE = "TX"
CONTENT_DIR = Path("/workspace/nrh-build/nrh-content")
OUT_DIR = Path("/workspace/nrh-site")

NAV_SERVICES = [
    ("/sewage-backup-cleanup/", "Sewage Backup Cleanup"),
    ("/emergency-sewage-cleanup/", "Emergency Sewage Cleanup"),
    ("/toilet-overflow-cleanup/", "Toilet Overflow Cleanup"),
    ("/black-water-cleanup/", "Black Water Cleanup"),
    ("/sewage-water-extraction/", "Sewage Water Extraction"),
    ("/crawl-space-sewage-cleanup/", "Crawl Space Sewage Cleanup"),
    ("/sewage-disinfection-sanitization/", "Disinfection & Sanitization"),
    ("/sewage-odor-removal/", "Sewage Odor Removal"),
    ("/sewage-damage-restoration/", "Damage Restoration"),
]

TRUST_ITEMS = [
    ("01", "Upfront scope", "No work before you approve it"),
    ("02", "Respectful crews", "Containment, clean floors, clear updates"),
    ("03", "IICRC-aligned", "Category 3 sewage cleanup standards"),
    ("04", "NRH only", "Local techs focused on this city"),
]

IMAGE_SLOTS: list[dict] = []
AREA_META: list[dict] = []


def phone_nowrap_html() -> str:
    return f'<span class="phone-nowrap">{PHONE_DISPLAY}</span>'


def phone_sub(text: str, wrap: bool = False) -> str:
    """Replace [PHONE]. wrap=True inserts a nowrap span for body HTML (not meta tags)."""
    repl = phone_nowrap_html() if wrap else PHONE_DISPLAY
    return (text or "").replace("[PHONE]", repl)


def esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def asset_prefix(url: str) -> str:
    path = url.strip("/")
    if not path:
        return "assets"
    depth = len(path.split("/"))
    return "/".join([".."] * depth) + "/assets"


def page_path(url: str) -> Path:
    u = url.strip("/")
    if not u:
        return OUT_DIR / "index.html"
    return OUT_DIR / u / "index.html"


def parse_frontmatter(raw: str) -> tuple[dict, str]:
    raw = raw.lstrip("\ufeff")
    if not raw.startswith("---"):
        return {}, raw
    end = raw.find("\n---", 3)
    if end < 0:
        return {}, raw
    fm_block = raw[3:end].strip()
    body = raw[end + 4 :].lstrip("\n")
    meta = {}
    for line in fm_block.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, body


def inline_md(text: str) -> str:
    text = phone_sub(text, wrap=True)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{esc(m.group(2))}">{esc(m.group(1))}</a>',
        text,
    )
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    # Wrap bare phone numbers that were not introduced via [PHONE] (e.g. literals).
    def _wrap_bare_phone(s: str) -> str:
        out = []
        i = 0
        token = PHONE_DISPLAY
        while True:
            j = s.find(token, i)
            if j < 0:
                out.append(s[i:])
                break
            prev = s[max(0, j - 48):j]
            if 'class="phone-nowrap"' in prev or "class='phone-nowrap'" in prev:
                out.append(s[i:j + len(token)])
            else:
                out.append(s[i:j])
                out.append(phone_nowrap_html())
            i = j + len(token)
        return "".join(out)
    return _wrap_bare_phone(text)


def md_to_blocks(body: str) -> list[dict]:
    lines = body.splitlines()
    blocks: list[dict] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if "|" in line and i + 1 < len(lines) and re.match(r"^\|?\s*-+", lines[i + 1]):
            rows = []
            while i < len(lines) and "|" in lines[i]:
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not re.match(r"^:?-+:?$", row[0].replace(" ", "")):
                    rows.append(row)
                i += 1
            blocks.append({"type": "table", "rows": rows})
            continue
        hm = re.match(r"^(#{1,3})\s+(.*)$", line)
        if hm:
            blocks.append({"type": "heading", "level": len(hm.group(1)), "text": hm.group(2).strip()})
            i += 1
            continue
        if re.match(r"^[-*]\s+", line):
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i]):
                items.append(re.sub(r"^[-*]\s+", "", lines[i]))
                i += 1
            blocks.append({"type": "ul", "items": items})
            continue
        if re.match(r"^\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i]))
                i += 1
            blocks.append({"type": "ol", "items": items})
            continue
        paras = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^#{1,3}\s+", lines[i]) and not re.match(r"^[-*]\s+", lines[i]) and not re.match(r"^\d+\.\s+", lines[i]) and "|" not in lines[i]:
            paras.append(lines[i])
            i += 1
        blocks.append({"type": "p", "text": " ".join(paras)})
    return blocks


def split_sections(blocks: list[dict]) -> dict:
    title = None
    intro: list[dict] = []
    sections: list[dict] = []
    current = None
    for b in blocks:
        if b["type"] == "heading" and b["level"] == 1:
            title = b["text"]
            continue
        if b["type"] == "heading" and b["level"] == 2:
            current = {"heading": b["text"], "blocks": []}
            sections.append(current)
            continue
        if current is None:
            intro.append(b)
        else:
            current["blocks"].append(b)
    return {"title": title, "intro": intro, "sections": sections}


def extract_faqs(sections: list[dict]) -> tuple[list[dict], list[dict]]:
    faqs = []
    remaining = []
    for sec in sections:
        h = sec["heading"].lower()
        if "frequently asked" in h or h.strip() == "faq" or h.startswith("faq"):
            q = None
            for b in sec["blocks"]:
                if b["type"] == "heading" and b["level"] == 3:
                    if q:
                        faqs.append(q)
                    q = {"q": b["text"], "a": []}
                elif q is not None:
                    q["a"].append(b)
            if q:
                faqs.append(q)
        else:
            remaining.append(sec)
    return remaining, faqs


def blocks_to_html(blocks: list[dict]) -> str:
    parts = []
    for b in blocks:
        if b["type"] == "p":
            parts.append(f"<p>{inline_md(b['text'])}</p>")
        elif b["type"] == "heading":
            tag = f"h{b['level']}"
            parts.append(f"<{tag}>{inline_md(b['text'])}</{tag}>")
        elif b["type"] == "ul":
            items = "".join(f"<li>{inline_md(it)}</li>" for it in b["items"])
            parts.append(f"<ul>{items}</ul>")
        elif b["type"] == "ol":
            items = "".join(f"<li>{inline_md(it)}</li>" for it in b["items"])
            parts.append(f"<ol>{items}</ol>")
        elif b["type"] == "table":
            rows = b["rows"]
            if not rows:
                continue
            thead = "<thead><tr>" + "".join(f"<th>{inline_md(c)}</th>" for c in rows[0]) + "</tr></thead>"
            body_rows = ""
            for r in rows[1:]:
                body_rows += "<tr>" + "".join(f"<td>{inline_md(c)}</td>" for c in r) + "</tr>"
            parts.append(f"<table>{thead}<tbody>{body_rows}</tbody></table>")
    return "\n".join(parts)


def first_paragraph(blocks: list[dict]) -> str:
    for b in blocks:
        if b["type"] == "p":
            return b["text"]
    return ""


def checklist_from_blocks(blocks: list[dict], limit: int = 5) -> list[str]:
    for b in blocks:
        if b["type"] in ("ul", "ol"):
            return b["items"][:limit]
    return []


def all_list_items(blocks: list[dict]) -> list[str]:
    items = []
    for b in blocks:
        if b["type"] in ("ul", "ol"):
            items.extend(b["items"])
    return items


def paragraphs(blocks: list[dict]) -> list[str]:
    return [b["text"] for b in blocks if b["type"] == "p"]


def find_section(sections: list[dict], *keywords: str):
    for sec in sections:
        h = sec["heading"].lower()
        if all(k.lower() in h for k in keywords):
            return sec
    for sec in sections:
        h = sec["heading"].lower()
        if any(k.lower() in h for k in keywords):
            return sec
    return None


def parse_ol_steps(blocks: list[dict]) -> list[tuple[str, str]]:
    steps = []
    for b in blocks:
        if b["type"] == "ol":
            for it in b["items"]:
                m = re.match(r"\*\*([^*]+)\*\*:?\s*(.*)", it)
                if m:
                    steps.append((m.group(1).strip(), m.group(2).strip() or m.group(1).strip()))
                else:
                    steps.append((it[:60], it))
    return steps
