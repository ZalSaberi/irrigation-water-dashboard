# UI v1.6 — Main Title + Sidebar Logo Position

## Required logo path

From the project root, place the real logo here:

`src/aqualog/resources/images/grovity_logo.png`

The filename must be exactly:

`grovity_logo.png`

Recommended:
- PNG
- transparent background
- wide logo aspect ratio
- at least 800 px wide

The UI will display it centered inside the lower sidebar card at approximately 200 x 100 px while preserving aspect ratio.

## Changes

- Adds the fixed Persian title:
  `پایش و تحلیل داده‌های کیفیت آب آبیاری`
  in the requested upper-left main header position.
- Removes the failed header-logo placement.
- Adds a dedicated Grovity logo card under Development Team in the sidebar.
- The logo card automatically hides itself if the expected image file is missing.

Apply:

```bash
unzip -o grovity_irrigation_water_ui_v1_6_title_sidebar_logo.zip -d .
python -m pytest -q
python -m aqualog
```
