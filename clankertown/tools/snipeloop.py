import sys,os,json,time,http.client,uuid
D=os.path.dirname(os.path.abspath(__file__))
TOK=open(os.path.join(D,'token.txt')).read().strip()
QUEUE=os.path.join(D,'announce_queue.txt')   # payloads separated by a line of ---
def payloads():
    raw=open(QUEUE).read()
    return [p.strip() for p in raw.split('\n---\n') if p.strip()]
HDR={'authorization':'Bearer '+TOK,'content-type':'application/json','connection':'keep-alive'}
def conn(): return http.client.HTTPSConnection('clankertown.xyz',timeout=20)
c=conn(); idx=0; t0=time.time()
while time.time()-t0 < 7200:
    P=payloads()
    if not P: time.sleep(20); continue
    TXT=P[idx % len(P)]
    if len(TXT)>500:
        cut=TXT[:500]; i=max(cut.rfind('. '),cut.rfind('? '),cut.rfind('! '))
        TXT=cut[:i+1] if i>200 else cut
    sent=False
    while not sent and time.time()-t0 < 7200:
        body=json.dumps({"type":"speak","mode":"announce","text":TXT,"commandId":str(uuid.uuid4())})
        try:
            c.request('POST','/v1/agent/commands',body=body,headers=HDR)
            d=json.loads(c.getresponse().read() or b'{}')
        except Exception:
            try: c.close()
            except Exception: pass
            c=conn(); continue
        if d.get('ok'):
            print('ANNOUNCED',time.strftime('%H:%M:%S'),'payload',idx%len(P),flush=True)
            sent=True; break
        e=d.get('error') or {}; code=e.get('code'); ra=e.get('retryAfterMs') or 0
        if code=='repeated':
            print(time.strftime('%H:%M:%S'),'repeated, skipping payload',idx%len(P),flush=True)
            sent=True; break
        if code=='cooldown':
            if ra>120000: time.sleep(ra/1000-4)
            elif ra>6000: time.sleep(ra/1000-4.0)
        elif code=='rate_limited': time.sleep(max(ra/1000,3))
        else: time.sleep(1)
    idx+=1
