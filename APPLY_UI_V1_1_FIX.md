# UI v1.1 RTL + Windows Chart Fix

This patch fixes two issues visible in the first Windows run:

1. The global RTL setting mirrored the application shell twice, placing the
   sidebar and Persian header on the wrong physical side.
2. `datetime.timestamp()` may fail on Windows for pre-1970 dates. The RFP
   dataset contains samples from the 1960s, which caused the Dashboard to enter
   its error state while rendering the trend chart.

Additional improvements:
- Dashboard error state now shows the actual exception text.
- Database badge changes to error when a dashboard query/render fails.
- Filter reset performs one refresh instead of several.
- KPI physical order is made deterministic under global RTL.

Apply from the repository root:

```bash
unzip -o grovity_irrigation_water_ui_v1_1_fix.zip -d .
python -m pytest -q
python -m aqualog
```
