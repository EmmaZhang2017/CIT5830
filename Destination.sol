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
    address wrappedTokenAddress = wrapped_tokens[_underlying_token];
    require(wrappedTokenAddress != address(0), "Destination: Wrapped token not found");

    ERC20 underlyingToken = ERC20(_underlying_token);
    require(underlyingToken.allowance(msg.sender, address(this)) >= _amount, "Destination: Insufficient allowance");
    require(underlyingToken.transferFrom(msg.sender, address(this), _amount), "Destination: Transfer failed");

    _mintWrappedToken(_recipient, _amount, wrappedTokenAddress);
    emit Wrap(_underlying_token, wrappedTokenAddress, _recipient, _amount);
}

function unwrap(address _wrapped_token, address _recipient, uint256 _amount) public onlyRole(WARDEN_ROLE) {
    address underlyingTokenAddress = underlying_tokens[_wrapped_token];
    require(underlyingTokenAddress != address(0), "Destination: No underlying token");

    BridgeToken wrappedToken = BridgeToken(_wrapped_token);
    require(wrappedToken.balanceOf(msg.sender) >= _amount, "Destination: Insufficient balance");
    wrappedToken.burnFrom(msg.sender, _amount);

    ERC20 underlyingToken = ERC20(underlyingTokenAddress);
    require(underlyingToken.transfer(_recipient, _amount), "Destination: Transfer failed");
    emit Unwrap(underlyingTokenAddress, _wrapped_token, msg.sender, _recipient, _amount);
}







    function createToken(
        address _underlying_token,
        string memory name,
        string memory symbol
    ) public onlyRole(CREATOR_ROLE) returns (address) {
        require(underlying_tokens[_underlying_token] == address(0), "Destination: Wrapped token already exists for this underlying token");

        // Deploy a new BridgeToken with appropriate parameters
        address owner = address(this);
        BridgeToken newToken = new BridgeToken(_underlying_token, name, symbol, owner);
        address newTokenAddress = address(newToken);

        // Update the mappings to track the relationship between the underlying and wrapped tokens
        underlying_tokens[_underlying_token] = newTokenAddress;
        wrapped_tokens[newTokenAddress] = _underlying_token;

        // Store the wrapped token address
        tokens.push(newTokenAddress);

        // Emit the creation event
        emit Creation(_underlying_token, newTokenAddress);

        return newTokenAddress;
    }
}
