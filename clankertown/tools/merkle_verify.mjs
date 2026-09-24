import { keccak256, AbiCoder } from "ethers";
const rep = JSON.parse(await (await fetch("https://clankertown.xyz/v1/epochs/61")).text());
const coder = AbiCoder.defaultAbiCoder();
const leaves = rep.leaves.map((l) =>
  keccak256(keccak256(coder.encode(["address","address","uint256"], [l.wallet, rep.asset, l.cumulative])))
);
let level = [...leaves].sort();
while (level.length > 1) {
  const next = [];
  for (let i = 0; i < level.length; i += 2) {
    if (i + 1 === level.length) { next.push(level[i]); continue; }
    const [x, y] = [level[i], level[i+1]].sort();
    next.push(keccak256("0x" + x.slice(2) + y.slice(2)));
  }
  level = next;
}
console.log("leaves", rep.leaves.length, "allocations", rep.allocations.length);
console.log("computed", level[0]);
console.log("reported", rep.root);
console.log("match", level[0] === rep.root);
const mine = rep.leaves.find((l) => l.wallet.toLowerCase() === "0x8ac3e5966b7c60951cc7abfa1a16eba1c7be632c");
console.log("our leaf cumulative", mine ? mine.cumulative : "absent");
