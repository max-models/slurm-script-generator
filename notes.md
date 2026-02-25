# 

```

# How to run the Pyodide demo page

1. Build your Python wheel (if needed):

   ```sh
   python -m pip install build
   python -m build
   ```
   This creates a .whl file in the dist/ directory.

2. Start a local server with CORS enabled (so the browser can fetch the wheel):

   ```sh
   python3 serve_cors.py 8890
   ```

3. Open index.html in your browser (file:///... or http://localhost:8890/index.html).

4. You should see the output from the hardcoded Python code (e.g., 'hello world').

5. If you change your Python code or wheel, rebuild the wheel and hard-refresh the browser (Ctrl+Shift+R).
python -m pip install build
python -m build
```