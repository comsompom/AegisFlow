const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("ComplianceRegistry", function () {
  let registry, owner, compliance, aiAgent, user1, user2;

  beforeEach(async function () {
    [owner, compliance, aiAgent, user1, user2] = await ethers.getSigners();
    const ComplianceRegistry = await ethers.getContractFactory("ComplianceRegistry");
    registry = await ComplianceRegistry.deploy(
      compliance.address,
      aiAgent.address,
      ethers.parseEther("1000"),
      ethers.parseEther("10000")
    );
  });

  it("should set owner and roles", async function () {
    expect(await registry.owner()).to.equal(owner.address);
    expect(await registry.complianceOfficer()).to.equal(compliance.address);
    expect(await registry.aiAgent()).to.equal(aiAgent.address);
  });

  it("should allow compliance officer to whitelist", async function () {
    await registry.connect(compliance).addToWhitelist(user1.address);
    expect(await registry.isWhitelisted(user1.address)).to.be.true;
  });

  it("should allow compliance officer to blacklist", async function () {
    await registry.connect(compliance).addToWhitelist(user1.address);
    await registry.connect(compliance).addToBlacklist(user1.address);
    expect(await registry.isWhitelisted(user1.address)).to.be.false;
    expect(await registry.isBlacklisted(user1.address)).to.be.true;
  });

  it("should allow owner to set limits", async function () {
    await registry.setLimits(ethers.parseEther("500"), ethers.parseEther("5000"));
    expect(await registry.maxPerTx()).to.equal(ethers.parseEther("500"));
    expect(await registry.maxDailyVolume()).to.equal(ethers.parseEther("5000"));
  });

  it("should reject non-whitelisted for canReceive", async function () {
    expect(await registry.canReceive(user1.address, ethers.parseEther("100"))).to.be.false;
  });

  it("should accept whitelisted for canReceive within limits", async function () {
    await registry.connect(compliance).addToWhitelist(user1.address);
    expect(await registry.canReceive(user1.address, ethers.parseEther("100"))).to.be.true;
  });
});
