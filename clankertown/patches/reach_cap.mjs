// verify/reach_cap.mjs
// Checks every row of a split against the report's own reach cap, so the
// earshot ceiling can be read from the file rather than argued about.
// Usage: node verify/reach_cap.mjs <split>
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
const rules = report.rules || {};
const cap = Number.isFinite(rules.reachCap) ? rules.reachCap : 25;
const points = Number.isFinite(rules.reachPoints) ? rules.reachPoints : 0.01;
// The published fields carry six decimals, so compare at that precision:
// a tighter tolerance reports rounding as a violation.
const limit = cap * points + 1e-6;
let within = 0;
let over = 0;
for (const row of scores) {
  const reach = Number(row.reach) || 0;
  if (reach <= limit) within += 1;
  else over += 1;
}
process.stdout.write(
  `split ${n}: ${within} of ${scores.length} rows within reach cap ${cap}, ${over} over\n`
);
