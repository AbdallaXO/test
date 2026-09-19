import json,subprocess,os,sys,time
D=os.path.dirname(os.path.abspath(__file__))
def send(cid,body):
    r=subprocess.run([D+'/send.sh',cid,json.dumps(body)],capture_output=True,text=True,cwd=D)
    try: return json.loads(r.stdout)
    except Exception: return {'ok':False,'error':{'code':'nojson'}}
def say(cid,text,tries=4):
    for k in range(tries):
        res=send(cid if k==0 else cid,{'type':'speak','mode':'nearby','text':text})
        if res.get('ok'):
            d=res.get('data',{})
            mid=((d.get('message') or {}).get('id')) or d.get('messageId') or d.get('id')
            if mid:
                with open(D+'/my_msgs.txt','a') as f: f.write(mid+'\n')
            return True,'id=%s'%mid
        er=res.get('error',{}) or {}
        if er.get('code')=='cooldown':
            w=min(45,(er.get('retryAfterMs',8000)/1000.0)+2)
            time.sleep(w); continue
        return False,er.get('code','?')
    return False,'cooldown-exhausted'
L=json.load(open(sys.argv[1]))
for cid,t in L:
    ok,info=say(cid,t)
    print(('OK  ' if ok else 'FAIL'),cid,info)
