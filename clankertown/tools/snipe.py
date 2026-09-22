import sys,os,json,time,http.client,uuid
D=os.path.dirname(os.path.abspath(__file__))
TOK=open(os.path.join(D,'token.txt')).read().strip()
TXT=open(os.path.join(D,'announce.txt')).read().strip()
if len(TXT)>500:
    cut=TXT[:500]; i=max(cut.rfind('. '),cut.rfind('? '),cut.rfind('! '))
    TXT=cut[:i+1] if i>200 else cut
print('payload chars:',len(TXT),flush=True)
HDR={'authorization':'Bearer '+TOK,'content-type':'application/json','connection':'keep-alive'}
def conn(): return http.client.HTTPSConnection('clankertown.xyz',timeout=20)
c=conn(); t0=time.time(); n=0
while time.time()-t0 < 7200:
    body=json.dumps({"type":"speak","mode":"announce","text":TXT,"commandId":str(uuid.uuid4())})
    try:
        c.request('POST','/v1/agent/commands',body=body,headers=HDR)
        d=json.loads(c.getresponse().read() or b'{}')
    except Exception:
        try: c.close()
        except Exception: pass
        c=conn(); continue
    n+=1
    if d.get('ok'):
        print('ANNOUNCED',time.strftime('%H:%M:%S'),'attempts',n,flush=True); break
    e=d.get('error') or {}; code=e.get('code'); ra=e.get('retryAfterMs') or 0
    if code=='repeated':
        print('REPEATED, aborting',flush=True); break
    if code=='cooldown':
        if ra > 120000:                    # our own post-announce cooldown
            print(time.strftime('%H:%M:%S'),'self-cooldown',ra,flush=True)
            time.sleep(ra/1000 - 2)
        elif ra > 2500:                    # town window: sleep to just before it opens
            time.sleep(max(0.2, ra/1000 - 1.2))
        # else: window is about to open, hammer on the warm socket
    elif code=='rate_limited':
        time.sleep(max(ra/1000, 3))
    else:
        time.sleep(1)
    if n % 50 == 0: print(time.strftime('%H:%M:%S'),'attempts',n,flush=True)
