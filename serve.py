import http.server
import socketserver
import os
import tempfile
import pathlib

PORT = 5000
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "web")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def log_message(self, format, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("X-Frame-Options", "ALLOWALL")
        super().end_headers()

if not os.path.isdir(WEB_DIR):
    print(f"WARNING: '{WEB_DIR}' not found — app not built yet.")
    print("Push to GitHub to trigger the CI build, then pull the result.")
    print("Serving placeholder page instead.")

    tmp = tempfile.mkdtemp()
    pathlib.Path(tmp, "index.html").write_text("""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>NasTech AI - Building...</title>
<style>
  body { font-family: system-ui, sans-serif; display: flex; align-items: center;
         justify-content: center; height: 100vh; margin: 0; background: #f0f4ff; }
  .card { background: white; border-radius: 16px; padding: 48px 40px; max-width: 500px;
          box-shadow: 0 4px 24px rgba(0,0,0,.08); text-align: center; }
  h1 { margin: 0 0 8px; font-size: 2rem; color: #1a1a2e; }
  .sub { color: #0175C2; font-weight: 600; margin-bottom: 20px; }
  p { color: #555; line-height: 1.7; }
  code { background: #eef2ff; color: #3730a3; padding: 2px 7px;
         border-radius: 5px; font-size: .88em; }
</style>
</head>
<body>
<div class="card">
  <h1>NasTech AI</h1>
  <div class="sub">LLM Chat Client</div>
  <p>The Flutter web app hasn't been built yet.</p>
  <p>Push your code to GitHub — the <code>build-web</code> CI workflow will compile it
     and commit <code>build/web/</code> back to the repo. Pull those changes and
     the app will load here automatically.</p>
</div>
</body>
</html>""")
    WEB_DIR = tmp

os.chdir(WEB_DIR)

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Serving NasTech AI on http://0.0.0.0:{PORT}")
    print(f"Serving from: {WEB_DIR}")
    httpd.serve_forever()
