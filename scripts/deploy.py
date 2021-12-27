from brownie import accounts, Lottery, MockV3Aggregator, network, config
from web3 import Web3

def deploythingy():
    #account = accounts.load("metamask")
    account = accounts[0]
    print(account)
    print(Lottery)
    print(f"I'm on network {network.show_active()}")
    if network.show_active() in ["development", "ganache-local"]:
        mock_aggregator = MockV3Aggregator.deploy(18, Web3.toWei(4000, "ether"), {"from": account}, publish_source=False)
        print("Mock deployed!")
        price_feed_address = mock_aggregator.address
    else:
        price_feed_address = config["networks"][network.show_active()]["eth_usd_price_feed"]
    lottery = Lottery.deploy(price_feed_address, {"from": account}, publish_source=config["networks"][network.show_active()]["verify"])
    print("Current price is %s" % lottery.getEntranceFee())

def main():
    deploythingy()
    print("Hello")