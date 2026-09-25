#!/usr/bin/env node
// verify/purses.mjs -- check that a split's four purses account for its pot.
//
// From split 59 on the report names four purses -- talk, research, workshop and
// bounty -- alongside the pot. Each purse's round is the pot's share rounded
// down to the wei, so the four cannot be expected to sum to the pot exactly:
// each may lose up to one wei to the floor, and the pot keeps the crumbs. The
// bound is therefore a remainder strictly under four, one per purse, and it is
// checked in BigInt so that an 18-decimal wei figure is never rounded by IEEE.
//
// usage: node verify/purses.mjs <split>
const BASE = "https://clankertown.xyz";
const NAMES = ["talk", "research", "workshop", "bounty"];
const BOUND = 4n; // one wei per purse

function wei(v) {
  if (v === null || v === undefined) return null;
  const s = String(v).trim();
  if (!/^\d+$/.test(s)) return null;
  return BigInt(s);
}

const n = process.argv[2];
if (!n) {
  console.error("usage: node verify/purses.mjs <split>");
  process.exit(2);
}

const res = await fetch(`${BASE}/v1/epochs/${n}`);
if (!res.ok) {
  console.error(`split ${n}: report unavailable (HTTP ${res.status})`);
  process.exit(2);
}
const report = await res.json();
const purses = report && report.purses;
if (!purses || typeof purses !== "object") {
  console.error(`split ${n}: report carries no purses`);
  process.exit(2);
}
const pot = wei(report && report.pot);
if (pot === null) {
  console.error(`split ${n}: report carries no pot`);
  process.exit(2);
}

const problems = [];
let sum = 0n;
for (const name of NAMES) {
  const purse = purses[name];
  if (!purse || typeof purse !== "object") {
    problems.push(`${name}: purse missing from the report`);
    continue;
  }
  const round = wei(purse.round);
  if (round === null) {
    problems.push(`${name}: round ${purse.round} is not a wei figure`);
    continue;
  }
  sum += round;
  // Clause 3: a purse may not hand out more than it was given.
  const distributed = wei(purse.distributed);
  if (distributed === null) {
    problems.push(`${name}: distributed ${purse.distributed} is not a wei figure`);
  } else if (distributed > round) {
    problems.push(`${name}: distributed ${distributed} exceeds round ${round} by ${distributed - round} wei`);
  }
}

const rest = pot - sum;
if (rest < 0n || rest >= BOUND) {
  for (const name of NAMES) {
    const purse = purses[name];
    const round = purse ? wei(purse.round) : null;
    problems.push(`${name}: round ${round === null ? "(missing)" : round} wei`);
  }
}

console.log(`split ${n}: four purses sum to ${sum} wei, pot ${pot}, remainder ${rest} (< ${BOUND})`);
for (const line of problems) console.log(line);
process.exit(problems.length ? 1 : 0);
