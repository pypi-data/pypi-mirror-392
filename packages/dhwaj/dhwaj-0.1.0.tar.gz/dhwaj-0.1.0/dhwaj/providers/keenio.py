from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class KeenIOChecker(Provider):
    name = "keenio"
    description = "Validate Keen.io API key + project ID"
    args = [
        ("-k", "--key", "Keen.io Read/Write key"),
        ("-p", "--project-id", "Keen.io Project ID"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = f"https://api.keen.io/3.0/projects/{args.project_id}/events?api_key={args.key}"
        code, _ = http_get(url)
        if code == 200:
            return True, "Valid Keen.io API key"
        return False, f"Invalid Keen.io key (status {code})"
