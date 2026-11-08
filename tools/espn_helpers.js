// Paste into the browser pane on an espn.com page. Then: await __pull(true)
window.__ab=x=>({LA:'LAR',JAC:'JAX',WSH:'WAS'}[x]||x);
window.__DATE=window.__DATE||'20261108';
window.__events=async()=>{const j=await fetch('https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates='+__DATE+'&_='+Date.now()).then(r=>r.json());return j.events.map(e=>{const c=e.competitions[0];const h=c.competitors.find(t=>t.homeAway=='home'),a=c.competitors.find(t=>t.homeAway=='away');return {id:e.id,key:__ab(a.team.abbreviation)+'-'+__ab(h.team.abbreviation),state:e.status.type.state,detail:e.status.type.shortDetail}})};
window.__game=async(id)=>{const j=await fetch('https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event='+id+'&_='+Date.now()).then(r=>r.json());
const comp=j.header.competitions[0];const st=comp.status.type;const teams={};comp.competitors.forEach(c=>teams[c.team.id]=__ab(c.team.abbreviation));
const score={};comp.competitors.forEach(c=>score[__ab(c.team.abbreviation)]=+c.score||0);
const P={},K={};const g=(n)=>P[n]=P[n]||{};
(j.boxscore.players||[]).forEach(tp=>{const tm=__ab(tp.team.abbreviation);tp.statistics.forEach(s=>{const keys=s.keys;s.athletes.forEach(a=>{const n=a.athlete.displayName+'|'+tm;const v={};keys.forEach((k,i)=>v[k]=a.stats[i]);
if(s.name=='passing'){const [c]=(v['completions/passingAttempts']||'0/0').split('/');Object.assign(g(n),{pass_cmp:+c,pass_yds:+v.passingYards,int:+v.interceptions})}
if(s.name=='rushing')Object.assign(g(n),{rush_att:+v.rushingAttempts,rush_yds:+v.rushingYards});
if(s.name=='receiving')Object.assign(g(n),{rec:+v.receptions,rec_yds:+v.receivingYards});
if(s.name=='fumbles'&&+v.fumblesLost)g(n).fl=+v.fumblesLost;
if(s.name=='kicking'){const [fm,fa]=(v['fieldGoalsMade/fieldGoalAttempts']||'0/0').split('/');const [xm,xa]=(v['extraPointsMade/extraPointAttempts']||'0/0').split('/');K[n]={fgm:+fm,fga:+fa,xp_made:+xm,xp_missed:(+xa)-(+xm)}}
})})});
const tds=[],fgs=[],two=[],dst=[],saf=[];
(j.scoringPlays||[]).forEach(sp=>{const t=sp.text||'';const tm=teams[sp.team.id];const ty=sp.type.text||'';
 if(/Safety/i.test(ty)){saf.push(tm);return}
 if(/Field Goal/i.test(ty)){const m=t.match(/^(.*?) (\d+) Ya?r?d? Field Goal/i);if(m)fgs.push([m[1],+m[2],tm]);return}
 if(/(Interception|Fumble|Punt|Kickoff|Blocked).*Touchdown|Return Touchdown/i.test(ty)){const m=t.match(/(\d+) Ya?r?d/);dst.push([tm,m?+m[1]:0,t]);}
 else if(/Touchdown/i.test(ty)){let m=t.match(/^(.*?) (\d+) Ya?r?d pass from (.*?)( \(|,|$)/i);if(m)tds.push({type:'pass',rec:m[1],qb:m[3],len:+m[2],tm});else{m=t.match(/^(.*?) (\d+) Ya?r?d (run|rush)/i);if(m)tds.push({type:'rush',who:m[1],len:+m[2],tm});else tds.push({type:'?',t,tm})}}
 const tw=t.match(/\(([^()]*?)(Two-Point|2-pt|two point)[^()]*\)/i);if(tw&&!/fail/i.test(tw[0]))two.push([tw[0],tm]);
});
const miss=[];(j.drives?.previous||[]).forEach(d=>(d.plays||[]).forEach(p=>{const ty=p.type?.text||'';if(/Field Goal Missed|Blocked Field Goal/i.test(ty)){const m=(p.text||'').match(/^(.*?) (\d+) ya?r?d/i);miss.push([m?m[1].trim():p.text,m?+m[2]:0,teams[d.team?.id]])}}));
const tstat={};(j.boxscore.teams||[]).forEach(t=>{const o={};t.statistics.forEach(s=>o[s.name]=s.displayValue);tstat[__ab(t.team.abbreviation)]=o});
const ab=Object.keys(score);const D={};ab.forEach((tm,i)=>{const op=ab[1-i];const so=tstat[op]||{};D[tm]={sacks:+((so.sacksYardsLost||'0-0').split('-')[0]),int:+(so.interceptions||0),fum_rec:+(so.fumblesLost||0),safeties:saf.filter(x=>x==tm).length,def_st_td_lengths:dst.filter(x=>x[0]==tm).map(x=>x[1])}});
const clock=st.state=='post'?(st.shortDetail.includes('OT')?'Final/OT':'Final'):st.state=='pre'?'Pregame':(st.shortDetail||'');
return {status:st.state=='post'?'final':st.state=='in'?'live':'pre',clock,score,P,K,tds,fgs,miss,two,dst:dst.map(x=>x[2]),D}};
window.__last=s=>{s=s.toLowerCase().replace(/\./g,' ').replace(/'/g,'').replace(/\b(jr|sr|ii|iii|iv)\b/g,'').trim().split(/\s+/);return s[s.length-1]};
window.__fin=window.__fin||{};
window.__pull=async(skipFinal)=>{const ev=await __events();const out={};for(const e of ev){if(e.state=='pre')continue;if(skipFinal&&__fin[e.key])continue;try{const r=await __game(e.id);const P={};for(const [k,v] of Object.entries(r.P)){const [n,tm]=k.split('|');if((__need[tm]||[]).includes(__last(n)))P[k]=v}r.P=P;const K={};for(const [k,v] of Object.entries(r.K)){const [n,tm]=k.split('|');if((__need[tm]||[]).includes(__last(n)))K[k]=v}r.K=K;out[e.key]=r;if(r.status=='final')__fin[e.key]=1}catch(err){out[e.key]={err:String(err)}}}return JSON.stringify(out,(k,v)=>(Array.isArray(v)&&v.length==0&&k!='tds')||(v===0&&!/^[A-Z]{2,3}$/.test(k))?undefined:v)};
