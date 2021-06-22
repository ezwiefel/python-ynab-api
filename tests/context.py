# Copyright (c) 2021 Erik Zwiefel
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dataclasses import dataclass

import pytest
from environs import Env

import ynab


@dataclass
class Environment:
    token: str
    budget_id: str
    account: str


@pytest.fixture()
def ynab_env() -> Environment:
    """
    Get environment
    :return: Named Tuple Environment
    """
    env = Env()
    env.read_env(os.path.abspath(os.path.join(os.path.dirname(__file__), 'test-settings.env')))

    return Environment(
        token=env.str("YNAB_PAT"),
        budget_id=env.str('TEST_BUDGET_ID'),
        account=env.str('ACCOUNT_NAME')
    )