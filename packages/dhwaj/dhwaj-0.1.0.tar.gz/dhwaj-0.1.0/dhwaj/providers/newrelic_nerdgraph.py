from __future__ import annotations
from typing import Tuple, Dict, Any
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_post


class NewRelicNerdGraphChecker(Provider):
    name = "newrelic-nerd"
    description = "Validate New Relic Personal API key (NerdGraph)"
    args = [("-k", "--key", "New Relic personal API key")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = "https://api.newrelic.com/graphql"
        headers: Dict[str, Any] = {
            "Content-Type": "application/json",
            "API-Key": args.key,
        }
        payload = {"query": "{ actor { user { id } } }"}
        code, body = http_post(url, headers=headers, json=payload)
        if code == 200 and ("errors" not in (body or "").lower()):
            return True, "Valid New Relic NerdGraph API key"
        return False, f"Invalid New Relic key (status {code})"
