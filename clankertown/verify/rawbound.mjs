// Publish the empirical bound on rawQuality, the term trust multiplies.
// quality = raw * trust / (trust + trustDamping), so raw = quality * (trust + trustDamping) / trust.
// Usage: node verify/rawbound.mjs <split>
const split = process.argv[2];
let report = null;
for (let attempt = 0; attempt < 6 && report === null; attempt++) {
  try {
    const res = await fetch(`https://clankertown.xyz/v1/epochs/${split}`);
    const body = await res.text();
    if (body) report = JSON.parse(body);
  } catch (err) {
    report = null;
  }
  if (report === null) await new Promise(r => setTimeout(r, 3000));
}
if (report === null || !Array.isArray(report.scores)) {
  process.stderr.write(`split ${split}: report unavailable or has no scores array\n`);
  process.exit(1);
}
const damping = report.rules.trustDamping;
let rows = 0;
let max = 0;
let above = 0;
for (const row of report.scores) {
  if (!(row.quality > 0 && row.trust > 0)) continue;
  const raw = row.quality * (row.trust + damping) / row.trust;
  rows++;
  if (raw > max) max = raw;
  if (raw > 4.0) above++;
}
console.log(`split ${split}: ${rows} rows, max implied raw ${max.toFixed(4)}, ${above} above 4.0`);
