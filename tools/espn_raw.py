"""Convert raw ESPN extract {AWAY-HOME: raw} -> data/weekN/games/*.json using needed.json names.
usage: python3 tools/espn_raw.py N raw.json"""
import json, sys, os, re
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N, f = sys.argv[1], sys.argv[2]
need = json.load(open(f'{R}/data/week{N}/needed.json'))
ALIAS = {'pop douglas': 'demario douglas'}
def nz(s):
    s = s.lower().replace('.', ' ').replace("'", '')
    s = re.sub(r'\b(jr|sr|ii|iii|iv)\b', '', s)
    return ' '.join(s.split())
def last(s): return nz(s).split()[-1] if nz(s) else ''
def match(espn_name, cands):
    e = nz(espn_name)
    for c in cands:
        if nz(ALIAS.get(c.lower(), c)) == e or nz(c) == e: return c
    l = [c for c in cands if last(c) == last(espn_name)]
    if len(l) == 1:
        # avoid matching a different first initial when ESPN gives a full name
        ef = e.split()[0][0] if e.split() else ''
        cf = nz(ALIAS.get(l[0].lower(), l[0])).split()[0][0]
        if ef == cf or len(e.split()[0]) <= 2: return l[0]
    return None
for key, g in json.load(open(f)).items():
    if g.get('status') == 'pre': continue
    teams = key.split('-')
    ck = g['clock']; m = re.match(r'(\d+:\d+) - (\d)\w\w', ck)
    if m: ck = f'Q{m.group(2)} {m.group(1)}'
    elif re.match(r'(\d+:\d+) - OT', ck): ck = 'OT ' + ck.split(' ')[0]
    elif 'Half' in ck: ck = 'Halftime'
    elif ck.startswith('End of'): ck = 'End Q' + re.sub(r'\D', '', ck)[:1]
    out = dict(status=g['status'], clock=ck, score=g['score'], players={}, kickers={}, defenses={t: {**dict(sacks=0, int=0, fum_rec=0, safeties=0, def_st_td_lengths=[]), **g.get('D', {}).get(t, {})} for t in teams}, src='ESPN')
    for k, v in g.get('P', {}).items():
        nm, tm = k.rsplit('|', 1)
        c = match(nm, [n for p, n in need.get(tm, []) if p != 'K' and p != 'DEF'])
        if not c: continue
        d = {kk: vv for kk, vv in v.items() if vv}
        out['players'][c] = d
    def P(nm, tm):
        c = match(nm, [n for p, n in need.get(tm, []) if p not in ('K', 'DEF')])
        if c: return out['players'].setdefault(c, {})
    for t in g.get('tds', []):
        if t['type'] == 'pass':
            r = P(t['rec'], t['tm']); q = P(t['qb'], t['tm'])
            if r is not None: r.setdefault('rec_td_lengths', []).append(t['len'])
            if q is not None: q.setdefault('pass_td_lengths', []).append(t['len'])
        elif t['type'] == 'rush':
            r = P(t['who'], t['tm'])
            if r is not None: r.setdefault('rush_td_lengths', []).append(t['len'])
        else: print('UNPARSED TD', key, t)
    for k, v in g.get('K', {}).items():
        v = {**dict(fgm=0, fga=0, xp_made=0, xp_missed=0), **v}
        nm, tm = k.rsplit('|', 1)
        c = match(nm, [n for p, n in need.get(tm, []) if p == 'K'])
        if not c: continue
        made = [d for n, d, t in g.get('fgs', []) if t == tm and last(n) == last(nm)]
        miss = [d for n, d, t in g.get('miss', []) if t == tm and last(n.replace('.', ' ')) == last(nm)][:max(0, v['fga'] - v['fgm'])]
        if len(made) != v['fgm'] or len(miss) != v['fga'] - v['fgm']: print('FG CHECK', key, nm, v, made, miss)
        out['kickers'][c] = dict(fg_made_dist=made, fg_missed_dist=miss, xp_made=v['xp_made'], xp_missed=v['xp_missed'])
    for txt, tm in g.get('two', []):
        m = re.search(r'\((.*?) (?:Run|Rush) for Two-Point', txt) or re.search(r'Pass to (.*?) for Two-Point', txt)
        r = P(m.group(1), tm) if m else None
        if r is not None: r['two_pt'] = r.get('two_pt', 0) + 1
        elif not m: print('2PT unparsed', key, txt)
    if g.get('dst'): print('DEF/ST TD', key, g['dst'])
    json.dump(out, open(f'{R}/data/week{N}/games/{key}.json', 'w'), indent=0)
    print(key, g['status'], g['clock'], g['score'], len(out['players']), 'players')
