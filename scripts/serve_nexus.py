#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from mimetypes import guess_type
from pathlib import Path
from urllib.parse import urlparse, unquote
import html
import os

ROOT = Path('/root/.openclaw/workspace/aion-nexus').resolve()
SITE_ROOT = ROOT / 'site'

ROOT_INDEX = """<!doctype html>
<html lang=\"it\">
  <head>
    <meta charset=\"UTF-8\" />
    <meta http-equiv=\"refresh\" content=\"0; url=/site/\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <title>Altair Nexus</title>
    <meta name=\"description\" content=\"Reindirizzamento alla homepage pubblica di Altair Nexus.\" />
    <link rel=\"canonical\" href=\"/site/\" />
    <style>
      body { margin: 0; min-height: 100vh; display: grid; place-items: center; background: #0b1220; color: #e8eef8; font-family: Inter, system-ui, sans-serif; }
      .card { max-width: 560px; padding: 28px; border-radius: 18px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 20px 60px rgba(0,0,0,0.25); }
      a { color: #7ed8ff; }
    </style>
  </head>
  <body>
    <div class=\"card\">
      <h1>Altair Nexus</h1>
      <p>Ti sto portando alla homepage pubblica del progetto.</p>
      <p>Se il reindirizzamento non parte da solo, apri <a href=\"/site/\">/site/</a>.</p>
      <p>Area tecnica: <a href=\"/administration/\">/administration/</a></p>
    </div>
  </body>
</html>
"""

class NexusHandler(SimpleHTTPRequestHandler):
    def _is_proxy_request(self) -> bool:
        return bool(self.headers.get('X-Forwarded-For') or self.headers.get('X-Real-Ip'))

    def _is_local_admin_request(self) -> bool:
        host, _port = self.client_address
        return host in {'127.0.0.1', '::1'} and not self._is_proxy_request()

    def _is_hidden_path(self, path: str) -> bool:
        parts = [part for part in Path(path).parts if part not in {'/', ''}]
        return any(part.startswith('.') for part in parts)

    def _safe_join(self, rel_path: str) -> Path:
        candidate = (ROOT / rel_path).resolve()
        if candidate != ROOT and ROOT not in candidate.parents:
            return ROOT
        return candidate

    def _serve_public_path(self, rel_path: str, send_body: bool = True):
        target = self._safe_join(rel_path)
        if self._is_hidden_path(target.relative_to(ROOT).as_posix()):
            self.send_error(404, 'File not found')
            return

        if target.is_dir():
            target = target / 'index.html'

        if not target.exists() or not target.is_file():
            self.send_error(404, 'File not found')
            return

        try:
            data = target.read_bytes()
        except OSError:
            self.send_error(404, 'File not found')
            return

        content_type = guess_type(str(target))[0] or 'application/octet-stream'
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        if send_body:
            self.wfile.write(data)

    def _redirect_to_site(self, path: str):
        target = f'/site{path}'
        self.send_response(308)
        self.send_header('Location', target)
        self.send_header('Content-Length', '0')
        self.end_headers()

    def _canonical_site_alias(self, path: str) -> bool:
        return (
            path == '/stories'
            or path.startswith('/stories/')
            or path == '/assets'
            or path.startswith('/assets/')
            or path == '/history.html'
            or path == '/aion-brief.html'
            or path == '/reports.html'
            or path == '/reports'
            or path.startswith('/reports/')
        )

    def _admin_listing(self, fs_path: Path, request_path: str):
        try:
            entries = sorted(fs_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except OSError:
            self.send_error(404, 'Directory not found')
            return None

        parent_link = ''
        if fs_path != ROOT:
            rel_parent = '/' + str(fs_path.parent.relative_to(ROOT)).strip('/')
            parent_url = '/administration/' if rel_parent == '/' else f'/administration{rel_parent}/'
            parent_link = f'<li><a href="{html.escape(parent_url)}">../</a></li>'

        items = []
        for entry in entries:
            rel = entry.relative_to(ROOT).as_posix()
            href = f'/administration/{rel}'
            label = entry.name + ('/' if entry.is_dir() else '')
            if entry.is_dir():
                href += '/'
            items.append(f'<li><a href="{html.escape(href)}">{html.escape(label)}</a></li>')

        body = f"""<!doctype html>
<html lang=\"it\">
  <head>
    <meta charset=\"UTF-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <title>Altair Nexus Administration</title>
    <style>
      body {{ margin: 0; padding: 32px; background: #0b1220; color: #e8eef8; font-family: Inter, system-ui, sans-serif; }}
      .wrap {{ max-width: 980px; margin: 0 auto; }}
      .card {{ padding: 24px; border-radius: 18px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); }}
      a {{ color: #7ed8ff; text-decoration: none; }}
      a:hover {{ text-decoration: underline; }}
      ul {{ line-height: 1.8; }}
      .topnav {{ margin-bottom: 18px; display: flex; gap: 16px; flex-wrap: wrap; }}
      .muted {{ color: #aab8d1; }}
    </style>
  </head>
  <body>
    <div class=\"wrap\">
      <div class=\"topnav\">
        <a href=\"/site/\">Apri sito pubblico</a>
        <a href=\"/administration/\">Administration root</a>
      </div>
      <div class=\"card\">
        <h1>Administration</h1>
        <p class=\"muted\">Percorso: /{html.escape(str(fs_path.relative_to(ROOT)).strip('/'))}</p>
        <ul>
          {parent_link}
          {''.join(items)}
        </ul>
      </div>
    </div>
  </body>
</html>
"""
        encoded = body.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(encoded)))
        self.end_headers()
        return encoded

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path == '/':
            encoded = ROOT_INDEX.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
            return

        if path in {'/robots.txt', '/sitemap.xml', '/llms.txt'}:
            self._serve_public_path(f'site{path}')
            return

        if self._canonical_site_alias(path):
            self._redirect_to_site(path)
            return

        if path.startswith('/administration'):
            if not self._is_local_admin_request():
                self.send_error(403, 'Forbidden')
                return
            rel = path[len('/administration'):].lstrip('/')
            target = self._safe_join(rel)
            if target.is_dir():
                encoded = self._admin_listing(target, path)
                if encoded is not None:
                    self.wfile.write(encoded)
                return
            if target.exists():
                self.path = '/' + target.relative_to(ROOT).as_posix()
                return super().do_GET()
            self.send_error(404, 'File not found')
            return

        if self._is_hidden_path(path):
            self.send_error(404, 'File not found')
            return

        if not (
            path == '/site'
            or path.startswith('/site/')
            or path == '/data'
            or path.startswith('/data/')
        ):
            self.send_error(404, 'File not found')
            return

        rel_path = path.lstrip('/')
        self._serve_public_path(rel_path)
        return

    def do_HEAD(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path == '/':
            encoded = ROOT_INDEX.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(encoded)))
            self.end_headers()
            return

        if path in {'/robots.txt', '/sitemap.xml', '/llms.txt'}:
            self._serve_public_path(f'site{path}', send_body=False)
            return

        if self._canonical_site_alias(path):
            self._redirect_to_site(path)
            return

        if self._is_hidden_path(path):
            self.send_error(404, 'File not found')
            return

        if not (
            path == '/site'
            or path.startswith('/site/')
            or path == '/data'
            or path.startswith('/data/')
        ):
            self.send_error(404, 'File not found')
            return

        rel_path = path.lstrip('/')
        self._serve_public_path(rel_path, send_body=False)
        return

    def translate_path(self, path):
        parsed = urlparse(path)
        cleaned = unquote(parsed.path).lstrip('/')
        if self._is_hidden_path(cleaned):
            return str(SITE_ROOT / '__blocked__')
        return str((ROOT / cleaned).resolve())


def main():
    port = int(os.environ.get('PORT', '8766'))
    server = ThreadingHTTPServer(('127.0.0.1', port), NexusHandler)
    print(f'Altair Nexus server listening on http://127.0.0.1:{port}', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
