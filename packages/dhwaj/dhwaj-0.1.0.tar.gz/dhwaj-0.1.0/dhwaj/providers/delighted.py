from .base import Provider
from typing import Tuple
from argparse import Namespace
from dhwaj.utils.http import http_get
import base64


class DelightedChecker(Provider):
    name = "delighted"
    description = "Validate Delighted API key"
    args = [("-k", "--key", "Delighted API key")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        auth = base64.b64encode(f"{args.key}:".encode()).decode()
        headers = {"Authorization": f"Basic {auth}"}
        url = "https://api.delighted.com/v1/metrics.json"
        code, _ = http_get(url, headers=headers)
        if code == 200:
            return True, "Valid Delighted API key"
        return False, f"Invalid Delighted key (status {code})"
