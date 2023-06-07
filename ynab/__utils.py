# Copyright (c) 2021 Erik Zwiefel
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from requests import Response
from requests.exceptions import HTTPError


def raise_exceptions(resp: Response) -> None:
    if resp.status_code != 200:
        raise HTTPError(resp.text)
