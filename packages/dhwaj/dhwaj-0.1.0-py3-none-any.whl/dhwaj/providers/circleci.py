from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class CircleCIChecker(Provider):
    name = "circleci"
    description = "Validate CircleCI API token"
    args = [("-k", "--token", "CircleCI API token")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = f"https://circleci.com/api/v1.1/me?circle-token={args.token}"
        code, _ = http_get(url)
        if code == 200:
            return True, "Valid CircleCI token"
        return False, f"Invalid CircleCI token (status {code})"
