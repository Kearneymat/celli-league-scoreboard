"""Split an ESPN-extract JSON {AWAY-HOME: game} into data/weekN/games/*.json with defaults.
usage: python3 tools/apply_espn.py N file.json"""
import json, sys, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N, f = sys.argv[1], sys.argv[2]
for k, g in json.load(open(f)).items():
    if 'err' in g: print('ERR', k, g['err']); continue
    for kk in g.get('kickers', {}).values():
        for x in ('fg_made_dist', 'fg_missed_dist'): kk.setdefault(x, [])
        kk.setdefault('xp_made', 0); kk.setdefault('xp_missed', 0)
    for t in k.split('-'):
        d = g.setdefault('defenses', {}).setdefault(t, {})
        for x in ('sacks', 'int', 'fum_rec', 'safeties'): d.setdefault(x, 0)
        d.setdefault('def_st_td_lengths', [])
    g.setdefault('players', {}); g['src'] = 'ESPN'
    json.dump(g, open(f'{R}/data/week{N}/games/{k}.json', 'w'), indent=0)
    print(k, g['status'], g['clock'], g['score'])
