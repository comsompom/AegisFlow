// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IComplianceRegistry {
    function isWhitelisted(address account) external view returns (bool);
    function isBlacklisted(address account) external view returns (bool);
    function canReceive(address to, uint256 amount) external view returns (bool);
    function recordVolume(uint256 amount) external;
    function maxPerTx() external view returns (uint256);
}

/**
 * @title AegisFlowVault
 * @dev ERC-20 style vault that only transfers to whitelisted addresses.
 * Uses ComplianceRegistry for KYC/AML checks (transfer hook in-contract).
 */
contract AegisFlowVault {
    string public name = "AegisFlow Vault Shares";
    string public symbol = "AFV";
    uint8 public decimals = 18;

    IComplianceRegistry public complianceRegistry;

    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;
    uint256 private _totalSupply;

    address public owner;
    address public treasury; // receives deposits / authorized to mint

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event Deposit(address indexed from, uint256 amount);
    event Withdraw(address indexed to, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner, "AegisFlowVault: not owner");
        _;
    }

    modifier onlyTreasury() {
        require(msg.sender == treasury || msg.sender == owner, "AegisFlowVault: not treasury");
        _;
    }

    constructor(address _complianceRegistry, address _treasury) {
        owner = msg.sender;
        treasury = _treasury;
        complianceRegistry = IComplianceRegistry(_complianceRegistry);
    }

    function setComplianceRegistry(address _complianceRegistry) external onlyOwner {
        complianceRegistry = IComplianceRegistry(_complianceRegistry);
    }

    function setTreasury(address _treasury) external onlyOwner {
        treasury = _treasury;
    }

    function totalSupply() external view returns (uint256) {
        return _totalSupply;
    }

    function balanceOf(address account) external view returns (uint256) {
        return _balances[account];
    }

    function allowance(address holder, address spender) external view returns (uint256) {
        return _allowances[holder][spender];
    }

    /**
     * @dev Deposit: treasury (or owner) mints vault shares to depositor.
     * In a full implementation, this would pull actual stablecoins (e.g. USDC).
     * For MVP we mint internal accounting units.
     */
    function deposit(address to, uint256 amount) external onlyTreasury {
        require(to != address(0), "AegisFlowVault: zero address");
        _mint(to, amount);
        emit Deposit(to, amount);
    }

    /**
     * @dev Transfer: only to whitelisted, non-blacklisted addresses; respects AML.
     */
    function transfer(address to, uint256 amount) external returns (bool) {
        _transfer(msg.sender, to, amount);
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        uint256 currentAllowance = _allowances[from][msg.sender];
        require(currentAllowance >= amount, "AegisFlowVault: insufficient allowance");
        unchecked {
            _allowances[from][msg.sender] = currentAllowance - amount;
        }
        _transfer(from, to, amount);
        return true;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        _allowances[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }

    /**
     * @dev Withdraw: vault sends tokens to whitelisted address. Compliance hook enforced.
     */
    function withdraw(address to, uint256 amount) external onlyTreasury returns (bool) {
        _withdraw(msg.sender, to, amount);
        return true;
    }

    /**
     * @dev AI agent or treasury can trigger transfer from vault balance to whitelisted recipient.
     */
    function withdrawTo(address from, address to, uint256 amount) external onlyTreasury returns (bool) {
        _withdraw(from, to, amount);
        return true;
    }

    function _transfer(address from, address to, uint256 amount) internal {
        require(from != address(0), "AegisFlowVault: from zero");
        require(to != address(0), "AegisFlowVault: to zero");
        require(complianceRegistry.isWhitelisted(to), "AegisFlowVault: recipient not whitelisted");
        require(!complianceRegistry.isBlacklisted(to), "AegisFlowVault: recipient blacklisted");
        require(amount <= complianceRegistry.maxPerTx(), "AegisFlowVault: exceeds maxPerTx");
        require(complianceRegistry.canReceive(to, amount), "AegisFlowVault: compliance check failed");

        uint256 fromBalance = _balances[from];
        require(fromBalance >= amount, "AegisFlowVault: insufficient balance");
        unchecked {
            _balances[from] = fromBalance - amount;
            _balances[to] += amount;
        }
        complianceRegistry.recordVolume(amount);
        emit Transfer(from, to, amount);
    }

    function _withdraw(address from, address to, uint256 amount) internal {
        require(complianceRegistry.isWhitelisted(to), "AegisFlowVault: recipient not whitelisted");
        require(!complianceRegistry.isBlacklisted(to), "AegisFlowVault: recipient blacklisted");
        require(amount <= complianceRegistry.maxPerTx(), "AegisFlowVault: exceeds maxPerTx");
        require(complianceRegistry.canReceive(to, amount), "AegisFlowVault: compliance check failed");

        uint256 fromBalance = _balances[from];
        require(fromBalance >= amount, "AegisFlowVault: insufficient balance");
        unchecked {
            _balances[from] = fromBalance - amount;
            _balances[to] += amount;
        }
        complianceRegistry.recordVolume(amount);
        emit Withdraw(to, amount);
        emit Transfer(from, to, amount);
    }

    function _mint(address account, uint256 amount) internal {
        require(account != address(0), "AegisFlowVault: mint to zero");
        _totalSupply += amount;
        _balances[account] += amount;
        emit Transfer(address(0), account, amount);
    }
}
