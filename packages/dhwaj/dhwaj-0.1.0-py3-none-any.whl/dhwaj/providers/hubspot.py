from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class HubSpotAPIKeyChecker(Provider):
    name: str = "hubspot"
    description: str = "Validate HubSpot API key"
    args = [
        ("-k", "--key", "HubSpot API key"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        key = args.key

        endpoints = [
            f"https://api.hubapi.com/owners/v2/owners?hapikey={key}",
            f"https://api.hubapi.com/contacts/v1/lists/all/contacts/all?hapikey={key}",
        ]

        for url in endpoints:
            code, body = http_get(url)

            if code is None:
                return False, f"Request error: {body}"

            # Valid HubSpot responses
            if code == 200:
                if "ownerId" in body or "contacts" in body.lower():
                    return True, "Valid HubSpot API Key"

            # Invalid key format or HubSpot error JSON
            if code in (401, 403):
                return False, f"Invalid HubSpot API key (status {code})"

        return False, "Invalid or unrecognized HubSpot API key"
