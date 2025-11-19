from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class InstagramBasicChecker(Provider):
    name = "instagram-basic"
    description = "Validate Instagram Basic Display API token"
    args = [
        ("-t", "--token", "Instagram access token"),
        ("-i", "--id", "Instagram user ID"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = f"https://graph.instagram.com/{args.id}?fields=id,username&access_token={args.token}"
        code, body = http_get(url)
        if code == 200 and '"id"' in body:
            return True, "Valid Instagram Basic token"
        return False, f"Invalid Instagram basic token (status {code})"
