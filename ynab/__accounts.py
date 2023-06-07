# Copyright (c) 2021 Erik Zwiefel
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from dataclasses import dataclass, field
from typing import List, Optional

from ynab.__base import RESTBase
from ynab.__transactions import Transaction


@dataclass
class Account:
    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    deleted: Optional[bool] = None
    api: Optional[object] = None

    meta: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, api, data: dict) -> "Account":
        known_args = {}
        unknown_args = {}

        for key, value in data.items():
            if key in cls.__annotations__:
                known_args[key] = value
            else:
                unknown_args[key] = value

        return cls(**known_args, api=api, meta=unknown_args)

    def get_transactions(self, since_date: Optional[str] = None) -> List[Transaction]:
        return self.api.parent.transactions.get_by_account(account_id=self.id, since_date=since_date)  # type: ignore

    def get_transactions_by_payee(
        self, payee_name: str, since_date: Optional[str] = None
    ) -> List[Transaction]:
        transactions = self.api.parent.transactions.get_by_account(  # type: ignore
            account_id=self.id, since_date=since_date
        )

        return list(filter(lambda x: x.payee_name == payee_name, transactions))

    def __repr__(self):
        return f"Account(" f"name='{self.name}', " f"type='{self.type}'" f")"


class AccountsAPI(RESTBase):
    def __init__(self, budget_id: str, **kwargs):
        super().__init__(**kwargs)
        self._budget_id = budget_id
        self._budget_uri = f"/budgets/{budget_id}/"

    def __load_accounts_from_json(self, data: dict):
        return [Account.from_dict(data=a, api=self) for a in data["data"]["accounts"]]

    def get_all(self):
        method = "GET"
        api_path = self._budget_uri + f"accounts"

        resp = self._rest_call[method](api_path)

        return self.__load_accounts_from_json(resp.json())

    def get_by_name(self, name: str):
        all_accounts = self.get_all()

        for c in all_accounts:
            if c.name == name:
                ret_val = c
                break
        else:
            ret_val = None

        return ret_val
