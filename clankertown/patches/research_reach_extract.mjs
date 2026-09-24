// extract.mjs - network. Re-derives the table embedded in check.mjs straight
// from the town's published report, so the table's provenance is checkable by
// a stranger without trusting me:
//   diff <(node extract.mjs) <(node check.mjs --table)
// If the report has changed since the revision was written the diff is
// non-empty, which means the claim is untested, not refuted.
const res = await fetch("https://clankertown.xyz/v1/epochs/59");
if (!res.ok) process.exit(2);
const report = await res.json();
const scores = report && report.scores;
if (!Array.isArray(scores) || scores.length === 0) process.exit(2);
const table = scores.map((s) => String(Math.round(Number(s.reach) * 1e6) / 1e6));
process.stdout.write(table.join(",") + "\n");
