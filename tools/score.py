import json, re, sys
D = '/tmp/claude-0/-home-claude/0d765627-dffb-5633-8a20-77c3b1fe877c/scratchpad/wk5/'
FUMBLE_MODE = sys.argv[1] if len(sys.argv) > 1 else 'all'   # 'all' = -3 per fumble; 'lost' etc. for testing

stats = {'P': {}, 'K': {}, 'D': {}}
games = []
for f in 'ABCD':
    d = json.load(open(D + f'stats_{f}.json'))
    games += d['games']
    for p in d['players']: stats['P'][p['name']] = p
    for k in d['kickers']: stats['K'][k['name']] = k
    for x in d['defenses']: stats['D'][x['team']] = x

LOST = {'Mark Andrews': 1, 'Chase Brown': 1, 'Deshaun Watson': 1, 'Brock Bowers': 1, 'Aaron Jones': 1, 'Geno Smith': 1, 'Kenyon Sadiq': 1, 'Emanuel Wilson': 1, 'Deebo Samuel': 1}
def tdv(L):
    L = int(L)
    return 6 if L < 10 else 7 if L < 20 else 8 if L < 30 else 9 if L < 40 else 10 if L < 50 else 12
def thr(x, at, base, per, step):
    return base + per * ((x - at) // step) if x >= at else 0

def score_player(pos, s):
    """returns (points, [breakdown lines])"""
    if not s or not s.get('played'): return 0, ['Did not play']
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
    fl = LOST.get(s['name'], 0)
    add(f"{fl} lost fumble", -3 * fl)
    return sum(p for _, p in out), out

def score_k(s):
    if not s: return 0, ['no data']
    out = []
    for d in s['fg_made_dist']:
        out.append((f"{d}-yd FG", 3 if d < 30 else 6 if d < 40 else 9 if d < 50 else 12 if d < 60 else 15))
    for d in s['fg_missed_dist']:
        out.append((f"missed {d}-yd FG", -9 if d < 30 else -6 if d < 40 else -3 if d < 50 else -1 if d < 60 else 0))
    if s['xp_made']: out.append((f"{s['xp_made']} XP", s['xp_made']))
    if s['xp_missed']: out.append((f"{s['xp_missed']} missed XP", -9 * s['xp_missed']))
    return sum(p for _, p in out), out

def pa_pts(pa):
    return 20 if pa == 0 else 15 if pa <= 6 else 10 if pa <= 10 else 5 if pa <= 14 else 0 if pa <= 24 else -5 if pa <= 30 else -10 if pa <= 35 else -15 if pa <= 44 else -20
def score_d(s):
    out = [(f"{s['opp_points']} pts allowed", pa_pts(s['opp_points']))]
    if s['sacks']: out.append((f"{s['sacks']} sacks", 2 * s['sacks']))
    if s['int']: out.append((f"{s['int']} INT", 2 * s['int']))
    if s['fum_rec']: out.append((f"{s['fum_rec']} fum rec", 2 * s['fum_rec']))
    if s['safeties']: out.append((f"{s['safeties']} safety", 5 * s['safeties']))
    for L in s.get('def_st_td_lengths') or []: out.append((f"{L}-yd def/ST TD", tdv(L)))
    r = s['result']
    out.append(({'W': 'Win', 'L': 'Loss', 'T': 'Tie'}[r], 5 if r == 'W' else -5 if r == 'L' else 0))
    return sum(p for _, p in [o for o in out if o[1]]), [o for o in out if o[1] or 'allowed' in o[0]]

# --------- name map: league shorthand -> canonical ----------
P = {
 'maye': 'Drake Maye', 'dak': 'Dak Prescott', 'stafford': 'Matthew Stafford', 'brissett': 'Jacoby Brissett', 'bissett': 'Jacoby Brissett', 'brisett': 'Jacoby Brissett', 'briussett': 'Jacoby Brissett',
 'goff': 'Jared Goff', 'lawrence': 'Trevor Lawrence', 'cousins': 'Kirk Cousins', 'allen': 'Josh Allen', 'jallen': 'Josh Allen', 'lamar': 'Lamar Jackson', 'purdy': 'Brock Purdy',
 'shough': 'Tyler Shough', 'stroud': 'C.J. Stroud', 'stoud': 'C.J. Stroud', 'rodgers': 'Aaron Rodgers', 'burrow': 'Joe Burrow', 'darnold': 'Sam Darnold', 'dwatson': 'Deshaun Watson', 'geno': 'Geno Smith',
 'bijan': 'Bijan Robinson', 'cbrown': 'Chase Brown', 'brown': 'Chase Brown', 'gibbs': 'Jahmyr Gibbs', 'kwilliams': 'Kyren Williams', 'ballen': 'Braelon Allen', 'warren': 'Jaylen Warren', 'jwarren': 'Jaylen Warren',
 'jones': 'Aaron Jones', 'ajones': 'Aaron Jones', 'swift': "D'Andre Swift", 'judkins': 'Quinshon Judkins', 'ewilson': 'Emanuel Wilson', 'javwilliams': 'Javonte Williams', 'javwlliams': 'Javonte Williams',
 'jtaylor': 'Jonathan Taylor', 'irving': 'Bucky Irving', 'tuten': 'Bhayshul Tuten', 'henderson': 'TreVeyon Henderson', 'thenderson': 'TreVeyon Henderson', 'henry': 'Derrick Henry', 'gordon': 'Ollie Gordon II', 'monty': 'David Montgomery',
 'collins': 'Nico Collins', 'nico': 'Nico Collins', 'pickens': 'George Pickens', 'burden': 'Luther Burden', 'puka': 'Puka Nacua', 'adams': 'Davante Adams', 'dadams': 'Davante Adams', 'mwilson': 'Michael Wilson', 'wilson': 'Michael Wilson',
 'lamb': 'CeeDee Lamb', 'olave': 'Chris Olave', 'doubs': 'Romeo Doubs', 'samuel': 'Deebo Samuel', 'deebo': 'Deebo Samuel', 'stbrown': 'Amon-Ra St. Brown', 'asbrown': 'Amon-Ra St. Brown', 'golden': 'Matthew Golden',
 'jwilliams': 'Jameson Williams', 'jamwilliams': 'Jameson Williams', 'jamwill': 'Jameson Williams', 'jsn': 'Jaxon Smith-Njigba', 'shakir': 'Khalil Shakir', 'tucker': 'Tre Tucker', 'ctate': 'Carnell Tate', 'tate': 'Carnell Tate',
 'london': 'Drake London', 'mlemon': 'Makai Lemon', 'flowers': 'Zay Flowers', 'coleman': 'Keon Coleman', 'kcoleman': 'Keon Coleman', 'sutton': 'Courtland Sutton', 'pwash': 'Parker Washington', 'washington': 'Parker Washington',
 'watson': 'Christian Watson', 'cwatson': 'Christian Watson', 'downs': 'Josh Downs', 'higgins': 'Tee Higgins', 'bostoncle': 'Denzel Boston', 'gwilson': 'Garrett Wilson', 'evans': 'Mike Evans',
 'awilliamswash': 'Antonio Williams', 'awilliams': 'Antonio Williams', 'addison': 'Jordan Addison', 'iosivas': 'Andrei Iosivas', 'kallen': 'Keenan Allen', 'dk': 'DK Metcalf', 'mwashmia': 'Malik Washington',
 'fanin': 'Harold Fannin', 'kincaid': 'Dalton Kincaid', 'mcbride': 'Trey McBride', 'bowers': 'Brock Bowers', 'laporta': 'Sam LaPorta', 'likely': 'Isaiah Likely', 'hock': 'T.J. Hockenson', 'hockenson': 'T.J. Hockenson',
 'andrews': 'Mark Andrews', 'freiermuth': 'Pat Freiermuth', 'jjohnson': 'Juwan Johnson', 'okonwkowas': 'Chig Okonkwo', 'gesicki': 'Mike Gesicki', 'giseki': 'Mike Gesicki', 'schultz': 'Dalton Schultz', 'barner': 'AJ Barner',
 'sadiq': 'Kenyon Sadiq', 'kraft': 'Tucker Kraft', 'goedart': 'Dallas Goedert', 'goedert': 'Dallas Goedert', 'gronk': None,
}
TE_HENRY = 'Hunter Henry'
K = {'lutz': 'Wil Lutz', 'schrader': 'Spencer Shrader', 'shrader': 'Spencer Shrader', 'shraeder': 'Spencer Shrader', 'gay': 'Matt Gay', 'little': 'Cam Little', 'reichard': 'Will Reichard', 'reichrd': 'Will Reichard',
 'mcpherson': 'Evan McPherson', 'aubrey': 'Brandon Aubrey', 'zvada': 'Dominik Zvada', 'elliott': 'Jake Elliott', 'fairbain': "Ka'imi Fairbairn", 'santos': 'Cairo Santos', 'bates': 'Jake Bates', 'carlson': 'Daniel Carlson',
 'smack': 'Trey Smack', 'myers': 'Jason Myers', 'rhyland': 'Chad Ryland', 'stevens': 'Drew Stevens', 'stevenswash': 'Drew Stevens', 'mcglaughlin': 'Chase McLaughlin', 'slye': 'Joey Slye', 'folk': 'Nick Folk', 'dicker': 'Cameron Dicker'}
DF = {'pats': 'NE', 'texans': 'HOU', 'texas': 'HOU', 'browns': 'CLE', 'jags': 'JAX', 'cowboys': 'DAL', 'dallas': 'DAL', 'vikings': 'MIN', 'bengals': 'CIN', 'bears': 'CHI', 'commanders': 'WAS', 'steelers': 'PIT',
 'broncos': 'DEN', 'falcons': 'ATL', 'jets': 'NYJ', 'eagles': 'PHI', 'raiders': 'LV', 'ravens': 'BAL', 'seattle': 'SEA'}
TEAMNAME = {'NE': 'Patriots', 'HOU': 'Texans', 'CLE': 'Browns', 'JAX': 'Jaguars', 'DAL': 'Cowboys', 'MIN': 'Vikings', 'CIN': 'Bengals', 'CHI': 'Bears', 'WAS': 'Commanders', 'PIT': 'Steelers',
 'DEN': 'Broncos', 'ATL': 'Falcons', 'NYJ': 'Jets', 'PHI': 'Eagles', 'LV': 'Raiders', 'BAL': 'Ravens', 'SEA': 'Seahawks'}
def key(raw): return re.sub(r'[^a-z]', '', (raw or '').lower())

teams = json.load(open(D + 'teams.json'))
cache = {}
def resolve(pos, raw):
    k = key(raw)
    if pos == 'K':
        n = K[k]; s = stats['K'].get(n); pts, br = score_k(s); team = s['team'] if s else ''
    elif pos == 'DEF':
        t = DF[k]; s = stats['D'][t]; n = TEAMNAME[t] + ' D'; pts, br = score_d(s); team = t
    else:
        if k == 'gronk': return 'Rob Gronkowski (retired)', '', 0, [('Retired', 0)]
        n = TE_HENRY if (pos == 'TE' and k == 'henry') else P[k]
        s = stats['P'].get(n)
        if s is None: raise KeyError(n)
        pts, br = score_player(pos, s); team = s['team']
    return n, team, pts, br

rows = []
for t in teams:
    tot = 0; lineup = []
    for x in t['lineup']:
        n, team, pts, br = resolve(x['pos'], x['raw'])
        tot += pts
        lineup.append(dict(pos=x['pos'], raw=x['raw'], name=n, team=team, pts=pts, comm=x['pts'], breakdown=[[a, b] for a, b in br] if br and isinstance(br[0], tuple) else []))
    rows.append(dict(owner=t['owner'], total=tot, comm_total=t['total'], lineup=lineup))
json.dump(dict(teams=rows, games=games), open(D + 'scored.json', 'w'), indent=0)

# ---- report ----
diffs = {}
for r in rows:
    for x in r['lineup']:
        c = x['comm'] if isinstance(x['comm'], (int, float)) else None
        if c != x['pts']:
            diffs.setdefault((x['pos'], x['name']), set()).add((c, x['pts']))
print('PLAYER DIFFERENCES (commissioner -> mine):')
for (pos, n), v in sorted(diffs.items()):
    for c, m in v:
        x = next(x for r in rows for x in r['lineup'] if x['name'] == n and x['pos'] == pos)
        print(f"  {pos:3s} {n:24s} comm={c!s:>5} mine={m:>4}   {x['breakdown']}")
print('\nTEAM TOTALS that differ:')
for r in sorted(rows, key=lambda r: -r['total']):
    if r['total'] != r['comm_total']: print(f"  {r['owner']:20s} comm={r['comm_total']} mine={r['total']}")
