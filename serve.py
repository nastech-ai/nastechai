import http.server
import socketserver
import os
import tempfile
import pathlib
import base64

PORT = 5000
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "web")

LOGO_B64 = (
    "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"
    "YII="
)

PLACEHOLDER_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NasTech AI</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
    }}
    .card {{
      background: rgba(255,255,255,0.05);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 24px;
      padding: 56px 48px;
      max-width: 520px;
      width: 90%;
      text-align: center;
      box-shadow: 0 24px 64px rgba(0,0,0,.5);
    }}
    .logo {{
      width: 96px;
      height: 96px;
      border-radius: 22px;
      margin: 0 auto 24px;
      display: block;
      border: 2px solid rgba(220,30,30,0.3);
      box-shadow: 0 0 32px rgba(220,30,30,0.2);
    }}
    h1 {{
      font-size: 2rem;
      font-weight: 700;
      color: #fff;
      letter-spacing: -0.5px;
      margin-bottom: 6px;
    }}
    .tagline {{
      color: #dc1e1e;
      font-weight: 600;
      font-size: 0.95rem;
      letter-spacing: 1px;
      text-transform: uppercase;
      margin-bottom: 28px;
    }}
    .divider {{
      height: 1px;
      background: rgba(255,255,255,0.08);
      margin: 0 0 28px;
    }}
    p {{
      color: rgba(255,255,255,0.55);
      line-height: 1.8;
      font-size: 0.95rem;
    }}
    code {{
      background: rgba(220,30,30,0.15);
      color: #ff6b6b;
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 0.85em;
      font-family: 'SF Mono', 'Fira Code', monospace;
    }}
    .step {{
      display: flex;
      align-items: flex-start;
      gap: 12px;
      text-align: left;
      margin-top: 16px;
      padding: 14px 16px;
      background: rgba(255,255,255,0.03);
      border-radius: 12px;
      border: 1px solid rgba(255,255,255,0.05);
    }}
    .step-num {{
      background: #dc1e1e;
      color: #fff;
      font-size: 0.75rem;
      font-weight: 700;
      width: 22px;
      height: 22px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      margin-top: 1px;
    }}
    .step p {{ margin: 0; font-size: 0.88rem; }}
    .footer {{
      margin-top: 32px;
      color: rgba(255,255,255,0.2);
      font-size: 0.78rem;
    }}
  </style>
</head>
<body>
  <div class="card">
    <img class="logo" src="data:image/png;base64,{LOGO_B64}" alt="NasTech AI Logo">
    <h1>NasTech AI</h1>
    <div class="tagline">LLM Chat Client</div>
    <div class="divider"></div>
    <p>The Flutter web app needs to be compiled first.</p>
    <div class="step">
      <div class="step-num">1</div>
      <p>Push to GitHub — the <code>build-web</code> workflow compiles the app automatically.</p>
    </div>
    <div class="step">
      <div class="step-num">2</div>
      <p>Pull the changes — <code>build/web/</code> will appear in the repo.</p>
    </div>
    <div class="step">
      <div class="step-num">3</div>
      <p>The app loads here instantly — no other steps needed.</p>
    </div>
    <div class="footer">© 2026 NasTech AI · com.nastechai.app</div>
  </div>
</body>
</html>"""


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
    print(f"WARNING: build/web not found — serving placeholder.")
    tmp = tempfile.mkdtemp()
    pathlib.Path(tmp, "index.html").write_text(PLACEHOLDER_HTML)
    WEB_DIR = tmp

os.chdir(WEB_DIR)

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"NasTech AI running on http://0.0.0.0:{PORT}")
    httpd.serve_forever()
