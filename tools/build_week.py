"""Score a week's lineups from data/weekN/games/*.json and render index.html.
usage: python3 tools/build_week.py 6 [--final] [--cut 6]"""
import json, sys, os, re, datetime, html
sys.path.insert(0, os.path.dirname(__file__))
from rules import score_player, score_k, score_d
from names import resolve
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WK = int(sys.argv[1]); FINAL = '--final' in sys.argv
CUT = int(sys.argv[sys.argv.index('--cut') + 1]) if '--cut' in sys.argv else 5
W = f'{R}/data/week{WK}'
teams = json.load(open(f'{W}/teams.json'))
sched = json.load(open(f'{W}/schedule.json'))
games = {}
for g in sched:
    f = f"{W}/games/{g['away']}-{g['home']}.json"
    d = json.load(open(f)) if os.path.exists(f) else {'status': 'pre'}
    d.update(away=g['away'], home=g['home'], kick=g['kick'])
    games[g['away']] = games[g['home']] = d
def label(d):
    a, h = d['away'], d['home']
    if d['status'] == 'pre': return f"{a} @ {h}", d['kick']
    sc = d['score']
    return f"{a} {sc[a]} @ {h} {sc[h]}", (d.get('clock') or 'Final') if d['status'] == 'final' else d.get('clock', 'Live')

prev = {}
pw = f'{R}/data/week{WK-1}/page_data.json'
norm = lambda o: re.sub(r'\(.*?\)|[^a-z]', '', o.lower())
if os.path.exists(pw):
    for t in json.load(open(pw))['teams']: prev[norm(t['owner'])] = t['prev'] + t['total']

out = []
for t in teams:
    lu = []
    for x in t['lineup']:
        name, tm = resolve(x['pos'], x['raw'])
        d = games.get(tm)
        e = dict(pos=x['pos'], name=name, team=tm, pts=0, comm=None, bd=[], game='Bye week' if tm else 'Retired')
        if d:
            lab, st = label(d); e['game'] = f"{lab} · {st}"
            if d['status'] == 'pre': e['yet'] = True
            else:
                if d['status'] == 'live': e['on'] = True
                fin = d['status'] == 'final'
                if x['pos'] == 'K':
                    s = d.get('kickers', {}).get(name)
                    pts, br = score_k(s) if s else (0, [])
                elif x['pos'] == 'DEF':
                    s = dict(d['defenses'].get(tm, {}))
                    opp = d['home'] if tm == d['away'] else d['away']
                    s['opp_points'] = d['score'][opp]
                    s['result'] = 'W' if d['score'][tm] > d['score'][opp] else 'L' if d['score'][tm] < d['score'][opp] else 'T'
                    pts, br = score_d(s, final=fin)
                else:
                    s = d.get('players', {}).get(name)
                    pts, br = score_player(x['pos'], s) if s else (0, [])
                    if not s and fin: br = []
                e['pts'] = pts; e['bd'] = [[a, b] for a, b in br]
        lu.append(e)
    owner = re.sub(r'\s*\(2025 champ\)', '', t['owner'])
    out.append(dict(owner=owner, champ='2025 champ' in t['owner'], total=sum(p['pts'] for p in lu), comm=None,
                    prev=prev.get(norm(owner), 0), alive=t['alive'], lineup=lu))
missing = [t['owner'] for t in out if norm(t['owner']) not in prev]
seen = []; glist = []
for g in sched:
    d = games[g['away']]; lab, st = label(d)
    glist.append(dict(t=lab, s=st, live=d['status'] == 'live'))
nlive = sum(g['live'] for g in glist); nfin = sum(games[g['away']]['status'] == 'final' for g in sched)
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4)))
stamp = now.strftime('%a %b %-d, %-I:%M %p ET')
final = FINAL or nfin == len(sched)
alive_n = sum(t['alive'] for t in out)
meta = dict(updated=('Final · ' if final else 'Updated ') + stamp,
            status='All games final' if final else (f'Live · {nlive} game{"s" if nlive != 1 else ""} in progress' if nlive else f'{nfin} of {len(sched)} games final'),
            live=not final, audit=False, cut=CUT, cutLive=True,
            cutNote=f"bottom {CUT} by Week {WK} score are cut" + ("" if final else " · line moves as games play"),
            footnote=f"Live scoring under league rules from box scores (CBS Sports) and play-by-play (Sportradar). Updated about every 20 minutes during games; "
                     f"unofficial until the commissioner's results. Season = Weeks 1–{WK-1} official + Week {WK} live. Defense win/loss bonus applies when the game ends.")
data = dict(week=WK, teams=out, games=glist)
json.dump(data, open(f'{W}/page_data.json', 'w'), indent=0)
page = open(f'{R}/tools/page.html').read().replace('__DATA__', json.dumps(data, separators=(',', ':'))).replace('__META__', json.dumps(meta))
open(f'{R}/index.html', 'w').write(page)
rk = sorted(out, key=lambda t: -t['total'])
print(meta['status'], '|', meta['updated'], '| prev-missing:', missing)
print('Top 5:', [(t['owner'], t['total']) for t in rk[:5]])
me = next(t for t in out if t['owner'].lower() == 'kearney')
print('Kearney:', me['total'], 'rank', 1 + sum(t['total'] > me['total'] for t in out))
