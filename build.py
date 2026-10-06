#!/usr/bin/env python3
"""Generate Sewage Fix Pros static site from NRH markdown + reference layout."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "_gen"))

from mdutil import (
    CONTENT_DIR, OUT_DIR, AREA_META, IMAGE_SLOTS, BRAND, PHONE_DISPLAY, PHONE_TEL, ADDRESS,
    phone_sub, parse_frontmatter, md_to_blocks, split_sections, page_path,
)
from pages_home import build_home
from pages_inner import (
    build_service, build_services_index, build_areas_index, build_area,
    build_about, build_contact, build_legal,
)


def area_name_from_doc(doc: dict, url: str) -> str:
    t = doc.get("title") or ""
    t = t.replace("Sewage Cleanup in ", "").replace(", North Richland Hills", "").strip()
    if t:
        return t
    slug = url.strip("/").split("/")[-1]
    return slug.replace("-", " ").title()


def load_all() -> list[dict]:
    files = sorted(CONTENT_DIR.rglob("*.md"))
    pages = []
    for f in files:
        raw = f.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(raw)
        meta = {k: phone_sub(v) for k, v in meta.items()}
        blocks = md_to_blocks(body)
        doc = split_sections(blocks)
        url = meta.get("url", "/")
        pages.append({"file": f, "meta": meta, "doc": doc, "url": url})
    return pages


def write_checklist():
    lines = [
        "# Image Checklist — Sewage Fix Pros (NRH)\n\n",
        "Replace each placeholder `div.img-placeholder` with a real WebP/JPEG at the suggested path.\n\n",
        "Pages share a small reusable library of **12** files under `assets/images/*.webp`.\n\n",
    ]
    seen = set()
    unique = []
    pages_by_file: dict[str, list[str]] = {}
    for s in IMAGE_SLOTS:
        key = s["suggested"]
        pages_by_file.setdefault(key, [])
        if s["page"] not in pages_by_file[key]:
            pages_by_file[key].append(s["page"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(s)
    lines.append(f"Total unique files: **{len(unique)}**\n\n")
    lines.append("| # | Suggested file | Example page | Subject | Aspect |\n")
    lines.append("|---|----------------|--------------|---------|--------|\n")
    for i, s in enumerate(unique, 1):
        lines.append(f"| {i} | `{s['suggested']}` | {s['page']} | {s['subject']} | {s['aspect']} |\n")

    cats = {"Hero": 0, "Portrait": 0, "Service card": 0, "Process": 0, "Detail": 0, "Other": 0}
    for s in unique:
        slot = s["slot"]
        if "hero" in slot:
            cats["Hero"] += 1
        elif "portrait" in slot:
            cats["Portrait"] += 1
        elif "card" in slot:
            cats["Service card"] += 1
        elif "process" in slot:
            cats["Process"] += 1
        elif "detail" in slot:
            cats["Detail"] += 1
        else:
            cats["Other"] += 1
    lines.append("\n## Categories\n\n")
    for k, v in cats.items():
        lines.append(f"- **{k}:** {v}\n")

    lines.append("\n## Reuse map\n\n")
    lines.append("Each file is reused across many pages/slots. Place the photo once; every matching placeholder points at the same path.\n\n")
    reuse_notes = {
        "shared-hero.webp": "Default page heroes (home, about, contact, services, areas, most service & area heroes, legal)",
        "shared-hero-emergency.webp": "Emergency banner + emergency-sewage-cleanup hero",
        "shared-portrait.webp": "About/image stacks, about-team, service-about portraits",
        "shared-portrait-ppe.webp": "Containment/PPE (home-what-matters)",
        "shared-process.webp": "All process sections sitewide (+ non-mapped service cards)",
        "shared-card-backup.webp": "Sewage backup service cards",
        "shared-card-emergency.webp": "Emergency service cards",
        "shared-card-toilet.webp": "Toilet overflow / bathroom-related cards",
        "shared-detail-extraction.webp": "Detail shot 0 (index % 4)",
        "shared-detail-removal.webp": "Detail shot 1 (index % 4)",
        "shared-detail-disinfect.webp": "Detail shot 2 (index % 4)",
        "shared-detail-drying.webp": "Detail shot 3 (index % 4)",
    }
    for s in unique:
        name = Path(s["suggested"]).name
        note = reuse_notes.get(name, "")
        pages = ", ".join(pages_by_file[s["suggested"]][:8])
        more = len(pages_by_file[s["suggested"]]) - 8
        page_note = pages + (f", …(+{more} more)" if more > 0 else "")
        lines.append(f"- **`{s['suggested']}`** — {note}. Pages: {page_note}\n")

    lines.append("\n## Notes\n\n")
    lines.append("- Accent brand color is orange `#f15a1b`—avoid blue-tinted stock.\n")
    lines.append("- Prefer real NRH crew / Category 3 PPE / extraction equipment photography.\n")
    lines.append("- Do not use Leak Fix Pros or San Jacinto reference photos.\n")
    (OUT_DIR / "IMAGE_CHECKLIST.md").write_text("".join(lines), encoding="utf-8")
    return len(unique), cats


def write_readme():
    readme = f'''# Sewage Fix Pros — North Richland Hills Sewage Cleanup

Static multi-page site matching the Leak Fix Pros (San Jacinto) layout/design system, with NRH sewage-cleanup content only.

## Branding
- **Business:** {BRAND}
- **Phone:** {PHONE_DISPLAY} (`tel:{PHONE_TEL}`)
- **Address:** {ADDRESS}
- **Accent:** `#f15a1b` (orange)

## Preview locally

From this directory:

```bash
cd /workspace/nrh-site
python3 -m http.server 8080
```

Then open http://127.0.0.1:8080/

Or open `index.html` directly in a browser (absolute `/` links work best via a local server).

## Rebuild

```bash
python3 build.py
```

Content source: `/workspace/nrh-build/nrh-content/`  
Design reference: `/workspace/nrh-build/ref-site/`

## Structure
- `assets/global.css` — design tokens & components (DM Sans / Manrope, orange accent)
- `assets/fonts/` — self-hosted fonts
- `assets/js/main.js` — mobile nav + FAQ accordion + process UI
- Trailing-slash URLs as `path/index.html`

## Images
See `IMAGE_CHECKLIST.md`. Placeholders are labeled gray blocks until real photos are added.
'''
    (OUT_DIR / "README.md").write_text(readme, encoding="utf-8")


def main():
    IMAGE_SLOTS.clear()
    AREA_META.clear()
    pages = load_all()

    for p in pages:
        if p["url"].startswith("/areas/") and p["url"] != "/areas/":
            AREA_META.append({"url": p["url"], "name": area_name_from_doc(p["doc"], p["url"])})
    AREA_META.sort(key=lambda a: a["name"])

    count = 0
    for p in pages:
        url = p["url"]
        meta, doc = p["meta"], p["doc"]
        if url == "/":
            html_out = build_home(doc, meta)
        elif url == "/services/":
            html_out = build_services_index(doc, meta)
        elif url == "/areas/":
            html_out = build_areas_index(doc, meta)
        elif url == "/about/":
            html_out = build_about(doc, meta)
        elif url == "/contact/":
            html_out = build_contact(doc, meta)
        elif url in ("/privacy-policy/", "/terms/"):
            html_out = build_legal(doc, meta, url)
        elif url.startswith("/areas/"):
            html_out = build_area(doc, meta, url)
        else:
            html_out = build_service(doc, meta, url)

        out = page_path(url)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html_out, encoding="utf-8")
        count += 1
        print(f"Wrote {out.relative_to(OUT_DIR)}")

    n_slots, cats = write_checklist()
    write_readme()
    print(f"\nDone. {count} HTML pages. {n_slots} unique image slots.")
    print("Categories:", cats)


if __name__ == "__main__":
    main()
