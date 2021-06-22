# Copyright (c) 2021 Erik Zwiefel
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import pytest

from context import ynab, ynab_env


@pytest.fixture()
def client(ynab_env) -> ynab.YNABBudgetClient:
    # Create YNAB Client
    return ynab.YNABBudgetClient(
        budget_id=ynab_env.budget_id,
        pat_token=ynab_env.token
    )


@pytest.fixture()
def account(client, ynab_env) -> ynab.Account:
    return client.accounts.get_by_name(ynab_env.account)


def test_get_all_accounts(client):
    accounts = client.accounts.get_all()

    assert isinstance(accounts, list)
    assert isinstance(accounts[0], ynab.Account)


def test_get_account_by_name(account, ynab_env):
    assert isinstance(account, ynab.Account)
    assert account.name == ynab_env.account


def test_invalid_account_by_name_returns_none(client):
    assert client.accounts.get_by_name("NO SUCH ACCOUNT") is None


def test_get_transactions(account):
    transaction_list = account.get_transactions()

    assert isinstance(transaction_list, list)
    assert isinstance(transaction_list[0], ynab.Transaction)


def test_save_transactions_generated_correctly(account):
    transaction = account.get_transactions()[0]
    save_transaction = transaction.save_transaction

    # Dict Object
    assert isinstance(save_transaction, dict)

    # Attributes match
    assert transaction.id == save_transaction['id']
    assert transaction.payee_id == save_transaction['payee_id']
    assert transaction.memo == save_transaction['memo']
    assert transaction.date == save_transaction['date']
    assert len(transaction.subtransactions) == len(save_transaction['subtransactions'])

# TODO: Test sub transactions
# TODO: Test "create new transaction"
# TODO: Test create and delete transactions
# TODO: Test Categories functionality
