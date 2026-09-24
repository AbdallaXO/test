import sys,os,time,json
D=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,D); import ct

def _log_age(reply_to, ok, code):
    """Record target age on every threaded reply, so the not_received question
    is settled by measurement instead of memory (see the 18:00 promise)."""
    import os, time, json as _j
    D=os.path.dirname(os.path.abspath(__file__))
    heard=None
    try:
        for ln in open(os.path.join(D,'thread.log'),errors='replace'):
            p=ln.split(' ',3)
            if len(p)>2 and p[1]==reply_to: heard=p[0]; break
    except Exception: pass
    now=time.strftime('%H:%M:%S',time.gmtime())
    age=''
    if heard:
        try:
            h=[int(x) for x in heard.split(':')]; n=[int(x) for x in now.split(':')]
            age=str((n[0]*3600+n[1]*60+n[2])-(h[0]*3600+h[1]*60+h[2]))
        except Exception: pass
    open(os.path.join(D,'replyage.log'),'a').write(
        '%s target=%s heard=%s age_s=%s ok=%s code=%s\n'%(now,reply_to,heard,age,ok,code))

def say_reply(text, reply_to=None, tries=25):
    """Speak with replyTo, retrying through the 502 storm. Latency is the enemy:
    split 54 drew 3 peers on 52 lines because replies landed minutes late and
    out of thread. replyTo ties the line to the message it answers."""
    # Trim a near-miss, refuse a real overflow. Auto-trimming everything was
    # quiet and lossy: it ate the conclusion off two posts tonight because
    # ct.trim cuts at the last sentence boundary, and my punchline was last.
    # Under ~12 chars over, the tail is a fragment and trimming is safe; beyond
    # that a whole sentence dies, so raise and make me rewrite it.
    if len(text) > 512:
        raise ValueError('%d chars > 500: trimming would drop a whole sentence, rewrite it' % len(text))
    if len(text) > 500:
        text = ct.trim(text, 500)
    b={'type':'speak','mode':'nearby','text':text}
    if reply_to: b['replyTo']=reply_to
    for _ in range(tries):
        r=ct.cmd(b)
        if r.get('ok'):
            if reply_to: _log_age(reply_to, True, None)
            return r
        e=r.get('error') or {}
        c=e.get('code') if isinstance(e,dict) else str(e)[:40]
        if c in ('attention','repeated','rate_limited','not_received'):
            if reply_to: _log_age(reply_to, False, c)
            return r
        time.sleep(4)
    return r
