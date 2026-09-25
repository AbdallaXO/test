#!/usr/bin/env node
// verify/cumulative.mjs -- tie a split's allocations and leaves back to its own published totals.
//
// The report states two totals and also states the parts they are made of: distributed against
// allocations[].amount, and totalAllocated against leaves[].cumulative. Nothing recomputed them,
// so a total could drift from its own parts unseen. Both sums are taken as BigInt on the wei
// strings -- an 18-decimal figure does not survive IEEE double, and 7429831986924594731 is past
// 2^53 on its own.
//
// A leaf is one wallet's running lifetime total, so the same wallet twice would double-count it in
// totalAllocated and give that wallet two proofs against the root. Hence the duplicate check.
//
// usage: node verify/cumulative.mjs <split>
const BASE = "https://clankertown.xyz";

function wei(v) {
  if (v === null || v === undefined) return null;
  const s = String(v).trim();
  if (!/^\d+$/.test(s)) return null;
  return BigInt(s);
}

function key(w) {
  return String(w === null || w === undefined ? "" : w).trim().toLowerCase();
}

const n = process.argv[2];
if (!n) {
  console.error("usage: node verify/cumulative.mjs <split>");
  process.exit(2);
}

const res = await fetch(`${BASE}/v1/epochs/${n}`);
if (!res.ok) {
  console.error(`split ${n}: report unavailable (HTTP ${res.status})`);
  process.exit(2);
}
const report = await res.json();
const allocations = report && report.allocations;
const leaves = report && report.leaves;
if (!Array.isArray(allocations) || allocations.length === 0) {
  console.error(`split ${n}: report carries no allocations`);
  process.exit(2);
}
if (!Array.isArray(leaves) || leaves.length === 0) {
  console.error(`split ${n}: report carries no leaves`);
  process.exit(2);
}

const problems = [];

let allocSum = 0n;
for (const a of allocations) {
  const amount = wei(a && a.amount);
  if (amount === null) {
    problems.push(`allocation for ${key(a && a.wallet) || "(no wallet)"}: amount ${a && a.amount} is not a wei figure`);
    continue;
  }
  allocSum += amount;
}

let leafSum = 0n;
const seen = new Set();
let firstRepeat = null;
for (const l of leaves) {
  const cumulative = wei(l && l.cumulative);
  if (cumulative === null) {
    problems.push(`leaf for ${key(l && l.wallet) || "(no wallet)"}: cumulative ${l && l.cumulative} is not a wei figure`);
  } else {
    leafSum += cumulative;
  }
  const k = key(l && l.wallet);
  if (seen.has(k)) {
    if (firstRepeat === null) firstRepeat = k;
  } else {
    seen.add(k);
  }
}
if (firstRepeat !== null) problems.push(`wallet ${firstRepeat} is listed twice in the leaves`);

// Clause 4: an allocation with no leaf has nothing to prove itself against.
let firstMissing = null;
for (const a of allocations) {
  const k = key(a && a.wallet);
  if (!seen.has(k)) { firstMissing = k; break; }
}
if (firstMissing !== null) problems.push(`allocation for wallet ${firstMissing} has no leaf`);

const distributed = wei(report && report.distributed);
const totalAllocated = wei(report && report.totalAllocated);
if (distributed === null || allocSum !== distributed) {
  problems.push(`allocations sum to ${allocSum} wei but the report says distributed ${report && report.distributed}`);
}
if (totalAllocated === null || leafSum !== totalAllocated) {
  problems.push(`leaves sum to ${leafSum} wei but the report says totalAllocated ${report && report.totalAllocated}`);
}

console.log(`split ${n}: allocations sum to ${allocSum} wei, distributed ${report.distributed}; leaves sum to ${leafSum} wei, totalAllocated ${report.totalAllocated}; ${leaves.length} leaves, ${seen.size} wallets`);
for (const line of problems) console.log(line);
process.exit(problems.length ? 1 : 0);
