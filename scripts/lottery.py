from brownie import (Contract, LinkToken, Lottery, MockV3Aggregator,
                     VRFCoordinatorMock, accounts, config, network)
from web3.types import FeeHistory
from time import time


class LotteryContract:

    def __init__(self, price_feed_contract, vrf_coordinator_contract, link_token_contract, vrf_key_hash, vrf_fee, account, verify):
        self.price_feed_contract = price_feed_contract
        self.vrf_coordinator_contract = vrf_coordinator_contract
        self.link_token_contract = link_token_contract
        self.vrf_key_has = vrf_key_hash
        self.vrf_fee = vrf_fee
        self.lottery_contract = Lottery.deploy(
            price_feed_contract.address,
            vrf_coordinator_contract.address,
            link_token_contract.address,
            vrf_key_hash,
            vrf_fee,
            {"from": account}, publish_source=verify)

    def enter_lottery(self, account, amount):
        enterLottery = self.lottery_contract.enterLottery({"from": account, "value": amount})
        enterLottery.wait(1)

    def start_lottery(self, account):
        startLottery = self.lottery_contract.startLottery({"from": account})
        startLottery.wait(1)

    def get_entrance_fee(self):
        return self.lottery_contract.getEntranceFee()

    def end_lottery(self, account):
        stopLotteryAndPayout = self.lottery_contract.stopLotteryAndPayout({"from": account})
        stopLotteryAndPayout.wait(1)
        self.last_request_id = stopLotteryAndPayout.return_value

    def fund_with_link(self, account, amount):
        tx = self.link_token_contract.transfer(self.lottery_contract, amount, {"from": account})
        tx.wait(1)
        return tx

    def get_current_link_balance(self):
        return self.lottery_contract.getCurrentLinkTokenBalance().return_value

    def is_funded_enough(self):
        return self.lottery_contract.isFundedEnough().return_value

    def get_vrf_fee(self):
        return self.lottery_contract.getVrfFee().return_value

    def _test_only_vrf_callback(self):
        self.vrf_coordinator_contract.callBackWithRandomness(self.last_request_id, 1, self.lottery_contract)

    def get_current_eth_price(self):
        return self.lottery_contract.getCurrentEthPrice()