from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class NewRelicRESTChecker(Provider):
    name = "newrelic-rest"
    description = "Validate New Relic REST API key"
    args = [("-k", "--key", "New Relic REST API key")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = "https://api.newrelic.com/v2/applications.json"
        headers = {"X-Api-Key": args.key}
        code, _ = http_get(url, headers=headers)
        if code == 200:
            return True, "Valid New Relic REST key"
        return False, f"Invalid New Relic REST key (status {code})"
