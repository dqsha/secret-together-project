"""Сборка приложения бронирования: booking/template.html -> dist/booking.html
Вставляет фото (assets/photos) и схему зала (shared/plan.json),
затем заменяет light-dark() на CSS-переменные (поддержка iOS < 17.5).
Запуск из корня репозитория:  python3 booking/build.py
"""
import json, base64, io, pathlib
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parents[1]
s = (ROOT/'booking'/'template.html').read_text()
def rep(a, b):
    global s
    assert a in s, a[:60]; s = s.replace(a, b)
PH = {}
for f in sorted((ROOT/'booking'/'assets'/'photos').glob('*.jpg')):
    im = Image.open(f).convert('RGB'); im.thumbnail((560, 560))
    b = io.BytesIO(); im.save(b, 'JPEG', quality=62, optimize=True, progressive=True)
    PH[f.stem] = 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
plan = json.loads((ROOT/'shared'/'plan.json').read_text())
rep('__PH__', json.dumps(PH))
rep('__PLAN__', json.dumps({k: plan[k] for k in ('zones', 'tables', 'decor')}, ensure_ascii=False))
# light-dark(A,B) -> var(--ldN)
pairs = {}; out = []; i = 0
while True:
    j = s.find('light-dark(', i)
    if j < 0: out.append(s[i:]); break
    out.append(s[i:j]); k = j + len('light-dark('); depth = 1; p = k; comma = None
    while depth:
        ch = s[p]
        if ch == '(': depth += 1
        elif ch == ')': depth -= 1
        elif ch == ',' and depth == 1 and comma is None: comma = p
        p += 1
    key = (s[k:comma].strip(), s[comma+1:p-1].strip())
    if key not in pairs: pairs[key] = f'--ld{len(pairs)}'
    out.append(f'var({pairs[key]})'); i = p
s = ''.join(out)
L = ';'.join(f'{v}:{a}' for (a, b), v in pairs.items()); D = ';'.join(f'{v}:{b}' for (a, b), v in pairs.items())
block = f':root{{{L}}}@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{{D}}}}}:root[data-theme=dark]{{{D}}}\n'
s = s.replace('<style>\n', '<style>\n' + block, 1)
(ROOT/'dist').mkdir(exist_ok=True)
(ROOT/'dist'/'booking.html').write_text(s)
print('dist/booking.html', len(s), 'байт; light-dark пар:', len(pairs))
