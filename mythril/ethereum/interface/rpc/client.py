"""This module contains a basic Ethereum RPC client.

This code is adapted from: https://github.com/ConsenSys/ethjsonrpc
"""

import json
import logging

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError as RequestsConnectionError

from .base_client import BaseClient
from .exceptions import (
    BadJsonError,
    BadResponseError,
    BadStatusCodeError,
    ConnectionError,
)

log = logging.getLogger(__name__)

GETH_DEFAULT_RPC_PORT = 8545
ETH_DEFAULT_RPC_PORT = 8545
PARITY_DEFAULT_RPC_PORT = 8545
PYETHAPP_DEFAULT_RPC_PORT = 4000
MAX_RETRIES = 3
JSON_MEDIA_TYPE = "application/json"


class EthJsonRpc(BaseClient):
    """Ethereum JSON-RPC client class."""

    def __init__(self, host="localhost", port=GETH_DEFAULT_RPC_PORT, tls=False):
        """

        :param host:
        :param port:
        :param tls:
        """
        self.host = host
        self.port = port
        self.tls = tls
        self.session = requests.Session()
        self.session.mount(self.host, HTTPAdapter(max_retries=MAX_RETRIES))

    def _call(self, method, params=None, _id=1):
        """

        :param method:
        :param params:
        :param _id:
        :return:
        """
        params = params or []
        data = {"jsonrpc": "2.0", "method": method, "params": params, "id": _id}
        scheme = "http"
        if self.tls:
            scheme += "s"
        if self.host:
            if self.port:
                url = "{}://{}:{}".format(scheme, self.host, self.port)
            else:
                url = "{}://{}".format(scheme, self.host)

        else:
            url = "{}".format(scheme)

        headers = {"Content-Type": JSON_MEDIA_TYPE}
        log.debug("rpc send: %s" % json.dumps(data))
        try:
            r = self.session.post(url, headers=headers, data=json.dumps(data))
        except RequestsConnectionError:
            raise ConnectionError
        if r.status_code / 100 != 2:
            raise BadStatusCodeError(r.status_code)
        try:
            response = r.json()
            log.debug("rpc response: %s" % response)
        except ValueError:
            raise BadJsonError(r.text)
        try:
            return response["result"]
        except KeyError:
            raise BadResponseError(response)

    def close(self):
        """Close the RPC client's session."""
        self.session.close()
