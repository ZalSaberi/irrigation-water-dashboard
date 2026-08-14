# UI v1.7.1 — RTL section headers fix

The previous patch used `AlignRight`, but some `QHBoxLayout`s still inherited the
application-wide RTL direction. Qt therefore mirrored the child order and several
section-title blocks still appeared on the physical left.

This patch fixes that at the layout level:
- Dashboard: overall-status, trend and recent-samples headers are physically right-aligned.
- Analysis: result, overall status, infiltration-risk and input-form headers are physically right-aligned.
- Archive: archive section header is physically right-aligned.
- Field wrappers in the analysis form are explicitly RTL.

Apply from project root:

```bash
unzip -o grovity_irrigation_water_ui_v1_7_1_rtl_headers_fix.zip -d .
python -m pytest -q
python -m aqualog
```
