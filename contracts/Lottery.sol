// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is Ownable {
    uint256 MINIMUM_PRICE_USD = 50;
    uint256 DECIMALS_FOR_ETH_CONVERSION = 10**18;

    address payable[] public players;
    AggregatorV3Interface public priceFeed;

    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lotteryState;

    constructor(address _priceFeed) {
        priceFeed = AggregatorV3Interface(_priceFeed);
        lotteryState = LOTTERY_STATE.CLOSED;
    }

    function enterLottery() public payable {
        require(msg.value > getEntranceFee(), "Pay more");
        require(lotteryState == LOTTERY_STATE.OPEN, "Lottery must be open");
        players.push(payable(msg.sender));
    }

    function getPrice() public view returns(uint256) {
        (,int256 answer,,,) = priceFeed.latestRoundData();
        return uint256(answer);
    }

    function getEntranceFee() public view returns(uint256) {
        return getPrice() / DECIMALS_FOR_ETH_CONVERSION / MINIMUM_PRICE_USD;
    }

    function startLottery() public onlyOwner {
        lotteryState = LOTTERY_STATE.OPEN;
    } 

    function stopLotteryAndPayout() public onlyOwner payable {
        players[0].transfer(address(this).balance);
        players = new address payable[](0);
        lotteryState = LOTTERY_STATE.CLOSED;
    } 
}