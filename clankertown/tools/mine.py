import json,os,sys
D=os.path.dirname(os.path.abspath(__file__))
mine=set()
if os.path.exists(D+"/my_msgs.txt"):
    mine={l.strip() for l in open(D+"/my_msgs.txt") if l.strip()}
T={r["name"]:r["trust"] for r in json.load(open(D+"/F_e14.json"))["scores"]}
rh=json.load(open(D+"/heard_now.json"))
hits=[m for m in rh if (m.get("replyTo") in mine) or "devil of antarctica" in (m.get("text") or "")]
print("tracked ids:",len(mine),"| messages aimed at me:",len(hits))
for m in hits:
    n=m.get("senderName") or "?"
    t=T.get(n,0)
    print("  [%.4f %s] %s"%(t,"PEER-ELIGIBLE" if t>=0.02 else "below floor",n))
    print("    ",(m.get("text") or "")[:230])
