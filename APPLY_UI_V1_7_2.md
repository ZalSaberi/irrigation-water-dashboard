# UI v1.7.2 — KPI Visual Polish

This patch only targets the four top KPI cards.

Changes:
- icon, label and number are aligned on one deliberate horizontal composition
- icons are enlarged to 22px inside 44px holders
- all KPI icons use the same Grovity teal/cyan color family
- numbers are larger (25px) and labels are larger (14px)
- internal padding and spacing are tightened to eliminate accidental-looking empty space
- the "needs attention" explanation remains as compact secondary text

Apply:

```bash
unzip -o grovity_irrigation_water_ui_v1_7_2_kpi_polish.zip -d .
python -m pytest -q
python -m aqualog
```
