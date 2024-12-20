// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "./BridgeToken.sol";

contract Destination is AccessControl {
    using SafeERC20 for ERC20;

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

    function _mintWrappedToken(address _recipient, uint256 _amount, address _wrappedToken) internal {
        require(_amount > 0, "Destination: Mint amount must be greater than zero");
        BridgeToken wrappedToken = BridgeToken(_wrappedToken);
        wrappedToken.mint(_recipient, _amount);
    }

    function wrap(address _underlying_token, address _recipient, uint256 _amount) public onlyRole(WARDEN_ROLE) {
        require(_amount > 0, "Destination: Amount must be greater than zero");

        address wrappedTokenAddress = wrapped_tokens[_underlying_token];
        require(wrappedTokenAddress != address(0), "Destination: Wrapped token not found");

        ERC20 underlyingToken = ERC20(_underlying_token);
        require(underlyingToken.allowance(msg.sender, address(this)) >= _amount, "Destination: Insufficient allowance");
        underlyingToken.safeTransferFrom(msg.sender, address(this), _amount);

        _mintWrappedToken(_recipient, _amount, wrappedTokenAddress);
        emit Wrap(_underlying_token, wrappedTokenAddress, _recipient, _amount);
    }

    function unwrap(address _wrapped_token, address _recipient, uint256 _amount) public {
        require(_amount > 0, "Destination: Amount must be greater than zero");

        address underlyingTokenAddress = underlying_tokens[_wrapped_token];
        require(underlyingTokenAddress != address(0), "Destination: No underlying token");

        BridgeToken wrappedToken = BridgeToken(_wrapped_token);
        require(wrappedToken.balanceOf(msg.sender) >= _amount, "Destination: Insufficient balance to unwrap");
        wrappedToken.burnFrom(msg.sender, _amount);

        ERC20 underlyingToken = ERC20(underlyingTokenAddress);
        underlyingToken.safeTransfer(_recipient, _amount);
        emit Unwrap(underlyingTokenAddress, _wrapped_token, msg.sender, _recipient, _amount);
    }

    function createToken(
        address _underlying_token,
        string memory name,
        string memory symbol
    ) public onlyRole(CREATOR_ROLE) returns (address) {
        require(_underlying_token != address(0), "Destination: Invalid underlying token address");
        require(underlying_tokens[_underlying_token] == address(0), "Destination: Wrapped token already exists for this underlying token");

        address owner = address(this);
        BridgeToken newToken = new BridgeToken(_underlying_token, name, symbol, owner);
        address newTokenAddress = address(newToken);

        underlying_tokens[_underlying_token] = newTokenAddress;
        wrapped_tokens[newTokenAddress] = _underlying_token;
        tokens.push(newTokenAddress);

        emit Creation(_underlying_token, newTokenAddress);
        return newTokenAddress;
    }
}
