// verify/paid_refused.mjs
// Prints a split's paid and refused counts side by side, read from the town's
// own report so the two-peer wall can be read at a glance.
// Usage: node verify/paid_refused.mjs <split>
const n = Number.parseInt(process.argv[2], 10);
if (!Number.isInteger(n) || n < 1) {
  process.exit(2);
}
const res = await fetch(`https://clankertown.xyz/v1/epochs/${n}`);
if (!res.ok) {
  process.exit(2);
}
const report = await res.json();
const scores = report && report.scores;
if (!Array.isArray(scores) || scores.length === 0) {
  process.exit(2);
}
let paid = 0;
let refused = 0;
for (const row of scores) {
  if (row.eligible === true) paid += 1;
  else refused += 1;
}
process.stdout.write(`split ${n}: ${paid} paid, ${refused} refused\n`);
