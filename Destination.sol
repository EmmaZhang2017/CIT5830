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
        require(_amount > 0, "Amount must be greater than zero");
        require(underlying_tokens[_underlying_token] != address(0), "Wrapped token does not exist");

        // Transfer the underlying token from the warden to this contract
        ERC20(_underlying_token).transferFrom(msg.sender, address(this), _amount);

        // Get the wrapped token address
        address wrapped_token = underlying_tokens[_underlying_token];

        // Transfer the wrapped tokens to the recipient
        ERC20(wrapped_token).transfer(_recipient, _amount);

        emit Wrap(_underlying_token, wrapped_token, _recipient, _amount);
    }

    function unwrap(address _wrapped_token, address _recipient, uint256 _amount) public {
        require(_amount > 0, "Amount must be greater than zero");
        require(wrapped_tokens[_wrapped_token] != address(0), "Underlying token does not exist");

        // Transfer the wrapped tokens from the caller to this contract
        ERC20(_wrapped_token).transferFrom(msg.sender, address(this), _amount);

        // Get the underlying token address
        address underlying_token = wrapped_tokens[_wrapped_token];

        // Transfer the underlying tokens to the recipient
        ERC20(underlying_token).transfer(_recipient, _amount);

        emit Unwrap(underlying_token, _wrapped_token, msg.sender, _recipient, _amount);
    }

    function createToken(address _underlying_token, string memory name, string memory symbol) public onlyRole(CREATOR_ROLE) returns (address) {
        require(_underlying_token != address(0), "Invalid underlying token address");
        
        // Create a new wrapped token contract
        BridgeToken newToken = new BridgeToken(name, symbol);
        address wrapped_token = address(newToken);

        // Update the mappings
        underlying_tokens[_underlying_token] = wrapped_token;
        wrapped_tokens[wrapped_token] = _underlying_token;
        tokens.push(wrapped_token);

        emit Creation(_underlying_token, wrapped_token);
        return wrapped_token;
    }
}