# Sewage Fix Pros — North Richland Hills Sewage Cleanup

Static multi-page site matching the Leak Fix Pros (San Jacinto) layout/design system, with NRH sewage-cleanup content only.

## Branding
- **Business:** Sewage Fix Pros
- **Phone:** (817) 204-3891 (`tel:8172043891`)
- **Address:** 6200 Rufe Snow Dr, North Richland Hills, TX 76180
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
