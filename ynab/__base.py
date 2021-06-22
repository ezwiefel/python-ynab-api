# Copyright (c) 2021 Erik Zwiefel
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import requests


class RESTBase(object):

    def __init__(self, **kwargs):
        self._host = kwargs.pop('host')
        self._api_version = kwargs.pop('api_version')
        self._uri = f"{self._host}/{self._api_version}/"
        self._token = kwargs.pop('token')
        self.parent = kwargs.get('parent', None)
        self._headers = {'Authorization': f'Bearer {self._token}'}
        self._rest_call = {'GET': self.__get,
                           'POST': self.__post,
                           'PATCH': self.__patch,
                           'PUT': self.__put}

    def __get(self, api_endpoint: str, params: dict = None) -> requests.Response:
        """
        Send HTTP GET request to REST API endpoint with data as query string
        :param api_endpoint: string : The api endpoint to be called - after version number
        :param data: dict : Data to be passed as query string in url
        :return: Partial function requests.get with URL populated
        """

        uri = self.__prep_uri(api_endpoint)
        resp = requests.get(url=uri, params=params, headers=self._headers)
        self.__check_for_errors(resp)

        return resp

    def __post(self, api_endpoint: str, data: dict) -> requests.Response:
        """
        Send HTTP POST request to REST API endpoint with data as JSON object
        :param api_endpoint:
        :param data:
        :return:
        """

        uri = self.__prep_uri(api_endpoint)

        resp = requests.post(url=uri, headers=self.json_header, json=data)

        self.__check_for_errors(resp)

        return resp

    def __patch(self, api_endpoint: str, data: dict) -> requests.Response:
        """
        Send HTTP POST request to REST API endpoint with data as JSON object
        :param api_endpoint:
        :param data:
        :return:
        """
        uri = self.__prep_uri(api_endpoint)

        resp = requests.patch(url=uri, headers=self.json_header, json=data)
        self.__check_for_errors(resp)

        return resp

    def __put(self, api_endpoint: str, data: dict) -> requests.Response:
        """
        Send HTTP POST request to REST API endpoint with data as JSON object
        :param api_endpoint:
        :param data:
        :return:
        """
        uri = self.__prep_uri(api_endpoint)

        resp = requests.put(url=uri, headers=self.json_header, json=data)
        self.__check_for_errors(resp)

        return resp

    def __prep_uri(self, api_endpoint: str) -> str:
        # Check that API_endpoint does not start with a '/', if so, remove it.
        # Because self.uri already contains the necessary '/'
        if api_endpoint.startswith("/"):
            api_endpoint = api_endpoint[1:]

        return self._uri + api_endpoint

    @property
    def json_header(self):
        header = self._headers
        header["Content-Type"] = "application/json"
        return header

    @staticmethod
    def __check_for_errors(resp: requests.Response):
        if resp.status_code not in [200, 201, 202, 204]:
            raise requests.exceptions.HTTPError(resp.text)
