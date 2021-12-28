from brownie import accounts, Lottery, MockV3Aggregator, network, config, exceptions
from web3 import Web3
import pytest
from scripts.lottery import LotteryContract
from scripts.dependencies import build_lottery

account = None
lottery = None

@pytest.fixture(autouse=True)
def run_around_tests():
    print(f"Current test is {network.show_active()}")
    global account
    account = accounts[0]
    global lottery
    lottery = build_lottery(account)

    # Ensure can't enter lottery yet
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter_lottery(account, 1000000000000000000)

    lottery.start_lottery(account)
    yield

def test_get_current_eth_price():
    assert 397707592737 == lottery.get_current_eth_price()

def test_get_entrance_fee():
    assert 125720506 == lottery.get_entrance_fee()

def test_entrance_check_passes():
    global account
    lottery.enter_lottery(account, 1000000000000000000)

def test_entrance_check_fails_not_enough_funds():
    global account
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter_lottery(account, 5)

def test_lottery_end_works_when_owner():
    global account
    lottery.enter_lottery(account, 1000000000000000000)
    lottery.fund_with_link(account, 200000000000000000)
    lottery.end_lottery(account)

def test_lottery_pays_out():
    global account
    lottery.enter_lottery(account, 1000000000000000000)
    account_balance_before_winning = account.balance()
    lottery.fund_with_link(account, 200000000000000000)
    lottery.end_lottery(account)
    lottery._test_only_vrf_callback()
    assert account_balance_before_winning < account.balance()

def test_lottery_end_fails_when_not_owner():
    global account
    lottery.enter_lottery(account, 1000000000000000000)

    not_owner_account = accounts[1]
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.end_lottery(not_owner_account)

def test_fails_to_enter_lottery_when_its_closed():
    global account
    lottery.fund_with_link(account, 200000000000000000)
    lottery.fund_with_link(account, 100)
    lottery.end_lottery(account)
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter_lottery(account, 1000000000000000000)

def test_fund_with_link():
    lottery.fund_with_link(account, 100)
    assert lottery.get_current_link_balance() == 100

def test_vrf_is_funded():
    lottery.fund_with_link(account, 200000000000000000)
    assert lottery.is_funded_enough() is True

def test_get_current_link_balance_when_vrf_is_funded():
    lottery.fund_with_link(account, 200000000000000000)
    assert lottery.get_current_link_balance() == 200000000000000000

def test_vrf_isnt_funded_enough():
    assert lottery.is_funded_enough() is False

def test_get_current_link_balance_when_vrf_isnt_funded():
    assert lottery.get_current_link_balance() == 0

def test_get_vrf_fee():
    assert lottery.get_vrf_fee() == 100000000000000000
    
