from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class SalesforceChecker(Provider):
    name = "salesforce"
    description = "Validate Salesforce access token"
    args = [
        ("-k", "--access-token", "Salesforce access token"),
        ("-i", "--instance", "Salesforce instance domain"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        instance = args.instance or "instance_name"
        url = f"https://{instance}.salesforce.com/services/data/v20.0/"
        headers = {"Authorization": f"Bearer {args.access_token}"}
        code, _ = http_get(url, headers=headers)
        if code == 200:
            return True, "Valid Salesforce Access Token"
        return False, f"Invalid Salesforce token (status {code})"
