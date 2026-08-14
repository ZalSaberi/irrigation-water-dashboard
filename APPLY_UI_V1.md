# Grovity Irrigation Water — UI V1

1. Extract this overlay in the repository root.
2. Copy your local Shabnam files into `src/aqualog/resources/fonts/`.
3. Activate the virtual environment.
4. Install GUI dependencies:

   `python -m pip install -r requirements-gui.txt --timeout 60 --retries 10 --prefer-binary`

5. Keep the package installed editable:

   `python -m pip install -e . --no-deps`

6. Run all backend tests:

   `python -m pytest -q`

7. Start GUI:

   `python -m aqualog`

The app opens with the local SQLite database at `data/database/aqualog.sqlite3`. Import the RFP fixture from the Analysis page if the database is empty.
