// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

contract EmailHashStorage {
    address public owner;
    mapping(string => bytes32) private emailHashes;

    event HashStored(string uid, bytes32 emailHash);
    event HashRetrieved(string uid, bytes32 emailHash);

    constructor() {
        owner = msg.sender;  // Set the owner of the contract to the deployer
    } 

    // Modifier to restrict certain functions to the contract's owner
    modifier isOwner() {
        require(msg.sender == owner, "Caller is not the owner");
        _;
    }

    /**
     * Store the hash of an email's contents.
     * @param uid the unique identifier for the email
     * @param hash the SHA-256 hash of the email's contents
     */
    function storeHash(string calldata uid, bytes32 hash) external isOwner {
        require(emailHashes[uid] == 0, "Hash already exists for this UID");
        emailHashes[uid] = hash;
        emit HashStored(uid, hash);
    }

    /**
     * @param uid the unique identifier for the email
     * @return the hash of the email
     */
    function retrieveHash(string calldata uid) external view returns (bytes32) {
        require(emailHashes[uid] != 0, "No hash stored for this UID");
        return emailHashes[uid];
    }

    /**
     * Change the owner of the contract.
     * @param newOwner the address of the new owner
     */
    function changeOwner(address newOwner) external isOwner {
        require(newOwner != address(0), "New owner is the zero address");
        owner = newOwner;
    }
}
