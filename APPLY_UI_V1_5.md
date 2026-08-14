# UI v1.5 — Sidebar + Header + Fill Fix

This patch applies the latest requested refinements:

- removes the "فضای کاری" label
- makes the 3 sidebar navigation items large boxed buttons
- uses the middle sidebar space for the 3 buttons and keeps Development Team at the bottom
- replaces the top main title area with the Grovity logo
- expands dashboard content to use the available width instead of leaving large outer gaps
- slightly increases chart/table heights to use the page better

Apply from the repository root:

```bash
unzip -o grovity_irrigation_water_ui_v1_5_sidebar_header_fix.zip -d .
python -m pytest -q
python -m aqualog
```
