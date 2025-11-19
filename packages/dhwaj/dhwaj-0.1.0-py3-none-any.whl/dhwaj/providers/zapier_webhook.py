from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_post


class ZapierWebhookChecker(Provider):
    name = "zapier-webhook"
    description = "Validate Zapier Webhook URL"
    args = [("-u", "--url", "Zapier Webhook URL")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        code, _ = http_post(
            args.url,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            json={"name": "streaak"},
        )
        if code and code in (200, 201, 202):
            return True, "Zapier webhook reachable"
        return False, f"Invalid webhook (status {code})"
