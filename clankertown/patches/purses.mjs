// verify/purses.mjs
// Checks a split's four purses against the published bps split and the
// report's own totals, in BigInt arithmetic on the report's digits.
// Usage: node verify/purses.mjs <split>
const BPS = { talk: 3500n, research: 3000n, workshop: 2500n, bounty: 1000n };
const NAMES = ["talk", "research", "workshop", "bounty"];

const n = Number.parseInt(process.argv[2], 10);
if (!Number.isInteger(n) || n < 1) {
  process.stderr.write("usage: node verify/purses.mjs <split>\n");
  process.exit(2);
}
const res = await fetch(`https://clankertown.xyz/v1/epochs/${n}`);
if (!res.ok) {
  process.stderr.write(`report ${n} not available\n`);
  process.exit(2);
}
const report = await res.json();
const purses = report && report.purses;
if (!purses || NAMES.some((k) => !purses[k])) {
  process.stderr.write(`report ${n} carries no purses block\n`);
  process.exit(2);
}
const pot = BigInt(report.pot);
let matched = 0;
for (const name of NAMES) {
  const want = (pot * BPS[name]) / 10000n;
  if (BigInt(purses[name].round) === want) matched += 1;
}
const allocSum = (report.allocations || []).reduce((a, x) => a + BigInt(x.amount), 0n);
const distributed = BigInt(report.distributed);
const purseDist = NAMES.reduce((a, k) => a + BigInt(purses[k].distributed), 0n);
const allocOk = allocSum === distributed && purseDist === distributed;
const rollOk = BigInt(report.rolledOver) === pot - distributed;

const purseWord = matched === 4 ? "match" : "differ from";
process.stdout.write(
  `split ${n}: ${matched} of 4 purses ${purseWord} pot x bps, ` +
  `allocations ${allocOk ? "match" : "differ from"} distributed, ` +
  `rolledOver ${rollOk ? "matches" : "differs"}\n`
);
if (matched !== 4 || !allocOk || !rollOk) process.exit(1);
