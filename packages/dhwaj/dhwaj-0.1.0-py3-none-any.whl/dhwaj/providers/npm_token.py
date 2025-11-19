from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class NpmChecker(Provider):
    name = "npm"
    description = "Validate NPM token"
    args = [("-t", "--token", "NPM auth token")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = "https://registry.npmjs.org/-/whoami"
        headers = {"authorization": f"Bearer {args.token}"}
        code, _ = http_get(url, headers=headers)
        if code == 200:
            return True, "Valid NPM token (whoami)"
        if code == 401:
            return False, "Unauthorized (invalid NPM token)"
        return False, f"Unknown response (status {code})"
