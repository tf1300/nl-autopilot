require("@nomicfoundation/hardhat-ethers");
require("@nomicfoundation/hardhat-chai-matchers");
require("@nomicfoundation/hardhat-mocha");

const config = {
  solidity: "0.8.20",
  networks: {
    hardhat: {
      // Configuration for the Hardhat Network
      chainId: 31337,
      mining: {
        auto: true,
        interval: 0
      },
      type: "edr-simulated",
      allowBlocksWithSameTimestamp: true
    },
  },
  paths: {
    tests: "./test",
    sources: "./contracts",
    cache: "./cache",
    artifacts: "./artifacts",
  },
  mocha: {
    timeout: 40000
  }
};

module.exports = config;