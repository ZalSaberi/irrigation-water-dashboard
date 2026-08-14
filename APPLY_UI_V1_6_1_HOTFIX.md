# UI v1.6.1 Hotfix

Fixes the startup error:

`NameError: name 'font' is not defined`

Cause:
The QSS is built inside a Python f-string. Two newly-added style blocks used single
`{ ... }` braces instead of escaped `{{ ... }}` braces, so Python tried to parse
`font-size` as an f-string expression.

This patch:
- fixes both QSS blocks
- adds a regression test that calls `build_stylesheet()` directly

Apply:

```bash
unzip -o grovity_irrigation_water_ui_v1_6_1_hotfix.zip -d .
python -m pytest -q
python -m aqualog
```
