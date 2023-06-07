# Copyright (c) 2021 Erik Zwiefel
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from ynab.__accounts import AccountsAPI
from ynab.__categories import CategoriesAPI
from ynab.__transactions import TransactionAPI


class YNABBudgetClient(object):
    BASE_URL = "https://api.ynab.com"
    API_VERSION = "v1"

    def __init__(self, budget_id: str, pat_token: str, **kwargs) -> None:
        super().__init__()
        self.budget_id = budget_id

        api_kwargs = {
            "host": self.BASE_URL,
            "api_version": self.API_VERSION,
            "budget_id": self.budget_id,
            "token": pat_token,
            "parent": self,
        }

        self.categories = CategoriesAPI(**api_kwargs)
        self.transactions = TransactionAPI(**api_kwargs)
        self.accounts = AccountsAPI(**api_kwargs)
