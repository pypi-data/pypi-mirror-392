from __future__ import annotations
from typing import Tuple
from argparse import Namespace

from .base import Provider
from dhwaj.utils.http import http_get


class PivotalChecker(Provider):
    name: str = "razorpay"
    description = "Validate Razorpay key ID and secret"
    args = [
        ("-id", "--key-id", "Razorpay key ID"),
        ("-s", "--secret", "Razorpay secret key"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = "https://www.pivotaltracker.com/services/v5/me?fields=%3Adefault"
        headers = {"X-TrackerToken": args.token}
        code, _ = http_get(url, headers=headers)
        if code == 200:
            return True, "Valid PivotalTracker API token"
        return False, f"Invalid Pivotal token (status {code})"
