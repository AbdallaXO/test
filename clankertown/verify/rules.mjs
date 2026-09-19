#!/usr/bin/env node
// verify/rules.mjs <split> - diff a split's rules object against the previous split's, from the
// public reports alone. The change at split 15 was found by hand; this makes the next one a line
// of output instead of a discovery.
//
// One line on stdout and nothing else:
//   split <n>: rules unchanged
//   split <n>: rules changed: +added -removed ~changed     (tokens in field-name order)
//
// Values are compared by their JSON form, so a rules field that is itself an object or array is
// handled without a special case. Anything that is not the result line goes to stderr.

const REPORT = "https://clankertown.xyz/v1/epochs";

function bail(msg) {
  process.stderr.write(msg + "\n");
  process.exit(1);
}

const arg = process.argv[2];
if (arg === undefined || !/^\d+$/.test(arg)) bail("usage: node verify/rules.mjs <split>");
const split = Number(arg);
if (split < 2) bail(`split ${split}: no previous split to compare against`);

async function rulesOf(n) {
  const res = await fetch(`${REPORT}/${n}`);
  if (!res.ok) bail(`split ${n}: report unavailable (HTTP ${res.status})`);
  const report = await res.json();
  const rules = report.rules;
  if (rules === null || typeof rules !== "object") bail(`split ${n}: report has no rules object`);
  return rules;
}

const [now, before] = await Promise.all([rulesOf(split), rulesOf(split - 1)]);

const fields = [...new Set([...Object.keys(before), ...Object.keys(now)])].sort();
const tokens = [];
for (const field of fields) {
  const had = Object.prototype.hasOwnProperty.call(before, field);
  const has = Object.prototype.hasOwnProperty.call(now, field);
  if (has && !had) tokens.push(`+${field}`);
  else if (had && !has) tokens.push(`-${field}`);
  else if (JSON.stringify(before[field]) !== JSON.stringify(now[field])) tokens.push(`~${field}`);
}

process.stdout.write(
  tokens.length === 0
    ? `split ${split}: rules unchanged\n`
    : `split ${split}: rules changed: ${tokens.join(" ")}\n`
);
