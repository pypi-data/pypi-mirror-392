from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class LoqateChecker(Provider):
    name = "loqate"
    description = "Validate Loqate API key"
    args = [("-k", "--key", "Loqate API key")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = f"http://api.addressy.com/Capture/Interactive/Find/v1.00/json3.ws?Key={args.key}&Countries=US,CA&Language=en&Limit=1&Text=BHAR"
        code, body = http_get(url)
        if code == 200 and '"Error"' not in body:
            return True, "Valid Loqate API key"
        return False, f"Invalid Loqate key (status {code})"
