from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class IterableChecker(Provider):
    name = "iterable"
    description = "Validate Iterable API key"
    args = [("-k", "--key", "Iterable API key")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = "https://api.iterable.com/api/export/data.json?dataTypeName=emailSend&range=Today&onlyFields=List.empty"
        headers = {"Api_Key": args.key}
        code, _ = http_get(url, headers=headers)
        if code == 200:
            return True, "Valid Iterable API key"
        return False, f"Invalid Iterable key (status {code})"
