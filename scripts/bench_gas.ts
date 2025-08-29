import fs from "fs";
import path, { dirname } from "path";
import { fileURLToPath } from 'url';
import pkg from 'hardhat';
const { ethers } = pkg;

async function main() {
  const [deployer, ...signers] = await ethers.getSigners();
  const RoyaltySplit = await ethers.getContractFactory("RoyaltySplit", deployer);
  const splitter = await RoyaltySplit.deploy();
  await splitter.waitForDeployment();

  const Ns = [1, 2, 4, 8, 16];
  const rows: string[] = ["N,gasUsed,gasPerEvent"];

  for (const N of Ns) {
    // Ensure we have at least N addresses (reuse if needed)
    const sources = Array(N).fill(0).map((_, i) => signers[i % signers.length].address);
    const millis = Array(N).fill(1000);

    const tx = await splitter.reportMatch(1, sources, millis);
    const rc = await tx.wait();
    const gasUsed = Number(rc!.gasUsed); // ok for these sizes
    const gasPerEvent = Math.floor(gasUsed / N);
    rows.push([N, gasUsed, gasPerEvent].join(","));
    console.log(`N=${N} gas=${gasUsed} (~${gasPerEvent}/event)`);
  }

  const __filename = fileURLToPath(import.meta.url);
  const __dirname = dirname(__filename);
  const out = path.join(__dirname, "..", "contracts", "gas.csv");
  fs.writeFileSync(out, rows.join("\n") + "\n", "utf8");
  console.log(`Wrote ${out}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});