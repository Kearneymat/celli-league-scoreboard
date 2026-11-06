"""Build a week's page from the commissioner's official spreadsheet (player points already filled in).
usage: python3 tools/build_official.py 7"""
import json, sys, os, re, datetime
sys.path.insert(0, os.path.dirname(__file__))
from names import resolve
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WK = int(sys.argv[1]); W = f'{R}/data/week{WK}'
T = json.load(open(f'{W}/teams_official.json'))
norm = lambda o: re.sub(r'\(.*?\)|[^a-z]', '', o.lower())
prev = {}
pw = f'{R}/data/week{WK-1}/page_data.json'
if os.path.exists(f'{W}/prev.json'):
    prev = json.load(open(f'{W}/prev.json'))
elif os.path.exists(pw):
    for t in json.load(open(pw))['teams']: prev[norm(t['owner'])] = t['prev'] + t['total']
out = []
for t in T:
    lu = []
    for x in t['lineup']:
        name, tm = resolve(x['pos'], x['raw'])
        pts = x['pts'] if isinstance(x['pts'], (int, float)) else 0
        lu.append(dict(pos=x['pos'], name=name, team=tm, pts=pts, comm=pts, bd=[['Official score', pts]] if pts else [], game=f'{tm} · Week {WK} final' if tm else ''))
    owner = re.sub(r'\s*\(2025 champ\)', '', t['owner'])
    out.append(dict(owner=owner, champ='2025 champ' in t['owner'], total=t['total'], comm=t['total'], prev=prev.get(norm(owner), 0), alive=t['alive'], lineup=lu))
missing = [t['owner'] for t in out if norm(t['owner']) not in prev]
alive_n = sum(t['alive'] for t in out)
meta = dict(updated=f'Official results · Week {WK}', status='Official — commissioner\'s results', live=False, audit=False, cut=0, cutLive=False,
            cutNote=f'{alive_n} teams still alive after Week {WK} cuts (per commissioner)',
            footnote=f'Week {WK} scores are the commissioner\'s official results. Season totals through Week {WK-1} are from the commissioner\'s sheet.')
if os.path.exists(f'{W}/meta.json'): meta.update(json.load(open(f'{W}/meta.json')))
data = dict(week=WK, teams=out, games=[dict(t=f'Week {WK}', s='Official', live=False)])
json.dump(data, open(f'{W}/page_data.json', 'w'), indent=0)
page = open(f'{R}/tools/page.html').read().replace('__DATA__', json.dumps(data, separators=(',', ':'))).replace('__META__', json.dumps(meta))
open(f'{R}/index.html', 'w').write(page)
rk = sorted(out, key=lambda t: -t['total'])
print('missing prev:', missing); print('Top:', [(t['owner'], t['total']) for t in rk[:5]])
me = next(t for t in out if t['owner'].lower() == 'kearney'); print('Kearney', me['total'], 1 + sum(t['total'] > me['total'] for t in out), 'season', me['prev'] + me['total'])
s = sorted(out, key=lambda t: -(t['prev'] + t['total'])); print('Season top:', [(t['owner'], t['prev'] + t['total']) for t in s[:3]], 'Kearney season rank', 1 + [t['owner'] for t in s].index('Kearney'))
