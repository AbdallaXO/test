#!/usr/bin/env python3
"""ratejson.py <judgments.json> : [[messageId,usefulness,clarity,onTopic,agreement],...]
Rates only ids still in heard_now.json. Judged on usefulness, clarity and on-topic alone."""
import json,subprocess,os,sys
D=os.path.dirname(os.path.abspath(__file__))
rh={m['id']:m for m in json.load(open(D+'/heard_now.json'))}
J=json.load(open(sys.argv[1])); ok=0; out=[]
for mid,u,c,t,a in J:
    if mid not in rh: out.append((mid[-6:],'notheard')); continue
    b={'type':'rate_response','messageId':mid,'usefulness':u,'clarity':c,'onTopic':bool(t),'agreement':a}
    r=subprocess.run([D+'/send.sh','rj-%s'%mid[-8:],json.dumps(b)],capture_output=True,text=True,cwd=D)
    try: d=json.loads(r.stdout)
    except Exception: d={'ok':False,'error':{'code':'nojson'}}
    if d.get('ok'): ok+=1
    else: out.append((rh[mid].get('senderName'),d.get('error',{}).get('code')))
print('accepted %d of %d | issues: %s'%(ok,len(J),out))
