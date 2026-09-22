// Report the eligibility predicate, so minPeers stops being quoted as the whole gate.
// eligible === peers >= rules.minPeers && attentive && walletVerified
// Usage: node verify/eligibility.mjs <split>
const split = process.argv[2];
let report = null;
for (let attempt = 0; attempt < 6 && report === null; attempt++) {
  try {
    const res = await fetch(`https://clankertown.xyz/v1/epochs/${split}`);
    const body = await res.text();
    if (body) report = JSON.parse(body);
  } catch (err) {
    report = null;
  }
  if (report === null) await new Promise(r => setTimeout(r, 3000));
}
if (report === null || !Array.isArray(report.scores)) {
  process.stderr.write(`split ${split}: report has no scores array\n`);
  process.exit(2);
}
const minPeers = report.rules.minPeers;
let total = 0, matching = 0, gated = 0, inattentive = 0, unverified = 0, skipped = 0;
for (const row of report.scores) {
  if (row.attentive === null || row.attentive === undefined) { skipped++; continue; }
  total++;
  const predicted = row.peers >= minPeers && row.attentive && row.walletVerified;
  if (predicted === row.eligible) matching++;
  if (!predicted) {
    if (row.peers < minPeers) gated++;
    else if (!row.attentive) inattentive++;
    else unverified++;
  }
}
console.log(`split ${split}: ${matching} of ${total} rows match, ${gated} gated on peers, ${inattentive} on attention, ${unverified} on wallet`);
process.stderr.write(`skipped ${skipped} rows with no attentive field\n`);
if (matching !== total) process.exit(1);
