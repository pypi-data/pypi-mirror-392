from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class DataDogChecker(Provider):
    name = "datadog"
    description = "Validate DataDog API key + Application key"
    args = [
        ("-k", "--api-key", "DataDog API key"),
        ("-a", "--app-key", "DataDog Application key"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = f"https://api.datadoghq.com/api/v1/dashboard?api_key={args.api_key}&application_key={args.app_key}"
        code, _ = http_get(url)
        if code == 200:
            return True, "Valid DataDog keys"
        return False, f"Invalid DataDog keys (status {code})"
