"""League scoring rules (shared by all weeks)."""
def tdv(L):
    L = int(L)
    return 6 if L < 10 else 7 if L < 20 else 8 if L < 30 else 9 if L < 40 else 10 if L < 50 else 12
def thr(x, at, base, per, step):
    return base + per * ((x - at) // step) if x >= at else 0

def score_player(pos, s):
    g = lambda k: s.get(k) or 0
    out = []
    def add(label, pts):
        if pts: out.append((label, pts))
    if pos == 'QB':
        add(f"{g('pass_cmp')} completions", thr(g('pass_cmp'), 20, 5, 1, 1))
        add(f"{g('pass_yds')} pass yds", thr(g('pass_yds'), 200, 5, 1, 10))
        for L in s.get('pass_td_lengths') or []: add(f"{L}-yd TD pass", tdv(L))
        add(f"{g('int')} INT", -5 * g('int'))
        add(f"{g('rush_att')} rushes", thr(g('rush_att'), 15, 5, 1, 1))
    if pos == 'RB':
        add(f"{g('rush_att')} rushes", thr(g('rush_att'), 15, 5, 1, 1))
    add(f"{g('rush_yds')} rush yds", thr(g('rush_yds'), 50, 5, 1, 10))
    for L in s.get('rush_td_lengths') or []: add(f"{L}-yd TD run", tdv(L))
    if pos in ('RB', 'WR'):
        add(f"{g('rec')} catches", thr(g('rec'), 5, 5, 1, 1))
        add(f"{g('rec_yds')} rec yds", thr(g('rec_yds'), 50, 5, 1, 10))
    if pos == 'TE':
        add(f"{g('rec')} catches", thr(g('rec'), 3, 5, 2, 1))
        add(f"{g('rec_yds')} rec yds", thr(g('rec_yds'), 30, 5, 2, 10))
    for L in s.get('rec_td_lengths') or []: add(f"{L}-yd TD catch", tdv(L))
    for L in s.get('ret_td_lengths') or []: add(f"{L}-yd return TD", tdv(L))
    add(f"{g('two_pt')} two-pt conv", 2 * g('two_pt'))
    add(f"{g('fl')} lost fumble", -3 * g('fl'))
    return sum(p for _, p in out), out

def score_k(s):
    out = []
    for d in s.get('fg_made_dist', []):
        out.append((f"{d}-yd FG", 3 if d < 30 else 6 if d < 40 else 9 if d < 50 else 12 if d < 60 else 15))
    for d in s.get('fg_missed_dist', []):
        lab = s.get('miss_label', {}).get(str(d), f"{d}-yd")
        out.append((f"missed {lab} FG", -9 if d < 30 else -6 if d < 40 else -3 if d < 50 else -1 if d < 60 else 0))
    if s.get('xp_made'): out.append((f"{s['xp_made']} XP", s['xp_made']))
    if s.get('xp_missed'): out.append((f"{s['xp_missed']} missed XP", -9 * s['xp_missed']))
    return sum(p for _, p in out), out

def pa_pts(pa):
    return 20 if pa == 0 else 15 if pa <= 6 else 10 if pa <= 10 else 5 if pa <= 14 else 0 if pa <= 24 else -5 if pa <= 30 else -10 if pa <= 35 else -15 if pa <= 44 else -20
def score_d(s, final=True):
    out = [(f"{s['opp_points']} pts allowed", pa_pts(s['opp_points']))]
    if s.get('sacks'): out.append((f"{s['sacks']:g} sacks", int(2 * s['sacks'])))
    if s.get('int'): out.append((f"{s['int']} INT", 2 * s['int']))
    if s.get('fum_rec'): out.append((f"{s['fum_rec']} fum rec", 2 * s['fum_rec']))
    if s.get('safeties'): out.append((f"{s['safeties']} safety", 5 * s['safeties']))
    for L in s.get('def_st_td_lengths') or []: out.append((f"{L}-yd def/ST TD", tdv(L)))
    r = s.get('result')
    if r in ('W', 'L'):
        out.append(('Win' if r == 'W' else 'Loss', 5 if r == 'W' else -5) if final else ('Leading' if r == 'W' else 'Trailing', 0))
    out = [o for o in out if o[1] or 'allowed' in o[0] or o[0] in ('Leading', 'Trailing')]
    return sum(p for _, p in out), out
