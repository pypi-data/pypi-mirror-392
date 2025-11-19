from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class CalendlyChecker(Provider):
    name = "calendly"
    description = "Validate Calendly API key"
    args = [("-k", "--key", "Calendly API key")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = "https://calendly.com/api/v1/users/me"
        headers = {"X-TOKEN": args.key}
        code, _ = http_get(url, headers=headers)
        if code == 200:
            return True, "Valid Calendly token"
        return False, f"Invalid Calendly token (status {code})"
