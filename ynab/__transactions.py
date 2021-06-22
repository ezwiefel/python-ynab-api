# Copyright (c) 2021 Erik Zwiefel
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from dataclasses import dataclass, field
from typing import List, Union

from ynab.__base import RESTBase


@dataclass
class Subtransaction:
    id: str = None
    transaction_id: str = None
    amount: int = None
    memo: str = None
    payee_id: str = None
    payee_name: str = None
    category_id: str = None
    category_name: str = None
    transfer_account_id: str = None
    transfer_transaction_id: str = None
    deleted: bool = None

    meta: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> 'Subtransaction':
        known_args = {}
        unknown_args = {}

        for key, value in data.items():
            if key in cls.__annotations__:
                known_args[key] = value
            else:
                unknown_args[key] = value

        return cls(**known_args, meta=unknown_args)

    @property
    def save_sub_transaction(self):
        return {
            "amount": self.amount,
            "payee_id": self.payee_id,
            "category_id": self.category_id,
            "memo": self.memo
        }

    def __repr__(self):
        return f"Subtransaction(" \
               f"payee='{self.payee_name}, " \
               f"amount='{self.amount / 1000:.2f}', " \
               f"category='{self.category_name}'" \
               f")"


@dataclass
class Transaction:
    id: str = None
    date: str = None
    amount: int = None
    memo: str = None
    cleared: str = None
    approved: bool = None
    flag_color: str = None
    account_id: str = None
    payee_id: str = None
    category_id: str = None
    transfer_account_id: str = None
    transfer_transaction_id: str = None
    matched_transaction_id: str = None
    import_id: str = None
    deleted: bool = None
    account_name: str = None
    payee_name: str = None
    category_name: str = None

    subtransactions: List[Subtransaction] = field(default_factory=list)
    meta: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        known_args = {}
        unknown_args = {}
        subtransactions = []

        # Create subtransactions
        if 'subtransactions' in data:
            subtransactions_list = data.pop('subtransactions')

            subtransactions = [Subtransaction.from_dict(st) for st in subtransactions_list]

        for key, value in data.items():
            if key in cls.__annotations__:
                known_args[key] = value
            else:
                unknown_args[key] = value

        return cls(**known_args, meta=unknown_args, subtransactions=subtransactions)

    @property
    def save_transaction(self) -> dict:

        data = {
            "account_id": self.account_id,
            "date": self.date,
            "amount": self.amount if len(self.subtransactions) == 0 else sum([s.amount for s in self.subtransactions]),
            "category_id": self.category_id if len(self.subtransactions) == 0 else None,
            "subtransactions": [s.save_sub_transaction for s in self.subtransactions],
            "memo": self.memo,
            "flag_color": self.flag_color
        }

        if self.payee_id:
            data['payee_id'] = self.payee_id
        else:
            data['payee_name'] = self.payee_name

        if self.id:
            data['id'] = self.id

        return data

    def __repr__(self):
        return f"Transaction(" \
               f"date='{self.date}', " \
               f"payee='{self.payee_name}', " \
               f"amount='{self.amount / 1000:.2f}', " \
               f"category='{self.category_name}', " \
               f"subtransactions={len(self.subtransactions)}" \
               f")"


class TransactionAPI(RESTBase):

    def __init__(self, budget_id: str, **kwargs):
        super().__init__(**kwargs)
        self._budget_id = budget_id
        self._budget_uri = f'/budgets/{budget_id}/'

    @staticmethod
    def __load_transactions_from_json(data: dict) -> Union[List[Transaction], Transaction]:
        if transactions := data['data'].get('transactions'):
            return [Transaction.from_dict(t) for t in transactions]
        else:
            return Transaction.from_dict(data['data']['transaction'])

    def get_all(self, since_date: str = None) -> List[Transaction]:
        method = "GET"
        api_path = self._budget_uri + f"transactions/"
        params = {}

        if since_date:
            params['since_date'] = since_date

        resp = self._rest_call[method](api_path, params)

        return self.__load_transactions_from_json(resp.json())

    def get_by_account(self, account_id: str, since_date: str = None) -> List[Transaction]:
        method = "GET"
        api_path = self._budget_uri + f"accounts/{account_id}/transactions"
        params = {}

        if since_date:
            params['since_date'] = since_date

        resp = self._rest_call[method](api_path, params)

        return self.__load_transactions_from_json(resp.json())

    def save(self, transactions: Transaction) -> Union[List[Transaction], Transaction]:
        if isinstance(transactions, list):
            return self.save_many(transactions)
        elif transactions.id:
            return self.update_transaction(transactions)
        else:
            return self.create_transaction(transactions)

    def save_many(self, transactions: List[Transaction]) -> Union[List[Transaction], Transaction]:
        # For each transaction, determine if the transaction already exists
        # if so, then update it

        update_queue = []
        create_queue = []
        completed_trans = []

        for t in transactions:
            if t.id:
                update_queue.append(t)
            else:
                create_queue.append(t)

        if len(update_queue) >= 1:
            completed_trans.extend(self.update_transaction(update_queue))

        if len(create_queue) >= 1:
            completed_trans.extend(self.create_transaction(create_queue))

        return completed_trans

    def update_transaction(self, transactions: Union[List[Transaction], Transaction]):
        # Since there are different methods and endpoints, create two seperate functions
        if isinstance(transactions, list):
            return self._update_many_transactions(transactions)
        else:
            return self._update_single_transaction(transactions)

    def _update_single_transaction(self, transaction: Transaction):
        method = "PUT"
        api_path = self._budget_uri + f"transactions/{transaction.id}"

        data = {"transaction": transaction.save_transaction}
        resp = self._rest_call[method](api_path, data)

        return self.__load_transactions_from_json(resp.json())

    def _update_many_transactions(self, transactions: List[Transaction]):
        method = "PATCH"
        api_path = self._budget_uri + f"transactions"

        data = {"transactions": [t.save_transaction for t in transactions]}
        resp = self._rest_call[method](api_path, data)

        return self.__load_transactions_from_json(resp.json())

    def create_transaction(self, transactions: Union[Transaction, List[Transaction]]):
        method = "POST"
        api_path = self._budget_uri + f"transactions/"

        if isinstance(transactions, list):
            data = {"transactions": [t.save_transaction for t in transactions]}
        else:
            data = {"transaction": transactions.save_transaction}

        resp = self._rest_call[method](api_path, data)

        return self.__load_transactions_from_json(resp.json())

    def import_all(self):
        method = "POST"
        api_path = self._budget_uri + f"transactions/import"
        data = {}
        resp = self._rest_call[method](api_path, data)

        return resp.json()
