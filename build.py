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
    ]
    seen = set()
    unique = []
    for s in IMAGE_SLOTS:
        if s["slot"] in seen:
            continue
        seen.add(s["slot"])
        unique.append(s)
    lines.append(f"Total slots: **{len(unique)}**\n\n")
    lines.append("| # | Suggested file | Page | Subject | Aspect |\n")
    lines.append("|---|----------------|------|---------|--------|\n")
    for i, s in enumerate(unique, 1):
        lines.append(f"| {i} | `{s['suggested']}` | {s['page']} | {s['subject']} | {s['aspect']} |\n")

    cats = {"Hero": 0, "About/stack": 0, "Service card": 0, "Process": 0, "Emergency/CTA": 0, "Detail/area": 0, "Other": 0}
    for s in unique:
        slot = s["slot"]
        if "hero" in slot:
            cats["Hero"] += 1
        elif "about" in slot or "what-matters" in slot or "team" in slot:
            cats["About/stack"] += 1
        elif "card" in slot or slot.startswith("home-service") or slot.startswith("services-card"):
            cats["Service card"] += 1
        elif "process" in slot:
            cats["Process"] += 1
        elif "emergency" in slot or "banner" in slot:
            cats["Emergency/CTA"] += 1
        elif "detail" in slot or "area-" in slot:
            cats["Detail/area"] += 1
        else:
            cats["Other"] += 1
    lines.append("\n## Categories\n\n")
    for k, v in cats.items():
        lines.append(f"- **{k}:** {v}\n")
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
