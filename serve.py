import http.server
import socketserver
import os
import tempfile
import pathlib
import base64

PORT = 5000
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "web")

def _load_icon():
    icon_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "app_icon_2.png"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "web", "icons", "Icon-512.png"),
    ]
    for p in icon_paths:
        if os.path.isfile(p):
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return ""

LOGO_B64 = _load_icon()

LANDING_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NasTech AI — LLM Chat Client</title>
  <meta name="description" content="NasTech AI is a powerful LLM chat client available on iOS, macOS, Windows, Linux, and Web.">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --red: #dc1e1e;
      --red-dim: rgba(220,30,30,0.18);
      --red-glow: rgba(220,30,30,0.35);
      --bg: #080810;
      --bg2: #0f0f1a;
      --surface: rgba(255,255,255,0.04);
      --border: rgba(255,255,255,0.08);
      --text: #f0f0f4;
      --muted: rgba(255,255,255,0.45);
      --radius: 18px;
    }}

    html {{ scroll-behavior: smooth; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      overflow-x: hidden;
    }}

    /* NAV */
    nav {{
      position: fixed; top: 0; left: 0; right: 0; z-index: 100;
      display: flex; align-items: center; justify-content: space-between;
      padding: 0 40px;
      height: 64px;
      background: rgba(8,8,16,0.85);
      backdrop-filter: blur(20px);
      border-bottom: 1px solid var(--border);
    }}
    .nav-brand {{
      display: flex; align-items: center; gap: 10px;
      font-size: 1.1rem; font-weight: 700; color: var(--text); text-decoration: none;
    }}
    .nav-brand img {{
      width: 32px; height: 32px; border-radius: 8px;
    }}
    .nav-links {{
      display: flex; gap: 32px; list-style: none;
    }}
    .nav-links a {{
      color: var(--muted); text-decoration: none; font-size: 0.9rem;
      transition: color 0.2s;
    }}
    .nav-links a:hover {{ color: var(--text); }}

    /* HERO */
    .hero {{
      min-height: 100vh;
      display: flex; flex-direction: column;
      align-items: center; justify-content: center;
      text-align: center;
      padding: 100px 24px 60px;
      background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(220,30,30,0.12) 0%, transparent 70%),
                  linear-gradient(180deg, #080810 0%, #0f0f1a 100%);
      position: relative;
    }}
    .hero::before {{
      content: '';
      position: absolute; inset: 0;
      background: radial-gradient(ellipse 60% 40% at 50% 100%, rgba(220,30,30,0.06) 0%, transparent 70%);
      pointer-events: none;
    }}
    .hero-logo {{
      width: 120px; height: 120px;
      border-radius: 28px;
      border: 2px solid rgba(220,30,30,0.4);
      box-shadow: 0 0 60px rgba(220,30,30,0.25), 0 20px 60px rgba(0,0,0,0.6);
      margin-bottom: 32px;
      position: relative; z-index: 1;
    }}
    .badge {{
      display: inline-block;
      background: var(--red-dim);
      color: var(--red);
      border: 1px solid rgba(220,30,30,0.3);
      border-radius: 999px;
      padding: 4px 14px;
      font-size: 0.78rem;
      font-weight: 600;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      margin-bottom: 20px;
    }}
    h1 {{
      font-size: clamp(2.4rem, 6vw, 4.2rem);
      font-weight: 800;
      letter-spacing: -1.5px;
      line-height: 1.08;
      margin-bottom: 20px;
      background: linear-gradient(135deg, #fff 40%, rgba(220,30,30,0.8) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }}
    .hero-sub {{
      font-size: clamp(1rem, 2.5vw, 1.2rem);
      color: var(--muted);
      max-width: 560px;
      line-height: 1.7;
      margin-bottom: 44px;
    }}

    /* DOWNLOAD BUTTONS */
    .dl-grid {{
      display: flex; flex-wrap: wrap; gap: 12px;
      justify-content: center;
      margin-bottom: 24px;
    }}
    .dl-btn {{
      display: flex; align-items: center; gap: 10px;
      padding: 13px 22px;
      border-radius: 13px;
      border: 1px solid var(--border);
      background: var(--surface);
      color: var(--text);
      text-decoration: none;
      font-size: 0.92rem;
      font-weight: 600;
      transition: background 0.2s, border-color 0.2s, transform 0.15s, box-shadow 0.2s;
      cursor: pointer;
    }}
    .dl-btn:hover {{
      background: rgba(255,255,255,0.08);
      border-color: rgba(220,30,30,0.5);
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(220,30,30,0.2);
    }}
    .dl-btn svg {{ flex-shrink: 0; }}
    .dl-btn .btn-label {{ display: flex; flex-direction: column; text-align: left; }}
    .dl-btn .btn-sub {{ font-size: 0.72rem; font-weight: 400; color: var(--muted); }}

    .dl-btn.primary {{
      background: var(--red);
      border-color: transparent;
    }}
    .dl-btn.primary:hover {{
      background: #f02020;
      box-shadow: 0 8px 32px rgba(220,30,30,0.4);
    }}

    .version-note {{
      font-size: 0.8rem;
      color: var(--muted);
    }}
    .version-note span {{ color: rgba(220,30,30,0.8); }}

    /* DIVIDER */
    .section-divider {{
      height: 1px;
      background: var(--border);
      margin: 0 40px;
    }}

    /* FEATURES */
    .section {{
      padding: 80px 24px;
      max-width: 1100px;
      margin: 0 auto;
    }}
    .section-label {{
      text-align: center;
      color: var(--red);
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 2px;
      text-transform: uppercase;
      margin-bottom: 12px;
    }}
    .section-title {{
      text-align: center;
      font-size: clamp(1.6rem, 4vw, 2.4rem);
      font-weight: 800;
      letter-spacing: -0.5px;
      margin-bottom: 48px;
    }}

    .features-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 20px;
    }}
    .feature-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 28px 24px;
      transition: border-color 0.2s, transform 0.2s;
    }}
    .feature-card:hover {{
      border-color: rgba(220,30,30,0.35);
      transform: translateY(-3px);
    }}
    .feature-icon {{
      width: 44px; height: 44px;
      background: var(--red-dim);
      border-radius: 12px;
      display: flex; align-items: center; justify-content: center;
      margin-bottom: 16px;
      font-size: 1.4rem;
    }}
    .feature-card h3 {{
      font-size: 1.05rem; font-weight: 700; margin-bottom: 8px;
    }}
    .feature-card p {{
      font-size: 0.88rem; color: var(--muted); line-height: 1.65;
    }}

    /* PLATFORMS */
    .platforms-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
    }}
    .platform-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 28px 20px;
      text-align: center;
      text-decoration: none;
      color: var(--text);
      transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
      display: flex; flex-direction: column; align-items: center; gap: 12px;
    }}
    .platform-card:hover {{
      border-color: rgba(220,30,30,0.5);
      transform: translateY(-4px);
      box-shadow: 0 12px 40px rgba(220,30,30,0.15);
    }}
    .platform-icon {{
      font-size: 2.4rem;
      line-height: 1;
    }}
    .platform-card h3 {{
      font-size: 1rem; font-weight: 700;
    }}
    .platform-card p {{
      font-size: 0.8rem; color: var(--muted);
    }}
    .platform-card .platform-badge {{
      display: inline-block;
      background: var(--red-dim);
      color: var(--red);
      border: 1px solid rgba(220,30,30,0.25);
      border-radius: 999px;
      padding: 2px 10px;
      font-size: 0.7rem;
      font-weight: 600;
    }}
    .platform-badge.soon {{
      background: rgba(255,255,255,0.04);
      color: var(--muted);
      border-color: var(--border);
    }}

    /* SCREENSHOTS / DEMO */
    .demo-area {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 24px;
      overflow: hidden;
      padding: 48px 32px;
      text-align: center;
    }}
    .demo-screen {{
      background: var(--bg2);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 32px 24px;
      max-width: 640px;
      margin: 0 auto;
      font-size: 0.88rem;
      color: var(--muted);
      line-height: 1.8;
    }}
    .chat-msg {{
      display: flex; gap: 12px; margin-bottom: 16px; text-align: left;
    }}
    .chat-msg.user {{ flex-direction: row-reverse; }}
    .chat-avatar {{
      width: 34px; height: 34px; border-radius: 50%; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
      font-size: 0.9rem; font-weight: 700;
    }}
    .chat-msg.ai .chat-avatar {{ background: var(--red-dim); color: var(--red); }}
    .chat-msg.user .chat-avatar {{ background: rgba(255,255,255,0.08); color: var(--text); }}
    .chat-bubble {{
      background: rgba(255,255,255,0.05);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 10px 14px;
      max-width: 80%;
      font-size: 0.85rem;
      color: var(--text);
      line-height: 1.6;
    }}
    .chat-msg.user .chat-bubble {{
      background: var(--red-dim);
      border-color: rgba(220,30,30,0.2);
    }}

    /* FOOTER */
    footer {{
      border-top: 1px solid var(--border);
      padding: 40px 40px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
      color: var(--muted);
      font-size: 0.82rem;
    }}
    .footer-brand {{
      display: flex; align-items: center; gap: 8px;
      font-weight: 600; color: var(--text);
    }}
    .footer-brand img {{ width: 24px; height: 24px; border-radius: 6px; }}

    /* RESPONSIVE */
    @media (max-width: 600px) {{
      nav {{ padding: 0 20px; }}
      .nav-links {{ display: none; }}
      footer {{ flex-direction: column; text-align: center; }}
    }}
  </style>
</head>
<body>

<!-- NAV -->
<nav>
  <a class="nav-brand" href="#">
    {"<img src='data:image/png;base64," + LOGO_B64 + "' alt='NasTech AI'>" if LOGO_B64 else ""}
    NasTech AI
  </a>
  <ul class="nav-links">
    <li><a href="#features">Features</a></li>
    <li><a href="#platforms">Platforms</a></li>
    <li><a href="#download">Download</a></li>
  </ul>
</nav>

<!-- HERO -->
<section class="hero">
  {"<img class='hero-logo' src='data:image/png;base64," + LOGO_B64 + "' alt='NasTech AI Logo'>" if LOGO_B64 else ""}
  <div class="badge">v1.1.17 &nbsp;·&nbsp; LLM Chat Client</div>
  <h1>Your AI Assistant,<br>Everywhere You Are</h1>
  <p class="hero-sub">
    NasTech AI brings powerful large language models to every device —
    iOS, macOS, Windows, Linux, and the web. One app, all platforms.
  </p>

  <div class="dl-grid" id="download">
    <a class="dl-btn primary" href="https://apps.apple.com" target="_blank">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="white"><path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/></svg>
      <span class="btn-label">
        <span class="btn-sub">Download on the</span>
        App Store
      </span>
    </a>
    <a class="dl-btn" href="https://github.com/nastech-ai/nastechai/releases" target="_blank">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M21 2H3C1.9 2 1 2.9 1 4v16l4-4h16c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-9 9h-2V5h2v6zm0 4h-2v-2h2v2z" fill="rgba(255,255,255,0.7)"/></svg>
      <span class="btn-label">
        <span class="btn-sub">Download for</span>
        Windows &amp; Linux
      </span>
    </a>
    <a class="dl-btn" href="https://github.com/nastech-ai/nastechai/releases" target="_blank">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="rgba(255,255,255,0.7)"><path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/></svg>
      <span class="btn-label">
        <span class="btn-sub">Download for</span>
        macOS
      </span>
    </a>
    <a class="dl-btn" href="#web-app">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="rgba(255,255,255,0.7)"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
      <span class="btn-label">
        <span class="btn-sub">Open in browser</span>
        Web App
      </span>
    </a>
  </div>
  <p class="version-note">Version <span>1.1.17</span> · Free &amp; open source · com.nastechai.app</p>
</section>

<!-- FEATURES -->
<div class="section-divider"></div>
<div class="section" id="features">
  <p class="section-label">What's inside</p>
  <h2 class="section-title">Everything you need from an AI client</h2>
  <div class="features-grid">
    <div class="feature-card">
      <div class="feature-icon">🤖</div>
      <h3>Multiple LLM Providers</h3>
      <p>Connect to OpenAI, SiliconFlow, and other providers. Switch models on the fly without losing your conversation.</p>
    </div>
    <div class="feature-card">
      <div class="feature-icon">💬</div>
      <h3>Conversation Management</h3>
      <p>Organise chats into folders, search across all history, and continue from any device with cloud sync.</p>
    </div>
    <div class="feature-card">
      <div class="feature-icon">🧠</div>
      <h3>Custom Assistants</h3>
      <p>Create assistants with custom system prompts, avatars, and model settings for any use case.</p>
    </div>
    <div class="feature-card">
      <div class="feature-icon">🔌</div>
      <h3>MCP Support</h3>
      <p>Model Context Protocol integration lets your AI use tools, search the web, and run code.</p>
    </div>
    <div class="feature-card">
      <div class="feature-icon">🎙️</div>
      <h3>Voice & TTS</h3>
      <p>Talk to your assistant using voice input. Listen to responses with built-in text-to-speech.</p>
    </div>
    <div class="feature-card">
      <div class="feature-icon">🌐</div>
      <h3>Fully Cross-Platform</h3>
      <p>One codebase, five platforms. iOS, macOS, Windows, Linux, and the web — all with a native feel.</p>
    </div>
  </div>
</div>

<!-- DEMO CHAT -->
<div class="section">
  <div class="demo-area">
    <p class="section-label" style="margin-bottom:8px;">See it in action</p>
    <h2 class="section-title" style="margin-bottom:32px;">Intelligent conversations, beautifully simple</h2>
    <div class="demo-screen">
      <div class="chat-msg ai">
        <div class="chat-avatar">N</div>
        <div class="chat-bubble">Hello! I'm your NasTech AI assistant. How can I help you today?</div>
      </div>
      <div class="chat-msg user">
        <div class="chat-avatar">You</div>
        <div class="chat-bubble">Explain how neural networks learn in simple terms.</div>
      </div>
      <div class="chat-msg ai">
        <div class="chat-avatar">N</div>
        <div class="chat-bubble">Think of a neural network like a student taking an exam. It makes a guess, checks how wrong it was, and adjusts what it knows — millions of times — until the guesses get really good. That process of adjusting is called <em>backpropagation</em>, and the measuring of wrongness is the <em>loss function</em>.</div>
      </div>
      <div class="chat-msg user">
        <div class="chat-avatar">You</div>
        <div class="chat-bubble">That makes sense. Can you give a code example too?</div>
      </div>
      <div class="chat-msg ai">
        <div class="chat-avatar">N</div>
        <div class="chat-bubble">Of course! Here's a minimal PyTorch example showing the training loop… ✨</div>
      </div>
    </div>
  </div>
</div>

<!-- PLATFORMS -->
<div class="section-divider"></div>
<div class="section" id="platforms">
  <p class="section-label">Available on</p>
  <h2 class="section-title">Every platform, one great experience</h2>
  <div class="platforms-grid">
    <a class="platform-card" href="https://apps.apple.com" target="_blank">
      <div class="platform-icon">📱</div>
      <h3>iOS</h3>
      <p>iPhone &amp; iPad</p>
      <span class="platform-badge">App Store</span>
    </a>
    <a class="platform-card" href="https://github.com/nastech-ai/nastechai/releases" target="_blank">
      <div class="platform-icon">🍎</div>
      <h3>macOS</h3>
      <p>Apple Silicon &amp; Intel</p>
      <span class="platform-badge">GitHub Releases</span>
    </a>
    <a class="platform-card" href="https://github.com/nastech-ai/nastechai/releases" target="_blank">
      <div class="platform-icon">🪟</div>
      <h3>Windows</h3>
      <p>Windows 10 &amp; 11</p>
      <span class="platform-badge">GitHub Releases</span>
    </a>
    <a class="platform-card" href="https://github.com/nastech-ai/nastechai/releases" target="_blank">
      <div class="platform-icon">🐧</div>
      <h3>Linux</h3>
      <p>Ubuntu, Debian &amp; more</p>
      <span class="platform-badge">GitHub Releases</span>
    </a>
    <a class="platform-card" href="#web-app" id="web-app">
      <div class="platform-icon">🌐</div>
      <h3>Web</h3>
      <p>Any modern browser</p>
      <span class="platform-badge">{"Available" if False else "Building..."}</span>
    </a>
  </div>
</div>

<!-- FOOTER -->
<footer>
  <div class="footer-brand">
    {"<img src='data:image/png;base64," + LOGO_B64 + "' alt=''>" if LOGO_B64 else ""}
    NasTech AI
  </div>
  <span>© 2026 NasTech AI · com.nastechai.app · v1.1.17</span>
  <a href="https://github.com/nastech-ai/nastechai" target="_blank" style="color:var(--muted);text-decoration:none;">GitHub ↗</a>
</footer>

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


tmp = tempfile.mkdtemp()
pathlib.Path(tmp, "index.html").write_text(LANDING_HTML)
WEB_DIR = tmp
print("Serving NasTech AI landing page.")

os.chdir(WEB_DIR)

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"NasTech AI running on http://0.0.0.0:{PORT}")
    httpd.serve_forever()
