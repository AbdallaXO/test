"""Shared trust table: always from the NEWEST settled epoch file available, plus live board."""
import json,os,glob,re
D=os.path.dirname(os.path.abspath(__file__))
def newest_epoch_file():
    best=(None,-1)
    for f in glob.glob(D+'/*.json'):
        try: d=json.load(open(f))
        except Exception: continue
        if isinstance(d,dict) and 'scores' in d and 'epoch' in d and 'rules' in d:
            if d['epoch']>best[1]: best=(f,d['epoch'])
    return best
def load():
    f,ep=newest_epoch_file()
    T={}; extra={}
    if f:
        d=json.load(open(f))
        for r in d['scores']:
            T[r['name']]=r['trust']; extra[r['name']]=r
    for lb in ('F_leaderboard.json','LB6.json','LB5.json'):
        p=D+'/'+lb
        if os.path.exists(p):
            try:
                for r in json.load(open(p))['scores']: T.setdefault(r['name'],r['trust'])
            except Exception: pass
    return T,extra,ep
