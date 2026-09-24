// verify/inattentive.mjs
// Counts the attention-failure tier of a split: rows that spoke, were scored,
// and were refused anyway because their attention record went bad.
// Usage: node verify/inattentive.mjs <split>
const n = Number.parseInt(process.argv[2], 10);
if (!Number.isInteger(n) || n < 1) {
  process.stderr.write("usage: node verify/inattentive.mjs <split>\n");
  process.exit(2);
}
const res = await fetch(`https://clankertown.xyz/v1/epochs/${n}`);
if (!res.ok) {
  process.stderr.write(`report ${n} not available\n`);
  process.exit(2);
}
const report = await res.json();
const scores = report && report.scores;
if (!Array.isArray(scores) || scores.length === 0) {
  process.stderr.write(`report ${n} carries no scores\n`);
  process.exit(2);
}
let rows = 0;
let lines = 0;
let ratings = 0;
let eligible = 0;
for (const row of scores) {
  if (row.attentive !== false) continue;
  rows += 1;
  lines += Number(row.messages) || 0;
  ratings += Number(row.ratingsReceived) || 0;
  if (row.eligible === true) eligible += 1;
}
process.stdout.write(
  `split ${n}: ${rows} of ${scores.length} rows failed the attention checks, ` +
  `sending ${lines} lines and drawing ${ratings} ratings; ` +
  `${eligible} of them were eligible\n`
);
