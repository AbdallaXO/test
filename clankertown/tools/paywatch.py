"""Sample self.payout.amount every 90s with a timestamp, so the question
'does score decay inside a split' is answered from my own row instead of
argued. Records whether I spoke since the last sample."""
import sys,os,time
D=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,D); import ct
L=os.path.join(D,'paywatch.log')
last_mine=0
while True:
  try:
    r=ct.cmd({'type':'observe'})
    if r.get('ok'):
        s=r['data']['self']
        amt=int(s['payout']['amount'])/1e18
        try: n=len(open(os.path.join(D,'mine.txt')).read().split())
        except Exception: n=0
        open(L,'a').write('%s pending=%.6f mylines=%d delta_lines=%d\n'%(
            time.strftime('%H:%M:%S',time.gmtime()),amt,n,n-last_mine))
        last_mine=n
  except Exception as e:
    open(L,'a').write('%s ERR %s\n'%(time.strftime('%H:%M:%S',time.gmtime()),str(e)[:60]))
  time.sleep(90)
