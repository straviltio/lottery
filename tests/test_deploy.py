from brownie import accounts, Lottery, MockV3Aggregator, network, config, exceptions
from web3 import Web3
import pytest

account = None
deployed_lottery_contract = None

@pytest.fixture(autouse=True)
def run_around_tests():
    global account
    account = accounts[0]
    mock_aggregator = MockV3Aggregator.deploy(18, Web3.toWei(4000, "ether"), {"from": account})
    price_feed_address = mock_aggregator.address
    global deployed_lottery_contract
    deployed_lottery_contract = Lottery.deploy(price_feed_address, {"from": account})

    # Ensure can't enter lottery yet
    with pytest.raises(exceptions.VirtualMachineError):
        deployed_lottery_contract.enterLottery({"from": account, "value": 100})

    deployed_lottery_contract.startLottery({"from": account})
    yield

def test_get_entrance_fee():
    assert 80 == deployed_lottery_contract.getEntranceFee()

def test_entrance_check_passes():
    deployed_lottery_contract.enterLottery({"from": account, "value": 100})

def test_entrance_check_fails():
    with pytest.raises(exceptions.VirtualMachineError):
        deployed_lottery_contract.enterLottery({"from": account, "value": 5})

def test_lottery_end_works_when_owner():
    deployed_lottery_contract.enterLottery({"from": account, "value": 100})

    deployed_lottery_contract.stopLotteryAndPayout({"from": account})

def test_lottery_end_fails_when_not_owner():
    deployed_lottery_contract.enterLottery({"from": account, "value": 100})

    not_owner_account = accounts[1]
    with pytest.raises(exceptions.VirtualMachineError):
        deployed_lottery_contract.stopLotteryAndPayout({"from": not_owner_account})

def test_fails_to_enter_lottery_when_its_closed():
    deployed_lottery_contract.enterLottery({"from": account, "value": 100})
    deployed_lottery_contract.stopLotteryAndPayout({"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        deployed_lottery_contract.enterLottery({"from": account, "value": 100})
