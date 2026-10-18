"""League shorthand -> (canonical name, NFL team). Extend as new shorthands show up."""
import re
def key(raw): return re.sub(r'[^a-z]', '', (raw or '').lower())
PL = {  # key: (name, team)
 'maye': ('Drake Maye', 'NE'), 'mahomes': ('Patrick Mahomes', 'KC'), 'purdy': ('Brock Purdy', 'SF'), 'love': ('Jordan Love', 'GB'), 'jlove': ('Jordan Love', 'GB'),
 'dak': ('Dak Prescott', 'DAL'), 'cousins': ('Kirk Cousins', 'LV'), 'winston': ('Jameis Winston', 'NYG'), 'stroud': ('C.J. Stroud', 'HOU'), 'byoung': ('Bryce Young', 'CAR'), 'young': ('Bryce Young', 'CAR'),
 'rodgers': ('Aaron Rodgers', 'PIT'), 'stafford': ('Matthew Stafford', 'LAR'), 'caleb': ('Caleb Williams', 'CHI'), 'jallen': ('Josh Allen', 'BUF'), 'allen': ('Josh Allen', 'BUF'), 'brissett': ('Jacoby Brissett', 'ARI'),
 'kwalker': ('Kenneth Walker', 'KC'), 'walker': ('Kenneth Walker', 'KC'), 'warren': ('Jaylen Warren', 'PIT'), 'jwarren': ('Jaylen Warren', 'PIT'),
 'javwilliams': ('Javonte Williams', 'DAL'), 'javwill': ('Javonte Williams', 'DAL'), 'cook': ('James Cook', 'BUF'), 'jcook': ('James Cook', 'BUF'), 'bijan': ('Bijan Robinson', 'ATL'),
 'kwilliams': ('Kyren Williams', 'LAR'), 'jtaylor': ('Jonathan Taylor', 'IND'), 'taylor': ('Jonathan Taylor', 'IND'), 'stevenson': ('Rhamondre Stevenson', 'NE'), 'rstevenson': ('Rhamondre Stevenson', 'NE'),
 'rstephenson': ('Rhamondre Stevenson', 'NE'), 'rstvenson': ('Rhamondre Stevenson', 'NE'), 'swift': ("D'Andre Swift", 'CHI'), 'allgier': ('Tyler Allgeier', 'ARI'), 'henry': ('Derrick Henry', 'BAL'),
 'chubba': ('Chuba Hubbard', 'CAR'), 'hubbard': ('Chuba Hubbard', 'CAR'), 'irving': ('Bucky Irving', 'TB'), 'ewilson': ('Emanuel Wilson', 'SEA'), 'cmc': ('Christian McCaffrey', 'SF'),
 'mlyoyd': ('MarShawn Lloyd', 'GB'), 'mlloyd': ('MarShawn Lloyd', 'GB'), 'tuten': ('Bhayshul Tuten', 'JAX'), 'jeanty': ('Ashton Jeanty', 'LV'),
 'lamb': ('CeeDee Lamb', 'DAL'), 'olave': ('Chris Olave', 'NO'), 'mcmillan': ('Tetairoa McMillan', 'CAR'), 'tet': ('Tetairoa McMillan', 'CAR'), 'watson': ('Christian Watson', 'GB'), 'cwatson': ('Christian Watson', 'GB'),
 'pickens': ('George Pickens', 'DAL'), 'nabers': ('Malik Nabers', 'NYG'), 'evans': ('Mike Evans', 'SF'), 'dk': ('DK Metcalf', 'PIT'), 'golden': ('Matthew Golden', 'GB'), 'coker': ('Jalen Coker', 'CAR'),
 'pwash': ('Parker Washington', 'JAX'), 'nico': ('Nico Collins', 'HOU'), 'jsn': ('Jaxon Smith-Njigba', 'SEA'), 'london': ('Drake London', 'ATL'), 'puka': ('Puka Nacua', 'LAR'), 'dadams': ('Davante Adams', 'LAR'),
 'adams': ('Davante Adams', 'LAR'), 'zayflow': ('Zay Flowers', 'BAL'), 'flowers': ('Zay Flowers', 'BAL'), 'mclaurin': ('Terry McLaurin', 'WAS'), 'kallen': ('Keenan Allen', 'IND'), 'dboston': ('Denzel Boston', 'CLE'),
 'ttucker': ('Tre Tucker', 'LV'), 'worthy': ('Xavier Worthy', 'KC'), 'downs': ('Josh Downs', 'IND'), 'kcoleman': ('Keon Coleman', 'BUF'), 'mwilson': ('Michael Wilson', 'ARI'), 'burden': ('Luther Burden', 'CHI'),
 'odunze': ('Rome Odunze', 'CHI'), 'gwilson': ('Garrett Wilson', 'NYJ'),
 'kraft': ('Tucker Kraft', 'GB'), 'likely': ('Isaiah Likely', 'NYG'), 'bowers': ('Brock Bowers', 'LV'), 'kincaid': ('Dalton Kincaid', 'BUF'), 'higbee': ('Tyler Higbee', 'LAR'), 'kittle': ('George Kittle', 'SF'),
 'mcbride': ('Trey McBride', 'ARI'), 'jjohnson': ('Juwan Johnson', 'NO'), 'andrews': ('Mark Andrews', 'BAL'), 'kelce': ('Travis Kelce', 'KC'), 'waller': ('Darren Waller', 'CAR'), 'TE:henry': ('Hunter Henry', 'NE'),
 'goedart': ('Dallas Goedert', 'PHI'), 'goedert': ('Dallas Goedert', 'PHI'), 'friemuth': ('Pat Freiermuth', 'PIT'), 'freiermuth': ('Pat Freiermuth', 'PIT'), 'fanin': ('Harold Fannin', 'CLE'), 'fannin': ('Harold Fannin', 'CLE'),
 'gronk': ('Rob Gronkowski (retired)', ''),
 # kickers
 'folk': ('Nick Folk', 'ATL'), 'boswell': ('Chris Boswell', 'PIT'), 'little': ('Cam Little', 'JAX'), 'schrader': ('Spencer Shrader', 'IND'), 'shraeder': ('Spencer Shrader', 'IND'), 'scrader': ('Spencer Shrader', 'IND'),
 'shrader': ('Spencer Shrader', 'IND'), 'smack': ('Trey Smack', 'GB'), 'myers': ('Jason Myers', 'SEA'), 'fairbain': ("Ka'imi Fairbairn", 'HOU'), 'fairbairn': ("Ka'imi Fairbairn", 'HOU'), 'zvada': ('Dominik Zvada', 'NYG'),
 'aubrey': ('Brandon Aubrey', 'DAL'), 'bass': ('Tyler Bass', 'BUF'), 'santos': ('Cairo Santos', 'CHI'), 'loop': ('Tyler Loop', 'BAL'), 'gay': ('Matt Gay', 'LV'), 'borregalis': ('Andres Borregales', 'NE'),
 'borregales': ('Andres Borregales', 'NE'), 'butker': ('Harrison Butker', 'KC'), 'elliott': ('Jake Elliott', 'PHI'), 'piniero': ('Eddy Pineiro', 'SF'), 'pineiro': ('Eddy Pineiro', 'SF'), 'jsanders': ('Jason Sanders', 'NYJ'),
 'mcglaughlin': ('Chase McLaughlin', 'TB'), 'mclaughlin': ('Chase McLaughlin', 'TB'), 'reichard': ('Will Reichard', 'MIN'),
}
DF = {'chiefs': 'KC', 'kc': 'KC', 'steelers': 'PIT', 'carolina': 'CAR', 'panthers': 'CAR', 'giants': 'NYG', 'pats': 'NE', 'patriots': 'NE', 'rams': 'LAR', 'sanfran': 'SF', '49ers': 'SF', 'niners': 'SF',
      'ravens': 'BAL', 'colts': 'IND', 'seattle': 'SEA', 'bills': 'BUF', 'browns': 'CLE', 'cowboys': 'DAL', 'jags': 'JAX', 'jaguars': 'JAX', 'texans': 'HOU', 'eagles': 'PHI', 'bucs': 'TB', 'saints': 'NO',
      'falcons': 'ATL', 'bears': 'CHI', 'titans': 'TEN', 'jets': 'NYJ', 'raiders': 'LV', 'chargers': 'LAC', 'cardinals': 'ARI', 'packers': 'GB', 'commanders': 'WAS', 'broncos': 'DEN', 'vikings': 'MIN', 'lions': 'DET', 'dolphins': 'MIA', 'bengals': 'CIN'}
TEAMNAME = {'KC': 'Chiefs', 'PIT': 'Steelers', 'CAR': 'Panthers', 'NYG': 'Giants', 'NE': 'Patriots', 'LAR': 'Rams', 'SF': '49ers', 'BAL': 'Ravens', 'IND': 'Colts', 'SEA': 'Seahawks', 'BUF': 'Bills',
            'CLE': 'Browns', 'DAL': 'Cowboys', 'JAX': 'Jaguars', 'HOU': 'Texans', 'PHI': 'Eagles', 'TB': 'Buccaneers', 'NO': 'Saints', 'ATL': 'Falcons', 'CHI': 'Bears', 'TEN': 'Titans', 'NYJ': 'Jets',
            'LV': 'Raiders', 'LAC': 'Chargers', 'ARI': 'Cardinals', 'GB': 'Packers', 'WAS': 'Commanders', 'DEN': 'Broncos', 'MIN': 'Vikings', 'DET': 'Lions', 'MIA': 'Dolphins', 'CIN': 'Bengals'}
def resolve(pos, raw):
    k = key(raw)
    if pos == 'DEF':
        t = DF[k]; return TEAMNAME[t] + ' D', t
    if pos == 'TE' and 'TE:' + k in PL: return PL['TE:' + k]
    return PL[k]
