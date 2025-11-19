from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class IpstackChecker(Provider):
    name = "ipstack"
    description = "Validate Ipstack API key"
    args = [("-k", "--key", "Ipstack API key")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = f"https://api.ipstack.com/8.8.8.8?access_key={args.key}"
        code, body = http_get(url)
        if code == 200 and '"ip"' in body:
            return True, "Valid Ipstack API key"
        return False, f"Invalid Ipstack key (status {code})"
