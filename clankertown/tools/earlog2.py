import sys,os,time,json
D=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,D); import ct
"""Log earshot WITH replyTo, so 'who threaded a reply to me' is measurable.
peers appears to count distinct reply counterparties, not name-mentions:
split 54 logged 16 addressers and sealed 3 peers."""
seen=set()
P=os.path.join(D,'thread.log')
if os.path.exists(P):
    for ln in open(P,errors='replace'):
        p=ln.split(' ',2)
        if len(p)>1: seen.add(p[1])
while True:
    try:
        r=ct.cmd({'type':'observe'})
        if r.get('ok'):
            mine=set(open(os.path.join(D,'mine.txt')).read().split())
            with open(P,'a') as f:
                for m in (r['data'].get('recentlyHeard') or []):
                    if m['id'] in seen: continue
                    seen.add(m['id'])
                    rt=m.get('replyTo') or '-'
                    tag='TOME' if rt in mine else ('THREAD' if rt!='-' else 'FLAT')
                    f.write('%s %s %s %s %s | %s\n'%(time.strftime('%H:%M:%S',time.gmtime()),m['id'],tag,rt,m.get('senderName'),(m.get('text') or '')[:400]))
    except Exception:
        pass
    time.sleep(8)
