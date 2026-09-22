import sys,os,time,json
D=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,D); import ct
def say_reply(text, reply_to=None, tries=25):
    """Speak with replyTo, retrying through the 502 storm. Latency is the enemy:
    split 54 drew 3 peers on 52 lines because replies landed minutes late and
    out of thread. replyTo ties the line to the message it answers."""
    if len(text) > 500: raise ValueError('%d chars > 500' % len(text))
    b={'type':'speak','mode':'nearby','text':text}
    if reply_to: b['replyTo']=reply_to
    for _ in range(tries):
        r=ct.cmd(b)
        if r.get('ok'): return r
        e=r.get('error') or {}; c=e.get('code')
        if c in ('attention','repeated','rate_limited'): return r
        time.sleep(4)
    return r
