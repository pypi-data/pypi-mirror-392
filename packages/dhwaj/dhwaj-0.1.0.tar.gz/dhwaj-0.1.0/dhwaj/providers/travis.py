from __future__ import annotations
from typing import Tuple, Dict
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class TravisChecker(Provider):
    name = "travis"
    description = "Validate Travis CI token"
    args = [("-k", "--token", "Travis CI token")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        headers: Dict[str, str] = {
            "Travis-API-Version": "3",
            "Authorization": f"token {args.token}",
        }
        url = "https://api.travis-ci.org/repos"
        code, _ = http_get(url, headers=headers)
        if code == 200:
            return True, "Valid Travis token"
        return False, f"Invalid Travis token (status {code})"
