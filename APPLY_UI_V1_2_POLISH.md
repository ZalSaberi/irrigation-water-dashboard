# UI v1.2 Polish Patch

This patch applies the requested visual/layout refinements:

- Larger and more readable English text in the sidebar.
- Sidebar navigation typography increased and right-aligned.
- The water droplet brand icon is removed; the sidebar brand uses the wordmark only.
- Dashboard filter controls are centered.
- KPI cards are compacted to help the dashboard fit within one screen.
- The main window opens to the available screen size and is fixed.
- Dashboard page no longer uses a scroll area for the main content.
- Recent samples area is compacted to maintain a one-screen dashboard layout.

Apply from repository root:

```bash
unzip -o grovity_irrigation_water_ui_v1_2_polish.zip -d .
python -m pytest -q
python -m aqualog
```
