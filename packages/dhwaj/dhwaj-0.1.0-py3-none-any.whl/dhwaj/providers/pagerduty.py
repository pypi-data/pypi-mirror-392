from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class PagerDutyChecker(Provider):
    name = "pagerduty"
    description = "Validate PagerDuty API token"
    args = [("-k", "--key", "PagerDuty API token")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = "https://api.pagerduty.com/schedules"
        headers = {
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Authorization": f"Token token={args.key}",
        }
        code, _ = http_get(url, headers=headers)
        if code == 200:
            return True, "Valid PagerDuty API token"
        return False, f"Invalid PagerDuty token (status {code})"
