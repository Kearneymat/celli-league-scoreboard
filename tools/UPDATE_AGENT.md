# Live stat-collection instructions (for a helper agent)

Repo: /home/claude/celli-league-scoreboard. Week N data: data/weekN/.
- schedule.json: games with Sportradar `id` and CBS `cbs` id.
- needed.json: NFL team -> list of [pos, player name] that appear in league lineups. Only these players matter.

For EACH game you are told to update:
1. Call mcp__widgets__fetch_sports_data(data_type="game_stats", league="nfl", game_id=<id>). Use it for: status, quarter/clock, score,
   scoring_plays (TD lengths for passer/rusher/receiver, made FG distances, missed/blocked XPs, 2-pt conversions, defensive/return TDs),
   team_stats.<team>.defense (sacks, interceptions), team_stats.<team>.fumbles.opp_rec (= that team's fumble recoveries of opponent fumbles),
   summary.safeties, field_goals attempts_*/made_* buckets (to find MISSED FG ranges).
2. WebFetch https://www.cbssports.com/nfl/gametracker/boxscore/<cbs>/?r=<random 6 chars> (the ?r= cache-buster is REQUIRED; use a new value every time)
   asking for every player's passing (C/ATT YDS TD INT), rushing (CAR YDS TD), receiving (REC YDS TD), lost fumbles by player, and kicking.
   If CBS clock/score lags Sportradar noticeably, refetch once with a new ?r=.
3. Write data/weekN/games/<AWAY>-<HOME>.json (use the schedule's abbreviations, e.g. LAR not LA, JAX not JAC):
{"status":"live"|"final","clock":"Q2 5:12" (or "Halftime", "Final", "Final/OT"),"score":{"AWAY":n,"HOME":n},
 "players":{"<exact name from needed.json>":{"pass_cmp":0,"pass_yds":0,"pass_td_lengths":[],"int":0,"rush_att":0,"rush_yds":0,"rush_td_lengths":[],
            "rec":0,"rec_yds":0,"rec_td_lengths":[],"ret_td_lengths":[],"two_pt":0,"fl":0}},   # omit zero keys; include only needed players who have recorded any stat
 "kickers":{"<name>":{"fg_made_dist":[..],"fg_missed_dist":[..],"miss_label":{"45":"40-49 yd"},"xp_made":n,"xp_missed":n}},
 "defenses":{"AWAY":{"sacks":n,"int":n,"fum_rec":n,"safeties":n,"def_st_td_lengths":[..]},"HOME":{...}}}
   - pass_td_lengths for the QB = yardage of each TD pass he threw (from scoring plays). rec_td_lengths/rush_td_lengths likewise.
   - two_pt: credit the player who scored (runner/receiver) for a successful 2-pt conversion.
   - fl: fumbles LOST only. Team lost_fumbles is in team_stats; attribute to the player if CBS/play-by-play shows who; if a needed player may have lost one but you can't tell, say so in your reply.
   - Missed FG with unknown exact distance: use the bucket midpoint (20-29 -> 25, 30-39 -> 35, 40-49 -> 45, 50+ -> 55) and set miss_label.
   - Return/defensive TDs by a team's defense or special teams go in that team's def_st_td_lengths.
4. Reply with ONE short line per game: "AWAY-HOME status clock score; anything uncertain". Nothing else.
