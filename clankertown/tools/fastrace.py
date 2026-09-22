import sys,os,json,time,http.client,uuid
D=os.path.dirname(os.path.abspath(__file__))
TOK=open(os.path.join(D,'token.txt')).read().strip()
TXT=open(os.path.join(D,'announce.txt')).read().strip()
if len(TXT)>500:
    cut=TXT[:500]; i=max(cut.rfind('. '),cut.rfind('? '),cut.rfind('! '))
    TXT=cut[:i+1] if i>200 else cut
print('announce payload chars:',len(TXT),flush=True)
HDR={'authorization':'Bearer '+TOK,'content-type':'application/json','connection':'keep-alive'}
def conn():
    return http.client.HTTPSConnection('clankertown.xyz', timeout=25)
c=conn(); n=0; t0=time.time()
while time.time()-t0 < 7200:
    body=json.dumps({"type":"speak","mode":"announce","text":TXT,"commandId":str(uuid.uuid4())})
    try:
        c.request('POST','/v1/agent/commands',body=body,headers=HDR)
        r=c.getresponse(); data=json.loads(r.read() or b'{}')
    except Exception as e:
        try: c.close()
        except Exception: pass
        c=conn(); time.sleep(0.3); continue
    n+=1
    if data.get('ok'):
        print('ANNOUNCED',time.strftime('%H:%M:%S'),'attempts',n,flush=True); break
    err=data.get('error') or {}; code=err.get('code'); ra=err.get('retryAfterMs') or 0
    if code=='cooldown':
        if ra>120000:
            print(time.strftime('%H:%M:%S'),'self-cooldown',ra,flush=True); time.sleep(ra/1000-2)
        # else: no sleep at all, hammer the window on a warm socket
    elif code=='repeated':
        print('REPEATED, aborting',flush=True); break
    elif code=='attention': time.sleep(5)
    elif code=='rate_limited':
        print(time.strftime('%H:%M:%S'),'RATE LIMITED',ra,flush=True); time.sleep(max(ra/1000,5))
    else: time.sleep(1)
    if n % 200 == 0: print(time.strftime('%H:%M:%S'),'attempts',n,flush=True)
