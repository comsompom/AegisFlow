const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with account:", deployer.address);
  console.log("Account balance:", (await hre.ethers.provider.getBalance(deployer.address)).toString());

  // 1. Deploy ComplianceRegistry
  const ComplianceRegistry = await hre.ethers.getContractFactory("ComplianceRegistry");
  const registry = await ComplianceRegistry.deploy(
    deployer.address,   // complianceOfficer
    deployer.address,   // aiAgent (same for MVP)
    1000000n * 10n ** 18n,  // maxPerTx (1M units)
    10000000n * 10n ** 18n  // maxDailyVolume (10M units)
  );
  await registry.waitForDeployment();
  const registryAddress = await registry.getAddress();
  console.log("ComplianceRegistry deployed to:", registryAddress);

  // 2. Deploy AegisFlowVault
  const AegisFlowVault = await hre.ethers.getContractFactory("AegisFlowVault");
  const vault = await AegisFlowVault.deploy(registryAddress, deployer.address);
  await vault.waitForDeployment();
  const vaultAddress = await vault.getAddress();
  console.log("AegisFlowVault deployed to:", vaultAddress);

  // 3. Set vault address in registry so it can call recordVolume
  await registry.setVault(vaultAddress);
  console.log("Registry vault set to:", vaultAddress);

  const output = {
    network: hre.network.name,
    chainId: (await hre.ethers.provider.getNetwork()).chainId.toString(),
    deployer: deployer.address,
    contracts: {
      ComplianceRegistry: registryAddress,
      AegisFlowVault: vaultAddress,
    },
  };

  const outPath = path.join(__dirname, "..", "deployed.json");
  fs.writeFileSync(outPath, JSON.stringify(output, null, 2));
  console.log("Addresses written to", outPath);
}

main()
  .then(() => process.exit(0))
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
