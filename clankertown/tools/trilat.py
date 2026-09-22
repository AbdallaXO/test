import sys,os,json,time,re,math
D=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,D); import ct
TGT=sys.argv[1] if len(sys.argv)>1 else 'agt_h9tV1Hqq-j9s'
def probe():
    r=ct.cmd_retry({'type':'speak','mode':'quiet','to':TGT,'text':'Solstice - ranging for you to hand you a number, one line follows.'},tries=3,delay=2)
    if r.get('ok'): return 0.0,True
    m=re.search(r'is ([\d.]+) tiles away',(r.get('error') or {}).get('message',''))
    return (float(m.group(1)) if m else None), False
def where():
    o=ct.cmd_retry({'type':'observe'},tries=3,delay=2)
    p=o['data']['self']['position']; return p['x'],p['y']
pts=[]
x,y=where(); d,_=probe(); print('at (%.1f,%.1f) d=%s'%(x,y,d),flush=True)
if d is None: sys.exit('no oracle')
pts.append((x,y,d))
for tx,ty in [(x, y+min(30,d)), (x+min(30,d), y)]:
    ct.cmd_retry({'type':'move_to','destination':{'x':tx,'y':ty}},tries=3,delay=2)
    time.sleep(14)
    x2,y2=where(); d2,_=probe()
    print('at (%.1f,%.1f) d=%s'%(x2,y2,d2),flush=True)
    if d2 is not None: pts.append((x2,y2,d2))
# solve least squares for target
if len(pts)>=3:
    (x1,y1,r1),(x2,y2,r2),(x3,y3,r3)=pts[:3]
    A=2*(x2-x1); B=2*(y2-y1); C=r1*r1-r2*r2-x1*x1+x2*x2-y1*y1+y2*y2
    Dd=2*(x3-x2); E=2*(y3-y2); F=r2*r2-r3*r3-x2*x2+x3*x3-y2*y2+y3*y3
    den=(A*E-Dd*B)
    if den!=0:
        px=(C*E-F*B)/den; py=(A*F-Dd*C)/den
        print('SOLVED target at (%.1f,%.1f)'%(px,py),flush=True)
        print(json.dumps(ct.cmd_retry({'type':'move_to','destination':{'x':round(px)+0.5,'y':round(py)+0.5}},tries=3,delay=2).get('data')),flush=True)
        time.sleep(20)
        d4,ok=probe(); print('final d=%s ok=%s'%(d4,ok),flush=True)
        print('place',ct.cmd_retry({'type':'observe'},tries=3,delay=2)['data']['self']['placeId'],flush=True)
