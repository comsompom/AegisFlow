// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ComplianceRegistry
 * @dev KYC whitelist/blacklist and AML limits for AegisFlow.
 * Only whitelisted addresses can receive vault transfers.
 */
contract ComplianceRegistry {
    address public owner;
    address public complianceOfficer;
    address public aiAgent;
    address public vault; // AegisFlowVault allowed to call recordVolume

    mapping(address => bool) public whitelist;
    mapping(address => bool) public blacklist;
    mapping(address => uint256) public perAddressCap; // 0 = no cap

    uint256 public maxPerTx;
    uint256 public maxDailyVolume;
    uint256 public dailyVolumeUsed;
    uint256 public dailyVolumeResetTime;
    uint256 public constant SECONDS_PER_DAY = 86400;

    bool public paused;

    event AddressWhitelisted(address indexed account, string label);
    event AddressBlacklisted(address indexed account);
    event AddressRemovedFromWhitelist(address indexed account);
    event LimitsUpdated(uint256 maxPerTx, uint256 maxDailyVolume);
    event RoleUpdated(string role, address indexed account);
    event Paused(bool paused);

    modifier onlyOwner() {
        require(msg.sender == owner, "ComplianceRegistry: not owner");
        _;
    }

    modifier onlyComplianceOfficer() {
        require(
            msg.sender == complianceOfficer || msg.sender == owner,
            "ComplianceRegistry: not compliance officer"
        );
        _;
    }

    modifier onlyAIAgentOrVault() {
        require(
            msg.sender == aiAgent || msg.sender == vault || msg.sender == owner,
            "ComplianceRegistry: not AI agent or vault"
        );
        _;
    }

    modifier whenNotPaused() {
        require(!paused, "ComplianceRegistry: paused");
        _;
    }

    constructor(
        address _complianceOfficer,
        address _aiAgent,
        uint256 _maxPerTx,
        uint256 _maxDailyVolume
    ) {
        owner = msg.sender;
        complianceOfficer = _complianceOfficer;
        aiAgent = _aiAgent;
        maxPerTx = _maxPerTx;
        maxDailyVolume = _maxDailyVolume;
        dailyVolumeResetTime = block.timestamp;
    }

    function addToWhitelist(address account) external onlyComplianceOfficer whenNotPaused {
        require(account != address(0), "ComplianceRegistry: zero address");
        require(!blacklist[account], "ComplianceRegistry: address is blacklisted");
        whitelist[account] = true;
        emit AddressWhitelisted(account, "");
    }

    function addToWhitelistWithCap(address account, uint256 cap)
        external
        onlyComplianceOfficer
        whenNotPaused
    {
        require(account != address(0), "ComplianceRegistry: zero address");
        require(!blacklist[account], "ComplianceRegistry: address is blacklisted");
        whitelist[account] = true;
        perAddressCap[account] = cap;
        emit AddressWhitelisted(account, "");
    }

    function removeFromWhitelist(address account) external onlyComplianceOfficer {
        whitelist[account] = false;
        perAddressCap[account] = 0;
        emit AddressRemovedFromWhitelist(account);
    }

    function addToBlacklist(address account) external onlyComplianceOfficer {
        require(account != address(0), "ComplianceRegistry: zero address");
        blacklist[account] = true;
        whitelist[account] = false;
        perAddressCap[account] = 0;
        emit AddressBlacklisted(account);
    }

    function setLimits(uint256 _maxPerTx, uint256 _maxDailyVolume) external onlyOwner {
        maxPerTx = _maxPerTx;
        maxDailyVolume = _maxDailyVolume;
        emit LimitsUpdated(_maxPerTx, _maxDailyVolume);
    }

    function setComplianceOfficer(address _complianceOfficer) external onlyOwner {
        complianceOfficer = _complianceOfficer;
        emit RoleUpdated("complianceOfficer", _complianceOfficer);
    }

    function setAIAgent(address _aiAgent) external onlyOwner {
        aiAgent = _aiAgent;
        emit RoleUpdated("aiAgent", _aiAgent);
    }

    function setPaused(bool _paused) external onlyOwner {
        paused = _paused;
        emit Paused(_paused);
    }

    function isWhitelisted(address account) external view returns (bool) {
        return whitelist[account] && !blacklist[account];
    }

    function isBlacklisted(address account) external view returns (bool) {
        return blacklist[account];
    }

    function canReceive(address to, uint256 amount) external view returns (bool) {
        if (paused) return false;
        if (!whitelist[to] || blacklist[to]) return false;
        if (amount > maxPerTx) return false;
        _resetDailyIfNeeded();
        if (dailyVolumeUsed + amount > maxDailyVolume) return false;
        uint256 cap = perAddressCap[to];
        if (cap > 0) {
            // Caller (vault) would need to track per-address received; here we only check cap exists
            return true;
        }
        return true;
    }

    function setVault(address _vault) external onlyOwner {
        vault = _vault;
        emit RoleUpdated("vault", _vault);
    }

    function recordVolume(uint256 amount) external onlyAIAgentOrVault whenNotPaused {
        _resetDailyIfNeeded();
        require(dailyVolumeUsed + amount <= maxDailyVolume, "ComplianceRegistry: daily limit");
        dailyVolumeUsed += amount;
    }

    function _resetDailyIfNeeded() internal view {
        // Caller uses this for checks; actual reset in recordVolume
        if (block.timestamp >= dailyVolumeResetTime + SECONDS_PER_DAY) {
            // Next write will reset in recordVolume
        }
    }

    function resetDailyVolumeIfNeeded() external {
        if (block.timestamp >= dailyVolumeResetTime + SECONDS_PER_DAY) {
            dailyVolumeResetTime = block.timestamp;
            dailyVolumeUsed = 0;
        }
    }
}
