from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class InstagramGraphChecker(Provider):
    name = "instagram-graph"
    description = "Validate Instagram Graph API access token"
    args = [("-t", "--token", "Instagram Graph access token")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = f"https://graph.facebook.com/v8.0/me/accounts?access_token={args.token}"
        code, body = http_get(url)
        if code == 200 and '"data"' in body:
            return True, "Valid Instagram Graph token"
        return False, f"Invalid Instagram Graph token (status {code})"
