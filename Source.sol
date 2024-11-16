// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract Source is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant WARDEN_ROLE = keccak256("BRIDGE_WARDEN_ROLE");

    mapping(address => bool) public approved; // Tracks approved tokens
    address[] public tokens; // Stores a list of approved tokens

    event Deposit(address indexed token, address indexed recipient, uint256 amount);
    event Withdrawal(address indexed token, address indexed recipient, uint256 amount);
    event Registration(address indexed token);

    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(ADMIN_ROLE, admin);
        _grantRole(WARDEN_ROLE, admin);
    }

    /**
     * @notice Deposit tokens into the contract.
     * @param _token The address of the ERC20 token to deposit.
     * @param _recipient The address to credit the tokens to.
     * @param _amount The amount of tokens to deposit.
     */
    function deposit(address _token, address _recipient, uint256 _amount) public {
        require(approved[_token], "Token is not approved");
        require(_amount > 0, "Amount must be greater than 0");

        ERC20 token = ERC20(_token);

        // Transfer tokens from sender to this contract
        require(token.transferFrom(msg.sender, address(this), _amount), "Transfer failed");

        emit Deposit(_token, _recipient, _amount);
    }

    /**
     * @notice Withdraw tokens from the contract.
     * @param _token The address of the ERC20 token to withdraw.
     * @param _recipient The address to send the tokens to.
     * @param _amount The amount of tokens to withdraw.
     */
    function withdraw(address _token, address _recipient, uint256 _amount) public onlyRole(WARDEN_ROLE) {
        require(approved[_token], "Token is not approved");
        require(_amount > 0, "Amount must be greater than 0");

        ERC20 token = ERC20(_token);

        // Transfer tokens from this contract to the recipient
        require(token.transfer(_recipient, _amount), "Transfer failed");

        emit Withdrawal(_token, _recipient, _amount);
    }

    /**
     * @notice Register a token to allow its deposit and withdrawal.
     * @param _token The address of the ERC20 token to register.
     */
    function registerToken(address _token) public onlyRole(ADMIN_ROLE) {
        require(!approved[_token], "Token already registered");

        approved[_token] = true;
        tokens.push(_token);

        emit Registration(_token);
    }
}
