from brownie import accounts
from scripts.dependencies import build_lottery

def deploythingy():
    account = accounts.load("metamask")
    #account = accounts[0]
    lottery = build_lottery(account)
    lottery.start_lottery(account)
    lottery.enter_lottery(account, 100)
    lottery.fund_with_link(account, 10000000000000000000000000000000000)
    lottery.end_lottery(account)

def main():
    deploythingy()
    print("Hello")