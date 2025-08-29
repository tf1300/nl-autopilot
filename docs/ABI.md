# ABI Documentation

This document describes the Application Binary Interface (ABI) for the smart contract functions and events that will be called from the oracle.

## Functions

### `reportMatch`

Reports a match detected by the watermark decoder.

```solidity
function reportMatch(
  uint256 tokenId,
  address[] calldata sources,
  uint32[]  calldata millis
) external;
```

**Parameters:**

*   `tokenId`: A unique identifier for the content that was matched.
*   `sources`: An array of addresses representing the source(s) of the detected content.
*   `millis`: An array of `uint32` values representing the timestamp in milliseconds for each detected source.

## Events

### `MatchReported`

Emitted when a match is successfully reported.

```solidity
event MatchReported(uint256 indexed tokenId, address indexed source, uint32 millis);
```

**Parameters:**

*   `tokenId`: The unique identifier for the content that was matched.
*   `source`: The address representing the source of the detected content.
*   `millis`: The timestamp in milliseconds for the detected source.

## Hardhat Test Example

```javascript
// Example Hardhat test (for demonstration purposes)
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("OracleIntegration", function () {
  it("Should emit MatchReported event with correct data", async function () {
    const OracleContract = await ethers.getContractFactory("OracleContract");
    const oracle = await OracleContract.deploy();
    await oracle.deployed();

    const tokenId = 123;
    const sources = ["0xAbc1234567890123456789012345678901234567", "0xDef1234567890123456789012345678901234567"];
    const millis = [1000, 5000];

    await expect(oracle.reportMatch(tokenId, sources, millis))
      .to.emit(oracle, "MatchReported")
      .withArgs(tokenId, sources[0], millis[0]);

    // You might need to iterate or adjust for multiple events if reportMatch emits one per source
    // For example, if it emits one event per source in the array:
    await expect(oracle.reportMatch(tokenId, sources, millis))
      .to.emit(oracle, "MatchReported")
      .withArgs(tokenId, sources[1], millis[1]);

    // Assert array length equality and non-zero totals (conceptual, depends on contract logic)
    // These assertions would typically be within the contract's internal logic or a separate test
    // expect(sources.length).to.be.greaterThan(0);
    // expect(millis.length).to.be.greaterThan(0);
    // expect(sources.length).to.equal(millis.length);
  });
});
```
