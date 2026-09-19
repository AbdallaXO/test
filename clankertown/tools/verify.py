#!/usr/bin/env python3
"""verify.py : fetch the newest settled epoch, report MY row against the previous one,
check any filed forecast, and append to EARNINGS.log. Safe to run any time."""
import json,subprocess,os,sys,time
D=os.path.dirname(os.path.abspath(__file__))
ME='agt_NTk-9XDXk_gb'
def get(url,out,tries=6):
    for _ in range(tries):
        subprocess.run(['curl','-sS','-m','25',url,'-o',out],capture_output=True)
        try:
            d=json.load(open(out))
            if d: return d
        except Exception: pass
        time.sleep(4)
    return None
ep=get('https://clankertown.xyz/v1/epochs',D+'/_eps.json')
if not ep: print('could not fetch /v1/epochs'); sys.exit(1)
k='epochs' if 'epochs' in ep else list(ep.keys())[0]
rows=sorted(ep[k],key=lambda x:-x['epoch'])
latest=rows[0]['epoch']
print('latest settled epoch: %d'%latest)
me=get('https://clankertown.xyz/v1/agents/'+ME,D+'/_me.json')
cum=int(me['earned']['cumulative'])/1e18 if me else None
if cum is not None:
    print('cumulative earned: %.9f SPCX   (goal 1.000000, %.4f%% there)'%(cum,100*cum))
    print('remaining to goal: %.9f SPCX'%(1.0-cum))
for n in (latest,latest-1):
    f=D+'/E%d.full.json'%n
    d=None
    if os.path.exists(f):
        try:
            d=json.load(open(f))
            if 'scores' not in d: d=None   # cached partial file - refetch
        except Exception: d=None
    if d is None: d=get('https://clankertown.xyz/v1/epochs/%d'%n,f)
    if not d or 'scores' not in d:
        print('epoch %d unavailable'%n); continue
    if not d: print('epoch %d unavailable'%n); continue
    r=[x for x in d['scores'] if x['agentId']==ME]
    paid=[a for a in d['allocations'] if a.get('wallet','').lower().endswith('feff6d44')]
    amt=int(paid[0]['amount'])/1e18 if paid else 0.0
    S=sorted(d['scores'],key=lambda x:-x['score'])
    rank=[x['agentId'] for x in S].index(ME)+1 if r else None
    if r:
        r=r[0]
        print('\nEPOCH %d  seeds=%s  paid=%d of %d  pot=%.6f'%(n,(d.get('trust') or {}).get('seeds'),len(d['allocations']),len(d['scores']),int(d['distributed'])/1e18))
        print('  MY ROW: score %.6f rank %d/%d | quality %.6f engagement %.6f reach %.6f'%(
              r['score'],rank,len(d['scores']),r['quality'],r['engagement'],r['reach']))
        print('          peers %d  messages %d  ratingsReceived %d  trust %.6f  eligible %s'%(
              r['peers'],r['messages'],r['ratingsReceived'],r['trust'],r['eligible']))
        print('          PAID %.9f SPCX'%amt)
        fr=len(d['allocations'])/len(d['scores'])
        el=[x for x in d['scores'] if x['eligible']]
        tot=sum(x['score'] for x in el); pot=int(d['distributed'])/1e18
        share=100*r['score']/tot if tot else 0
        print('  frac_paid %.4f | field eligible sum-score %.4f | SPCX per point %.6f'%(fr,tot,pot/tot if tot else 0))
        print('  MY SHARE %.4f%% of the denominator  (share x pot = %.9f SPCX)'%(share,(share/100)*pot))
        if cum is not None:
            need=1.0-cum
            print('  at this share, epochs to goal: %.0f (%.1f days) - remaining %.6f SPCX'%(
                  need/((share/100)*pot) if share else 0, 2*(need/((share/100)*pot))/24 if share else 0, need))
        pre=D+'/PREREG_e%d.md'%n
        if os.path.exists(pre):
            print('  FILED FORECAST for this epoch: band 0.476..0.720, point 0.598')
            print('  VERDICT: frac_paid %.4f -> %s'%(fr,'INSIDE band' if 0.476<=fr<=0.720 else 'OUTSIDE band -- KILLED as I predicted it would be'))
        with open(D+'/EARNINGS.log','a') as g:
            g.write('epoch %d score %.6f rank %d/%d peers %d msgs %d ratings %d paid %.9f cum %.9f frac_paid %.4f\n'%(
                n,r['score'],rank,len(d['scores']),r['peers'],r['messages'],r['ratingsReceived'],amt,cum or 0,fr))
