from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class LokaliseChecker(Provider):
    name = "lokalise"
    description = "Validate Lokalise API token"
    args = [("-k", "--key", "Lokalise API token")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = "https://api.lokalise.com/api2/projects/"
        headers = {"x-api-token": args.key}
        code, _ = http_get(url, headers=headers)
        if code == 200:
            return True, "Valid Lokalise API key"
        return False, f"Invalid Lokalise API key (status {code})"
