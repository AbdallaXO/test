// The town's verifier for the w(2;3,t) ladders, with t taken from argv so one
// copy checks every rung. Byte-for-byte the same two tests as the ladder's
// _verify.mjs, which hardcodes ks = { 48: 3, 49: <t> } (char codes for '0','1').
import { readFileSync, existsSync } from 'node:fs';
const t = Number(process.argv[2]);
const file = process.argv[3] || 'colouring.txt';
const fail = (why) => { console.log('invalid: ' + why); process.exit(1); };
if (!existsSync(file)) fail(file + ' is missing');
const s = readFileSync(file, 'utf8').replace(/\s+/g, '');
if (!/^[01]+$/.test(s)) fail('must hold only the characters 0 and 1');
const n = s.length, ks = { 48: 3, 49: t };
for (let a = 0; a < n; a++) {
  const c = s.charCodeAt(a), k = ks[c];
  for (let d = 1; a + (k - 1) * d < n; d++) {
    let j = 1;
    while (j < k && s.charCodeAt(a + j * d) === c) j++;
    if (j === k) fail('monochromatic ' + k + '-term progression in colour ' + (c - 48) + ' starting at position ' + (a + 1) + ' with step ' + d);
  }
}
console.log('record=' + n);
