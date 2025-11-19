from __future__ import annotations
from typing import Tuple, Dict, Any
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_post


class InfuraChecker(Provider):
    name = "infura"
    description = "Validate Infura project ID (API key)"
    args = [("-k", "--key", "Infura project ID")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        api_key = args.key

        url = f"https://mainnet.infura.io/v3/{api_key}"

        headers = {"Content-Type": "application/json"}

        payload: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": "eth_accounts",
            "params": [],
            "id": 1,
        }

        code, body = http_post(url, headers=headers, json=payload)

        if code is None:
            return False, f"Request error: {body}"

        # Valid response example:
        # {"jsonrpc":"2.0","id":1,"result":[]}
        if code == 200 and '"result"' in body:
            return True, "Valid Infura API Key"

        # Invalid example:
        # {"error":{"code":-32601,"message":"The method eth_accounts does not exist/is not available"}}
        # Still counts as valid, because Infura processed the request using a valid key.
        if code == 200 and '"error"' in body.lower():
            return True, "Valid Infura API Key (method not allowed, but key accepted)"

        # Invalid key returns 401 or 403:
        # {"error":"project ID does not exist"}
        if code in [401, 403] or "project id" in body.lower():
            return False, "Invalid Infura API Key"

        return False, f"Unknown response (status {code})"
