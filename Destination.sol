// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "./BridgeToken.sol";

contract Destination is AccessControl {
    bytes32 public constant WARDEN_ROLE = keccak256("BRIDGE_WARDEN_ROLE");
    bytes32 public constant CREATOR_ROLE = keccak256("CREATOR_ROLE");
    mapping(address => address) public underlying_tokens;  // Maps underlying token addresses to wrapped token addresses
    mapping(address => address) public wrapped_tokens;     // Maps wrapped token addresses to underlying token addresses
    address[] public tokens;                               // List of wrapped token addresses

    event Creation(address indexed underlying_token, address indexed wrapped_token);
    event Wrap(address indexed underlying_token, address indexed wrapped_token, address indexed to, uint256 amount);
    event Unwrap(address indexed underlying_token, address indexed wrapped_token, address frm, address indexed to, uint256 amount);

    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(CREATOR_ROLE, admin);
        _grantRole(WARDEN_ROLE, admin);
    }


function wrap(address _underlying_token, address _recipient, uint256 _amount) public onlyRole(WARDEN_ROLE) {
    // Ensure the underlying token is known and a wrapped token exists
    address wrappedTokenAddress = wrapped_tokens[_underlying_token];
    require(wrappedTokenAddress != address(0), "Destination: Wrapped token not found for underlying token");

    // Transfer the underlying token to this contract
    ERC20 underlyingToken = ERC20(_underlying_token);
    require(underlyingToken.transferFrom(msg.sender, address(this), _amount), "Destination: Transfer failed");

    // Mint the equivalent amount of the wrapped token to the recipient
    BridgeToken wrappedToken = BridgeToken(wrappedTokenAddress);
    wrappedToken.mint(_recipient, _amount);

    // Emit the wrap event
    emit Wrap(_underlying_token, wrappedTokenAddress, _recipient, _amount);
}


function unwrap(address _wrapped_token, address _recipient, uint256 _amount) public {
     // Ensure the wrapped token is known and an underlying token exists
     address underlyingTokenAddress = underlying_tokens[_wrapped_token];
     require(underlyingTokenAddress != address(0), "Destination: Underlying token not found for wrapped token");

     // Burn the wrapped tokens
     BridgeToken wrappedToken = BridgeToken(_wrapped_token);
     require(wrappedToken.balanceOf(msg.sender) >= _amount, "Destination: Insufficient wrapped token balance");
     wrappedToken.burn(_amount);

     // Transfer the equivalent amount of the underlying token to the recipient
     ERC20 underlyingToken = ERC20(underlyingTokenAddress);
     require(underlyingToken.transfer(_recipient, _amount), "Destination: Transfer failed");

     // Emit the unwrap event
     emit Unwrap(underlyingTokenAddress, _wrapped_token, msg.sender, _recipient, _amount);
 }


function createToken(
    address _underlying_token,
    string memory name,
    string memory symbol
) public onlyRole(CREATOR_ROLE) returns (address) {
    require(underlying_tokens[_underlying_token] == address(0), "Destination: Wrapped token already exists for this underlying token");

    uint256 initialSupply = 0;  // Assuming initial supply is zero
    address owner = address(this);  // Setting the contract itself as the owner

    // Create the new wrapped token with four arguments
    BridgeToken newToken = new BridgeToken(name, symbol, initialSupply, owner);
    address newTokenAddress = address(newToken);

    // Track the relationship between the underlying and wrapped tokens
    underlying_tokens[_underlying_token] = newTokenAddress;
    wrapped_tokens[newTokenAddress] = _underlying_token;

    // Store the wrapped token address
    tokens.push(newTokenAddress);

    // Emit the creation event
    emit Creation(_underlying_token, newTokenAddress);

    return newTokenAddress;
}










}
