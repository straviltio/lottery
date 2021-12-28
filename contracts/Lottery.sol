// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";

contract Lottery is Ownable, VRFConsumerBase {
    uint256 MINIMUM_PRICE_USD = 50;
    uint256 DECIMALS_FOR_ETH_CONVERSION = 10**8;

    address payable[] public players;
    AggregatorV3Interface public priceFeed;
    uint256 fee;
    bytes32 keyHash;

    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lotteryState;

    constructor(
        address _priceFeed,         
        address _vrfCoordinator, 
        address _vrfToken, 
        bytes32 _keyHash,
        uint256 _fee
    ) VRFConsumerBase(_vrfCoordinator, _vrfToken) {
        fee = _fee;
        keyHash = _keyHash;
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
        require(lotteryState == LOTTERY_STATE.CLOSED, "Lottery must be closed");
        lotteryState = LOTTERY_STATE.OPEN;
    } 

    function stopLotteryAndPayout() public onlyOwner payable returns (bytes32) {
        lotteryState = LOTTERY_STATE.CALCULATING_WINNER;
        require(isFundedEnough(), "Not enough LINK - fill contract with faucet");
        return requestRandomness(keyHash, fee);
    }

    function fulfillRandomness(bytes32 requestId, uint256 randomness) internal override {
        uint256 winnerIndex = randomness % players.length;
        address payable recentWinner = payable(players[winnerIndex]);
        recentWinner.transfer(address(this).balance);
        players = new address payable[](0);
        lotteryState = LOTTERY_STATE.CLOSED;
    }

    function getCurrentLinkTokenBalance() public returns (uint256) {
        return LINK.balanceOf(address(this));
    }

    function isFundedEnough() public returns (bool) {
        return LINK.balanceOf(address(this)) >= fee;
    }

    function getVrfFee() public returns (uint256) {
        return fee;
    }
}