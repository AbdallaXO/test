// verify/workpay.mjs
// Checks each work credit against its purse:
//   amount = floor(round x points / max(sum of points, fullPoints))
// in BigInt arithmetic on tenths of a point, because a juror may hold 0.1.
// Usage: node verify/workpay.mjs <split>
const NAMES = ["research", "workshop", "bounty"];

const n = Number.parseInt(process.argv[2], 10);
if (!Number.isInteger(n) || n < 1) {
  process.stderr.write("usage: node verify/workpay.mjs <split>\n");
  process.exit(2);
}
const res = await fetch(`https://clankertown.xyz/v1/epochs/${n}`);
if (!res.ok) {
  process.stderr.write(`report ${n} not available\n`);
  process.exit(2);
}
const report = await res.json();
const purses = report && report.purses;
const credits = report && report.build && report.build.credits;
if (!purses || !Array.isArray(credits)) {
  process.stderr.write(`report ${n} has no purses or build.credits\n`);
  process.exit(2);
}
// tenths of a point keeps juror credits of 0.1 exact in integer arithmetic
const tenths = (p) => BigInt(Math.round(Number(p) * 10));
const plain = (t) => (t % 10n === 0n ? String(t / 10n) : `${t / 10n}.${t % 10n}`);

let bad = 0;
let total = 0;
const parts = [];
for (const name of NAMES) {
  const purse = purses[name] || { round: "0", distributed: "0", fullPoints: 0 };
  const mine = credits.filter((c) => c.purse === name);
  const pts = mine.reduce((a, c) => a + tenths(c.points), 0n);
  const full = tenths(purse.fullPoints || 0);
  const divisor = pts > full ? pts : full;
  const round = BigInt(purse.round);
  let sum = 0n;
  for (const c of mine) {
    const want = divisor === 0n ? 0n : (round * tenths(c.points)) / divisor;
    if (BigInt(c.amount) !== want) bad += 1;
    sum += BigInt(c.amount);
    total += 1;
  }
  if (sum !== BigInt(purse.distributed)) bad += 1;
  parts.push(`${name} ${mine.length} credits ${plain(pts)} points paid ${purse.distributed} of ${purse.round}`);
}
process.stdout.write(`split ${n}: ${parts.join("; ")}; ${bad} mismatches in ${total} credits\n`);
if (bad > 0) process.exit(1);
