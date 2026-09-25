#!/usr/bin/env python3
import json, sys, uuid, urllib.request, os
D=os.path.dirname(os.path.abspath(__file__))
TOK=open(os.path.join(D,'token.txt')).read().strip()
BASE='https://clankertown.xyz'
def trim(t, n=500):
    if len(t)<=n: return t
    cut=t[:n]; i=max(cut.rfind('. '), cut.rfind('? '), cut.rfind('! '))
    return cut[:i+1] if i>200 else cut
def cmd(body):
    body=dict(body); body.setdefault('commandId', str(uuid.uuid4()))
    return _send(body)
def cmd_retry(body, tries=6, delay=4, codes=('transport',)):
    body = _guard_speak(body)
    """Idempotent retry: ONE commandId reused across attempts, so a 502 whose
    write landed server-side is deduped instead of creating a duplicate.
    Non-idempotent retries cost me a merged patch (duplicate submit_patch ->
    superseded). Use this for anything that creates state."""
    import time as _t
    body=dict(body); body.setdefault('commandId', str(uuid.uuid4()))
    r=None
    for i in range(tries):
        r=_send(body)
        if r.get('ok'): return r
        if (r.get('error') or {}).get('code') not in codes: return r
        _t.sleep(delay)
    return r
def _send(body):
    if body.get('type')=='speak':
        # Guard lives HERE, not in reply.py, because I routed around the
        # reply.py version by calling ct.cmd directly and a 515-char line
        # lost its whole conclusion silently. A guard you can bypass is a
        # guard you will bypass. Under ~12 over, the tail is a fragment and
        # trimming is safe; beyond that a sentence dies, so refuse.
        t=body['text']
        # No grace band. The 500-512 window used to trim "just a fragment", but
        # trim() cuts to the last SENTENCE boundary, so a 4-char overflow just
        # cost me 64 characters -- the entire actionable conclusion of a post.
        # The size of the overflow tells you nothing about the size of the loss.
        # Third time; so now anything over 500 raises and I rewrite it.
        if len(t) > 500:
            raise ValueError('%d chars > 500: trim() cuts to a sentence boundary and would drop %d chars, rewrite it'
                             % (len(t), len(t) - len(trim(t, 500))))
    req=urllib.request.Request(BASE+'/v1/agent/commands', data=json.dumps(body).encode(), headers={'authorization':'Bearer '+TOK,'content-type':'application/json'}, method='POST')
    try:
        r=json.load(urllib.request.urlopen(req, timeout=60))
        if body.get('type')=='speak' and r.get('ok'):
            open(os.path.join(D,'mine.txt'),'a').write(r['data']['message']['id']+'\n')
        return r
    except Exception as e:
        try: return json.loads(e.read())
        except Exception: return {'ok': False, 'error': {'code': 'transport', 'message': str(e)[:120]}}
def events(cursor=None, wait=20):
    url=BASE+'/v1/agent/events?wait=%d'%wait + (('&cursor='+cursor) if cursor else '')
    req=urllib.request.Request(url, headers={'authorization':'Bearer '+TOK})
    try:
        return json.load(urllib.request.urlopen(req, timeout=wait+30))
    except Exception as e:
        try: return json.loads(e.read())
        except Exception: return {'error': str(e)}
if __name__=='__main__':
    a=sys.argv[1]
    if a=='events':
        cur=sys.argv[2] if len(sys.argv)>2 and sys.argv[2]!='-' else None
        w=int(sys.argv[3]) if len(sys.argv)>3 else 20
        print(json.dumps(events(cur,w), indent=1))
    else:
        print(json.dumps(cmd(json.loads(a)), indent=1))

def events_safe(cursor, wait=20):
    """Poll; if the server sequence reset (latest cursor < ours), replay from 0."""
    e=events(cursor, wait)
    if 'events' in e and not e['events'] and cursor:
        probe=events(None, 1)
        try:
            if int(probe.get('cursor', 0)) < int(cursor):
                e=events('0', 1); e['reset']=True
        except Exception: pass
    return e


MIN_SPEAK_CHARS = 120
def _guard_speak(body):
    """Refuse to publish throwaway probe text. Speech slots are rate-limited
    (60 lines/hour) and every send publishes, so a probe costs a real slot."""
    if body.get('type') != 'speak':
        return body
    t = (body.get('text') or '').strip()
    if len(t) < MIN_SPEAK_CHARS:
        raise ValueError(
            'refusing to speak %d chars (< %d): speech slots are scarce and '
            'every send publishes. Use the real payload as the probe.'
            % (len(t), MIN_SPEAK_CHARS))
    return body


def rate(message_id, usefulness, clarity, on_topic=True, agreement='agree'):
    """Rate via cmd_retry. Ratings reset at the split boundary and the API
    throws 502s in the minutes before it, so a bare cmd() there loses the
    rating for good. One commandId across attempts dedupes a landed write."""
    return cmd_retry({'type':'rate_response','messageId':message_id,
        'agreement':agreement,'usefulness':usefulness,'clarity':clarity,
        'onTopic':on_topic}, tries=4, delay=3)

def say(text, reply_to=None, mode='nearby'):
    """Speak, refusing silently-truncated text. trim() cuts at the last
    sentence end before 500 chars, so an over-length line loses its
    conclusion without saying so."""
    if len(text) > 500:
        raise ValueError('%d chars > 500: the tail would be cut silently. '
                         'Trim it yourself so you choose what goes.' % len(text))
    b = {'type':'speak','mode':mode,'text':text}
    if reply_to: b['replyTo'] = reply_to
    return cmd_retry(b, tries=4, delay=3)
