"""Append every line from my OWN observe recentlyHeard to earshot.log.

heard.log is written by daemon.py's polling and is a SAMPLE - it missed the
line that cost me a 15-minute mute in split 51. recentlyHeard from my own
observe is the authoritative record of what was said in my earshot.
"""
import sys,os,json,time
D=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,D); import ct
LOG=os.path.join(D,'earshot.log')
seen=set()
if os.path.exists(LOG):
    for ln in open(LOG):
        p=ln.split(' | ',1)[0].split()
        if len(p)>1: seen.add(p[1])
while True:
    try:
        r=ct.cmd_retry({'type':'observe'},tries=2,delay=2)
        for m in ((r.get('data') or {}).get('recentlyHeard') or []):
            mid=m.get('id')
            if mid and mid not in seen:
                seen.add(mid)
                with open(LOG,'a') as f:
                    f.write('%s %s %s | %s\n'%(time.strftime('%H:%M:%S'),mid,m.get('senderName',''),(m.get('text') or '').replace('\n',' ')))
    except Exception:
        pass
    time.sleep(8)
