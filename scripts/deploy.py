from scripts.helpful_scripts import (
    get_account,
    get_contract,
    get_current_network,
    get_from_current_account,
)
from brownie import DappToken, TokenFarm, network, config
from web3 import Web3
import yaml, json, os, shutil

KEPT_BALANCE = Web3.toWei(100, "ether")


def deploy_token_farm_and_dapp_token(update_the_front_end=False):
    account = get_account()
    from_account = get_from_current_account()
    dapp_token = DappToken.deploy(from_account)
    token_farm = TokenFarm.deploy(
        dapp_token.address,
        from_account,
        publish_source=get_current_network()["verify"],
    )
    print(f"Value of the totalSupply:{dapp_token.totalSupply()}")
    print(f"Value of the kept:{KEPT_BALANCE}")
    tx = dapp_token.transfer(
        token_farm, dapp_token.totalSupply() - KEPT_BALANCE, from_account
    )

    tx.wait(1)
    # dapp_token, weth_token, fau_token/dai
    weth_token = get_contract("weth_token")
    fau_token = get_contract("fau_token")
    dict_of_allowed_tokens = {
        dapp_token: get_contract("dai_usd_price_feed"),
        fau_token: get_contract("dai_usd_price_feed"),
        weth_token: get_contract("eth_usd_price_feed"),
    }
    add_allowed_tokens(token_farm, dict_of_allowed_tokens)
    if update_the_front_end:
        update_front_end()
    return token_farm, dapp_token


def update_front_end():
    # Send the build folder
    copy_folders_to_front_end("./build", "./front_end/src/chain-info")

    # Sending the front end our config in JSON format
    with open("brownie-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open("./front_end/src/brownie-config.json", "w") as brownie_config_json:
            json.dump(config, brownie_config_json)
    print("Front-end updated!")


def copy_folders_to_front_end(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def add_allowed_tokens(token_farm, dict_of_allowed_tokens):
    for token in dict_of_allowed_tokens:
        add_tx = token_farm.addAllowedTokens(token.address, get_from_current_account())
        add_tx.wait(1)

        set_tx = token_farm.setPriceFeedContract(
            token.address, dict_of_allowed_tokens[token], get_from_current_account()
        )
        set_tx.wait(1)
    return token_farm


def main():
    deploy_token_farm_and_dapp_token(update_the_front_end=True)
