// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";

contract Lottery {
    uint256 MINIMUM_PRICE_USD = 50;
    uint256 DECIMALS_FOR_ETH_CONVERSION = 10**18;

    address payable[] public players;
    address public owner;
    AggregatorV3Interface public priceFeed;

    constructor(address _priceFeed) public {
        owner = msg.sender;
        priceFeed = AggregatorV3Interface(_priceFeed);
    }

    function enterLottery() public payable {
        require(msg.value > getEntranceFee(), "Pay more");
        players.push(msg.sender);
    }

    function getPrice() public view returns(uint256) {
        (,int256 answer,,,) = priceFeed.latestRoundData();
        return uint256(answer);
    }

    function getEntranceFee() public view returns(uint256) {
        return getPrice() / DECIMALS_FOR_ETH_CONVERSION / MINIMUM_PRICE_USD;
    }

    modifier onlyOwner {
        require(msg.sender == owner, "you need to be the owner");
        _;
    }

    function stopLotteryAndPayout() public onlyOwner payable {
        players[0].transfer(address(this).balance);
        players = new address payable[](0);
    } 
}