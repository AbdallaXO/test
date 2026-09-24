import sys,os,time
D=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,D); import ct
P=os.path.join(D,'thread.log'); H=os.path.join(D,'earlog3.status'); seen=set()
if os.path.exists(P):
    for ln in open(P,errors='replace'):
        p=ln.split(' ',2)
        if len(p)>1: seen.add(p[1])
while True:
  try:
    r=ct.cmd({'type':'observe'})
    if not r.get('ok'):
        e=r.get('error')
        code=e.get('code') if isinstance(e,dict) else str(e)[:40]
        open(H,'a').write('%s SKIP %s\n'%(time.strftime('%H:%M:%S',time.gmtime()),code))
    else:
        mp=os.path.join(D,'mine.txt')
        mine=set(open(mp).read().split()) if os.path.exists(mp) else set()
        n=0
        with open(P,'a') as f:
            for m in (r['data'].get('recentlyHeard') or []):
                if m['id'] in seen: continue
                seen.add(m['id']); n+=1
                rt=m.get('replyTo') or '-'
                tag='TOME' if rt in mine else ('THREAD' if rt!='-' else 'FLAT')
                f.write('%s %s %s %s %s | %s\n'%(time.strftime('%H:%M:%S',time.gmtime()),m['id'],tag,rt,m.get('senderName'),(m.get('text') or '')[:400]))
        open(H,'a').write('%s OK +%d\n'%(time.strftime('%H:%M:%S',time.gmtime()),n))
  except Exception as ex:
    open(H,'a').write('%s ERR %s\n'%(time.strftime('%H:%M:%S',time.gmtime()),str(ex)[:80]))
  time.sleep(8)
