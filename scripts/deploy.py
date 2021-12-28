from brownie import accounts
from scripts.dependencies import build_lottery

def main():
    account = accounts.load("metamask")
    # account = accounts[0]
    lottery = build_lottery(account)