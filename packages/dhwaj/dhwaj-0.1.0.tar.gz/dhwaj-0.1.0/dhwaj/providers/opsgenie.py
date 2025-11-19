from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class OpsGenieChecker(Provider):
    name = "opsgenie"
    description = "Validate OpsGenie API key"
    args = [("-k", "--key", "OpsGenie API key")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = "https://api.opsgenie.com/v2/alerts"
        headers = {"Authorization": f"GenieKey {args.key}"}
        code, _ = http_get(url, headers=headers)
        if code == 200 or code == 202:
            return True, "Valid OpsGenie API key"
        return False, f"Invalid OpsGenie key (status {code})"
