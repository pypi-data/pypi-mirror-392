from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class AmplitudeChecker(Provider):
    name = "amplitude"
    description = "Validate Amplitude API Key + Secret Key"
    args = [
        ("-k", "--key", "Amplitude API Key"),
        ("-s", "--secret", "Amplitude Secret Key"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = "https://amplitude.com/api/2/export?start=20200101T00&end=20200102T00"
        # use HTTP basic with key:secret
        # http_get can't do basic easily - add Authorization header
        import base64

        auth = base64.b64encode(f"{args.key}:{args.secret}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}"}
        code, _ = http_get(url, headers=headers)
        if code == 200:
            return True, "Valid Amplitude credentials"
        return False, f"Invalid Amplitude credentials (status {code})"
