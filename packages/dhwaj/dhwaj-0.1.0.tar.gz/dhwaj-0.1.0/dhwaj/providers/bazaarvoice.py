from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class BazaarvoiceChecker(Provider):
    name = "bazaarvoice"
    description = "Validate Bazaarvoice Conversations Passkey"
    args = [("-k", "--passkey", "Bazaarvoice Passkey")]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = f"https://which-cpv-api.bazaarvoice.com/clientInfo?conversationspasskey={args.passkey}"
        code, body = http_get(url)
        if code == 200 and '"company"' in (body or "").lower():
            return True, "Valid Bazaarvoice passkey"
        return False, f"Invalid Bazaarvoice passkey (status {code})"
