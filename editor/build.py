"""Сборка редактора зала: editor/template.html -> dist/editor.html
Вставляет исходную схему из shared/plan.json (кнопка «Вернуть исходную схему» откатывает к ней).
Запуск из корня репозитория:  python3 editor/build.py
"""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
s = (ROOT/'editor'/'template.html').read_text()
plan = json.loads((ROOT/'shared'/'plan.json').read_text())
assert '__PLAN__' in s
s = s.replace('__PLAN__', json.dumps({k: plan[k] for k in ('zones', 'tables', 'decor')}, ensure_ascii=False))
(ROOT/'dist').mkdir(exist_ok=True)
(ROOT/'dist'/'editor.html').write_text(s)
print('dist/editor.html', len(s), 'байт')
