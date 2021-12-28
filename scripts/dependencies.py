from brownie import accounts, Lottery, MockV3Aggregator, VRFCoordinatorMock, LinkToken, network, config, Contract, interface
from web3 import Web3

from scripts.lottery import LotteryContract

def is_development():
    return network.show_active() in ["development", "ganache-local"]

def build_lottery(account):
    if is_development():
        link_token = LinkToken.deploy({"from": account})      
        price_feed = MockV3Aggregator.deploy(18, Web3.toWei(4000, "ether"), {"from": account})
        vrf = VRFCoordinatorMock.deploy(link_token.address, {"from": account})
        link = link_token
        key_hash = config["networks"][network.show_active()]["key_hash"]
        fee = config["networks"][network.show_active()]["fee"]
        verify = config["networks"][network.show_active()]["verify"]
    else:
        price_feed = Contract.from_abi(
                MockV3Aggregator._name, 
                config["networks"][network.show_active()]["eth_usd_price_feed"],
                MockV3Aggregator.abi)
        vrf = Contract.from_abi(
                VRFCoordinatorMock._name, 
                config["networks"][network.show_active()]["vrf_coordinator"],
                VRFCoordinatorMock.abi)
        link = Contract.from_abi(
                LinkToken._name, 
                config["networks"][network.show_active()]["link_token"],
                LinkToken.abi)
        key_hash = config["networks"][network.show_active()]["key_hash"]
        fee = config["networks"][network.show_active()]["fee"]
        verify = config["networks"][network.show_active()]["verify"]
    return LotteryContract(price_feed, vrf, link, key_hash, fee, account, verify)