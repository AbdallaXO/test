// Recompute the stake line for one sealed split: trust vs min(held/1e6, 1).
// Usage: node verify/stakeline.mjs 42
const epoch = process.argv[2];
let rows = null;
for (let attempt = 0; attempt < 6 && rows === null; attempt++) {
  try {
    const res = await fetch(`https://clankertown.xyz/v1/epochs/${epoch}`);
    const body = await res.text();
    if (body) rows = JSON.parse(body).scores;
  } catch (err) {
    rows = null;
  }
  if (rows === null) await new Promise(r => setTimeout(r, 3000));
}
if (rows === null) throw new Error(`could not read split ${epoch}`);
const staked = rows.filter(r => r.walletVerified && Number(r.held) >= 100000);
const onLine = staked.filter(r => Math.abs(r.trust - Math.min(Number(r.held) / 1e6, 1)) <= 0.03);
const flow = rows.filter(r => Number(r.held) < 1000 && r.trust >= 0.05);
console.log(`split ${epoch}: ${onLine.length} of ${staked.length} staked wallets within 0.03 of held/1e6; ${flow.length} zero-holders above 0.05`);
