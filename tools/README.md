Scoring tools for the scoreboard.
- score.py: league scoring rules + scorer (box-score JSON -> per-player points with breakdowns)
- template.html: page template (__DATA__ / __META__ placeholders) -> ../index.html
- data/weekN/: lineups (teams.json), box scores (stats_*.json), page data

Live update loop (Week 6+):
1. Sportradar scores (fetch_sports_data scores) -> which games are live/final.
2. For each live/final game not yet frozen: game_stats (scoring plays = TD lengths, FG distances; team defense sacks/INT/FR; FG miss buckets)
   + CBS box via WebFetch https://www.cbssports.com/nfl/gametracker/boxscore/<cbs id>/?r=<unique> (cache-buster required).
3. Write data/weekN/games/AWAY-HOME.json (only lineup players needed; see names.py), status live/final + clock.
4. python3 tools/build_week.py N  -> index.html; commit + push.
