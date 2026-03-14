const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("AegisFlowVault", function () {
  let registry, vault, owner, treasury, user1, user2;

  beforeEach(async function () {
    [owner, treasury, user1, user2] = await ethers.getSigners();
    const ComplianceRegistry = await ethers.getContractFactory("ComplianceRegistry");
    registry = await ComplianceRegistry.deploy(
      owner.address,
      owner.address,
      ethers.parseEther("1000"),
      ethers.parseEther("10000")
    );
    const AegisFlowVault = await ethers.getContractFactory("AegisFlowVault");
    vault = await AegisFlowVault.deploy(await registry.getAddress(), treasury.address);
    await registry.setVault(await vault.getAddress());
    await registry.addToWhitelist(user1.address);
  });

  it("should deposit and mint to user", async function () {
    await vault.connect(treasury).deposit(user1.address, ethers.parseEther("100"));
    expect(await vault.balanceOf(user1.address)).to.equal(ethers.parseEther("100"));
  });

  it("should transfer only to whitelisted", async function () {
    await vault.connect(treasury).deposit(user1.address, ethers.parseEther("100"));
    await registry.addToWhitelist(user2.address);
    await vault.connect(user1).transfer(user2.address, ethers.parseEther("50"));
    expect(await vault.balanceOf(user2.address)).to.equal(ethers.parseEther("50"));
  });

  it("should revert transfer to non-whitelisted", async function () {
    await vault.connect(treasury).deposit(user1.address, ethers.parseEther("100"));
    await expect(
      vault.connect(user1).transfer(user2.address, ethers.parseEther("50"))
    ).to.be.revertedWith("AegisFlowVault: recipient not whitelisted");
  });

  it("should withdraw to whitelisted via treasury", async function () {
    await vault.connect(treasury).deposit(treasury.address, ethers.parseEther("200"));
    await vault.connect(treasury).withdrawTo(treasury.address, user1.address, ethers.parseEther("100"));
    expect(await vault.balanceOf(user1.address)).to.equal(ethers.parseEther("100"));
  });
});
