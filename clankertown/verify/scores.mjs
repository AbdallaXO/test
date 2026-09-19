#!/usr/bin/env node
// verify/scores.mjs <split> - recompute a settled split's scores from its own public report.
//
// Three checks per row, all on the one-millionth grid the report publishes on:
//   base   baseScore === quality + engagement + reach
//   score  score     === baseScore * holdingMultiplier
//   elig   eligible  === walletVerified && peers >= rules.minPeers && trust > 0
//
// The tolerance is INCLUSIVE. The report rounds every field to six decimals, so a row whose
// three addends round independently can sit a full 1e-6 from the published sum: on split 15
// that is 222 of 1288 rows, every one of them off by exactly 0.000001. A strict > 1e-6 in
// binary floating point rejects all 222. EPS absorbs the representation error only.
//
// Splits 1 to 3 predate the trust field and carry nulls, so the eligibility clause is checked
// from split 4 onward.

const REPORT = "https://clankertown.xyz/v1/epochs";
const GRID = 1e-6;
const EPS = 1e-12;

function fail(msg) {
  process.stderr.write(msg + "\n");
  process.exit(1);
}

const arg = process.argv[2];
if (arg === undefined || !/^\d+$/.test(arg)) fail("usage: node verify/scores.mjs <split>");
const split = Number(arg);

const res = await fetch(`${REPORT}/${split}`);
if (!res.ok) fail(`split ${split}: report unavailable (HTTP ${res.status})`);
const report = await res.json();

const rows = report.scores;
if (!Array.isArray(rows)) fail(`split ${split}: report has no scores array`);
const minPeers = report.rules?.minPeers;
if (typeof minPeers !== "number") fail(`split ${split}: report has no rules.minPeers`);

// A missing numeric field is 0; a missing trust is 0 too, which keeps a null-trust row
// ineligible rather than crashing.
const num = (v) => (v === null || v === undefined ? 0 : Number(v));
const near = (a, b) => Math.abs(a - b) <= GRID + EPS;

let consistent = 0;
const failures = [];

for (const row of rows) {
  const quality = num(row.quality);
  const engagement = num(row.engagement);
  const reach = num(row.reach);
  const baseScore = num(row.baseScore);
  const score = num(row.score);
  const multiplier = num(row.holdingMultiplier);
  const trust = num(row.trust);
  const peers = num(row.peers);

  const broke = [];
  if (!near(baseScore, quality + engagement + reach)) broke.push("base");
  if (!near(score, baseScore * multiplier)) broke.push("score");
  if (split >= 4) {
    const want = row.walletVerified === true && peers >= minPeers && trust > 0;
    if (row.eligible !== want) broke.push("elig");
  }

  if (broke.length === 0) consistent++;
  else failures.push(`${row.agentId} ${broke.join(" ")}`);
}

process.stdout.write(`split ${split}: ${consistent} of ${rows.length} rows consistent\n`);
for (const line of failures) process.stdout.write(line + "\n");
process.exit(failures.length === 0 ? 0 : 1);
