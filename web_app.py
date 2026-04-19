from __future__ import annotations

from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from tiaochen_bot import ReportRequest, TiaochenBot


HOST = "0.0.0.0"
PORT = 8000
STATIC_DIR = Path(__file__).with_name("static")


def render_page(result_html: str = "", form_data: dict[str, str] | None = None) -> str:
    form_data = form_data or {}
    raw_text = escape(form_data.get("raw_text", ""))
    template = form_data.get("template", "")
    chief_checked = "checked" if form_data.get("chief") == "on" else ""
    council_checked = "checked" if form_data.get("council") == "on" else ""
    verbatim_checked = "checked" if form_data.get("verbatim") == "on" else ""

    template_options = ["", "fraud", "drug", "theft", "fight", "group_brawl", "death", "dui", "fire_or_signal"]
    option_html = "".join(
        f'<option value="{t}" {"selected" if t == template else ""}>{t or "自動判斷"}</option>' for t in template_options
    )

    return f"""<!doctype html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>條陳機器人 APP</title>
  <link rel="manifest" href="/manifest.webmanifest">
  <meta name="theme-color" content="#1f2937">
  <link rel="icon" href="/icon.svg" type="image/svg+xml">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="條陳機器人">
  <style>
    body {{ font-family: sans-serif; margin: 24px; max-width: 980px; }}
    textarea {{ width: 100%; min-height: 180px; }}
    .row {{ margin: 8px 0; }}
    pre {{ white-space: pre-wrap; background: #f7f7f7; padding: 12px; border-radius: 8px; }}
    .card {{ border: 1px solid #ddd; border-radius: 10px; padding: 12px; margin-top: 14px; }}
    button {{ padding: 8px 14px; }}
  </style>
</head>
<body>
  <h2>康定所／萬華分局條陳生成 APP</h2>
  <form method=\"post\">
    <div class=\"row\">
      <label>原始案件內容</label>
      <textarea name=\"raw_text\" required>{raw_text}</textarea>
    </div>
    <div class=\"row\">
      <label>模板：</label>
      <select name=\"template\">{option_html}</select>
    </div>
    <div class=\"row\">
      <label><input type=\"checkbox\" name=\"chief\" {chief_checked}> 加出報局長版本</label>
      <label><input type=\"checkbox\" name=\"council\" {council_checked}> 加出回覆議座版本</label>
      <label><input type=\"checkbox\" name=\"verbatim\" {verbatim_checked}> 原文照登</label>
    </div>
    <button type=\"submit\">產生條陳</button>
  </form>
  {result_html}
  <script>
    if ("serviceWorker" in navigator) {{
      window.addEventListener("load", function () {{
        navigator.serviceWorker.register("/service-worker.js");
      }});
    }}
  </script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    bot = TiaochenBot()

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/manifest.webmanifest":
            self._serve_static("manifest.webmanifest", "application/manifest+json; charset=utf-8")
            return
        if self.path == "/service-worker.js":
            self._serve_static("service-worker.js", "application/javascript; charset=utf-8")
            return
        if self.path == "/icon.svg":
            self._serve_static("icon.svg", "image/svg+xml")
            return
        html = render_page()
        self._send_html(html)

    def do_POST(self) -> None:  # noqa: N802
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length).decode("utf-8")
        form = {k: v[0] for k, v in parse_qs(body, keep_blank_values=True).items()}

        req = ReportRequest(
            raw_text=form.get("raw_text", "").strip(),
            force_template=form.get("template") or None,
            include_chief_version=form.get("chief") == "on",
            include_council_version=form.get("council") == "on",
            preserve_verbatim=form.get("verbatim") == "on",
        )

        reports = self.bot.generate(req)
        blocks = []
        for title, content in reports.items():
            blocks.append(f"<div class='card'><h3>{escape(title)}</h3><pre>{escape(content)}</pre></div>")
        html = render_page("\n".join(blocks), form)
        self._send_html(html)

    def _send_html(self, html: str) -> None:
        encoded = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _serve_static(self, filename: str, content_type: str) -> None:
        filepath = STATIC_DIR / filename
        if not filepath.exists():
            self.send_error(404, "Not Found")
            return
        payload = filepath.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main() -> None:
    server = HTTPServer((HOST, PORT), Handler)
    print(f"條陳機器人 APP 已啟動：http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
