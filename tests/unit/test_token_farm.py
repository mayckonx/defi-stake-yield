from brownie import network, exceptions
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    get_contract,
    get_from_current_account,
    INITIAL_VALUE,
    DECIMALS,
)
from scripts.deploy import deploy_token_farm_and_dapp_token, KEPT_BALANCE
import pytest


def test_add_allowed_tokens():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    non_owner = get_account(index=1)
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    # Act
    token_farm.addAllowedTokens(dapp_token.address, {"from": account})
    # Assert
    assert token_farm.allowedTokens(0) == dapp_token.address
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.addAllowedTokens(dapp_token.address, {"from": non_owner})


def test_stake_unapproved_tokens(random_erc20, amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    # Act
    random_erc20.approve(token_farm.address, amount_staked, {"from": account})
    # Assert
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.stakeTokens(amount_staked, random_erc20.address, {"from": account})


def test_set_price_feed_contract():
    # Arrange
    account, token_farm, dapp_token = get_account_token_farm_and_dapp_token()
    non_owner = get_account(index=2)

    # Act
    price_feed_address = get_contract("eth_usd_price_feed")
    token_farm.setPriceFeedContract(
        dapp_token.address, price_feed_address, get_from_current_account()
    )

    # Assert
    assert token_farm.tokenPriceFeedMapping(dapp_token.address) == price_feed_address
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.setPriceFeedContract(
            dapp_token.address, price_feed_address, {"from": non_owner}
        )


def test_stake_tokens_without_approval_should_throw_exception(amount_staked):
    # Arrange
    account, token_farm, dapp_token = get_account_token_farm_and_dapp_token()

    # assert
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.stakeTokens(
            amount_staked, dapp_token.address, get_from_current_account()
        )


def test_stake_tokens(amount_staked):
    # Arrange
    account, token_farm, dapp_token = get_account_token_farm_and_dapp_token()

    # Act
    dapp_token.approve(token_farm.address, amount_staked, get_from_current_account())
    token_farm.stakeTokens(
        amount_staked, dapp_token.address, get_from_current_account()
    )

    # Assert
    assert (
        token_farm.stakingBalance(dapp_token.address, account.address) == amount_staked
    )
    assert token_farm.uniqueTokensStaked(account.address) == 1
    assert token_farm.stakers(0) == account
    return token_farm, dapp_token


def test_unstake_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    # Act
    token_farm.unstakeTokens(dapp_token.address, {"from": account})
    # Assert
    assert dapp_token.balanceOf(account.address) == KEPT_BALANCE
    assert token_farm.stakingBalance(dapp_token.address, account.address) == 0
    assert token_farm.uniqueTokensStaked(account.address) == 0


def test_issue_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    starting_balance = dapp_token.balanceOf(account.address)

    # Act
    token_farm.issueTokens(get_from_current_account())

    # Arrange
    # We are staking 1dapp_token == in price to 1ETH
    # so... we should get 2,000 dapp tokens in reward
    # since the price of eth is $2,000
    assert dapp_token.balanceOf(account.address) == starting_balance + INITIAL_VALUE


# auxiliar
def get_account_token_farm_and_dapp_token():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    account = get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()

    return account, token_farm, dapp_token
