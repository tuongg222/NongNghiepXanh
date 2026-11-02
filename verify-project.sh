#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
command -v node >/dev/null || { echo 'ERROR: cần Node.js để kiểm tra JavaScript.' >&2; exit 2; }
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
python3 - "$ROOT" "$TMP" <<'PY'
from html.parser import HTMLParser
from pathlib import Path
import sys, xml.etree.ElementTree as ET
root,tmp=Path(sys.argv[1]),Path(sys.argv[2])
class Scripts(HTMLParser):
    def __init__(self): super().__init__(); self.active=False; self.src=None; self.parts=[]; self.inline=[]
    def handle_starttag(self, tag, attrs):
        if tag.lower()=='script': self.active=True; self.src=dict(attrs).get('src'); self.parts=[]
    def handle_data(self, data):
        if self.active: self.parts.append(data)
    def handle_endtag(self, tag):
        if tag.lower()=='script' and self.active:
            content=''.join(self.parts)
            if not self.src and content.strip(): self.inline.append(content)
            self.active=False; self.src=None; self.parts=[]
p=Scripts(); p.feed((root/'app/src/main/assets/index.html').read_text(encoding='utf-8'))
if not p.inline: raise SystemExit('ERROR: không tìm thấy JavaScript nhúng trong index.html')
for i,script in enumerate(p.inline,1): (tmp/f'inline-{i}.js').write_text(script,encoding='utf-8')
ET.parse(root/'app/src/main/AndroidManifest.xml')
print(f'OK: HTML parse, {len(p.inline)} block JavaScript nhúng, AndroidManifest XML')
PY
for f in "$TMP"/inline-*.js; do node --check "$f"; done
node --input-type=module --check < "$ROOT/worker.js"
node --input-type=module --check < "$ROOT/auth.js"
if grep -Eq '/auth/(random-test|crypto-test)' "$ROOT/worker.js"; then echo 'ERROR: còn endpoint kiểm tra mật mã thử nghiệm' >&2; exit 1; fi
echo 'OK: cú pháp JavaScript, worker.js, auth.js; không còn endpoint test mật mã.'
