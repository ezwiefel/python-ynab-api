# Copyright (c) 2021 Erik Zwiefel
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from dataclasses import dataclass, field
from typing import Optional

from ynab.__base import RESTBase


@dataclass
class Category:
    id: Optional[str] = None
    name: Optional[str] = None
    hidden: Optional[bool] = None
    deleted: Optional[bool] = None
    category_group_id: Optional[str] = None
    category_group_name: Optional[str] = None

    meta: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict, category_name: Optional[str] = None):
        known_args = {}
        unknown_args = {}

        for key, value in data.items():
            if key in cls.__annotations__:
                known_args[key] = value
            else:
                unknown_args[key] = value

        return cls(**known_args, category_group_name=category_name, meta=unknown_args)

    def __repr__(self):
        return (
            f"Category("
            f"name='{self.name}', "
            f"group='{self.category_group_name}'"
            f")"
        )


class CategoriesAPI(RESTBase):
    def __init__(self, budget_id: str, **kwargs):
        super().__init__(**kwargs)
        self._budget_id = budget_id
        self._budget_uri = f"/budgets/{budget_id}/"

    @staticmethod
    def __load_categories_from_json(data: dict):
        ret_list = []
        for group in data["data"]["category_groups"]:
            ret_list.extend(
                [
                    Category.from_dict(c, category_name=group["name"])
                    for c in group["categories"]
                ]
            )

        return ret_list

    def get_all(self):
        method = "GET"
        api_path = self._budget_uri + f"categories/"

        resp = self._rest_call[method](api_path)

        return self.__load_categories_from_json(resp.json())

    def get_by_name(self, name: str):
        all_categories = self.get_all()

        for c in all_categories:
            if c.name == name:
                ret_val = c
                break
        else:
            ret_val = None

        return ret_val
