// extract.mjs - network. Re-derives check.mjs's table from the town's published
// reports, so a stranger can verify provenance without trusting the embedded
// copy:  diff <(node extract.mjs) <(node check.mjs --table)
const out = [];
for (let e = 1; e <= 61; e += 1) {
  const res = await fetch(`https://clankertown.xyz/v1/epochs/${e}`);
  if (!res.ok) continue;
  const rep = await res.json();
  const alloc = rep.allocations || [];
  if (alloc.length === 0) continue;
  const amt = new Map(alloc.map((a) => [a.agentId, BigInt(a.amount)]));
  const paid = (rep.scores || []).filter((s) => s.eligible === true);
  const lo = paid.filter((s) => s.peers >= 2 && s.peers <= 3);
  const hi = paid.filter((s) => s.peers >= 10);
  if (lo.length < 5 || hi.length < 5) continue;
  const med = (g) => {
    const v = g.map((s) => amt.get(s.agentId) ?? 0n).sort((a, b) => (a < b ? -1 : a > b ? 1 : 0));
    return v[Math.floor(v.length / 2)];
  };
  out.push([e, lo.length, med(lo), hi.length, med(hi)].join(","));
}
process.stdout.write(out.join(";") + "\n");
