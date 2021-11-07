from brownie import accounts, network, config

from brownie import (
    accounts,
    network,
    config,
    MockV3Aggregator,
    MockDAI,
    MockWETH,
    Contract,
    interface,
)

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
OPENSEA_URL = "https://testnets.opensea.io/assets/{}/{}"


def get_account(index=None, id=None):

    if index:
        return accounts[index]
    if id:
        return accounts.load(id)

    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "dai_usd_price_feed": MockV3Aggregator,
    "fau_token": MockDAI,
    "weth_token": MockWETH,
}


def get_from_current_account():
    return {"from": get_account()}


def get_current_network():
    return config["networks"][network.show_active()]


def get_contract(contract_name):
    """This function will grab the contract addresses from the brownie config if define, otherwise
    it will deploy a mock version of that contract, and returns that mock contract

        Args:
            contract_name (string)

        Returns:
            brownie.network.contract.ProjectContract: the most recently deployed version of this contract.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            # MockV3Aggregator.length
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )

    return contract


DECIMALS = 18
INITIAL_VALUE = 10000000000000000000000  # ETH price at 1k


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, get_from_current_account())
    MockDAI.deploy(get_from_current_account())
    MockWETH.deploy(get_from_current_account())
    print("MOCKs Deployed!")
