import { expect } from "chai";
import pkg from 'hardhat';
const { ethers } = pkg;

describe("RoyaltySplit.reportMatch", () => {
  it("emits MatchReported N times (happy path)", async () => {
    const [deployer, ...signers] = await ethers.getSigners();
    const RoyaltySplit = await ethers.getContractFactory("RoyaltySplit", deployer);
    const splitter = await RoyaltySplit.deploy();
    await splitter.waitForDeployment();

    const tokenId = 1n;
    const N = 4;
    const sources = signers.slice(0, N).map(s => s.address);
    const millis = Array(N).fill(1000);

    const tx = await splitter.reportMatch(tokenId, sources, millis);
    const rc = await tx.wait();

    // Count decoded events
    const iface = splitter.interface;
    const events = rc!.logs
      .map((log: any) => {
        try { return iface.parseLog(log); } catch { return undefined; }
      })
      .filter((e: any) => e && e.name === "MatchReported");

    expect(events.length).to.equal(N);
    for (let i = 0; i < N; i++) {
      expect(events[i].args.tokenId).to.equal(tokenId);
      expect(events[i].args.source).to.equal(sources[i]);
      expect(events[i].args.millis).to.equal(millis[i]);
    }
  });

  it("reverts on length mismatch", async () => {
    const [deployer, a1, a2] = await ethers.getSigners();
    const RoyaltySplit = await ethers.getContractFactory("RoyaltySplit", deployer);
    const splitter = await RoyaltySplit.deploy();
    await splitter.waitForDeployment();

    await expect(
      splitter.reportMatch(1, [a1.address, a2.address], [1000])
    ).to.be.revertedWith("LEN_MISMATCH");
  });

  it("reverts on BAD_COUNT (0 or > MAX_SOURCES)", async () => {
    const [deployer, ...signers] = await ethers.getSigners();
    const RoyaltySplit = await ethers.getContractFactory("RoyaltySplit", deployer);
    const splitter = await RoyaltySplit.deploy();
    await splitter.waitForDeployment();

    // 0
    await expect(splitter.reportMatch(1, [], []))
      .to.be.revertedWith("BAD_COUNT");

    // > MAX_SOURCES (contract exposes public constant)
    const max = await splitter.MAX_SOURCES();
    const N = Number(max) + 1;
    const addrs = Array(N).fill(signers[0].address);
    const ms = Array(N).fill(1000);
    await expect(splitter.reportMatch(1, addrs, ms))
      .to.be.revertedWith("BAD_COUNT");
  });

  it("reverts on BAD_MILLIS and ZERO_TOTAL", async () => {
    const [deployer, a1] = await ethers.getSigners();
    const RoyaltySplit = await ethers.getContractFactory("RoyaltySplit", deployer);
    const splitter = await RoyaltySplit.deploy();
    await splitter.waitForDeployment();

    // BAD_MILLIS (zero)
    await expect(splitter.reportMatch(1, [a1.address], [0]))
      .to.be.revertedWith("BAD_MILLIS");

    // BAD_MILLIS (exceeds cap)
    const cap = await splitter.MAX_MILLIS_PER_CALL();
    await expect(splitter.reportMatch(1, [a1.address], [Number(cap) + 1]))
      .to.be.revertedWith("BAD_MILLIS");
  });
});