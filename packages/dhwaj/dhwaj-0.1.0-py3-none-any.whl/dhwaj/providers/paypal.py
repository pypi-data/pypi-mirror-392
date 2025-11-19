from __future__ import annotations
from typing import Tuple, Dict, Any
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_post
import base64


class PaypalChecker(Provider):
    name: str = "paypal"
    description: str = "Validate PayPal client ID + secret (sandbox optional)"
    args = [
        ("-cid", "--client-id", "PayPal client ID"),
        ("-cs", "--client-secret", "PayPal client secret"),
        ("--sandbox", "--sandbox", "Use PayPal sandbox environment"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        host = "api.sandbox.paypal.com" if args.sandbox else "api.paypal.com"
        url = f"https://{host}/v1/oauth2/token"

        auth = base64.b64encode(
            f"{args.client_id}:{args.client_secret}".encode()
        ).decode()

        headers: Dict[str, str] = {
            "Accept": "application/json",
            "Accept-Language": "en_US",
            "Authorization": f"Basic {auth}",
        }

        data: Dict[str, Any] = {"grant_type": "client_credentials"}

        code, body = http_post(url, headers=headers, data=data)

        if code == 200 and '"access_token"' in (body or ""):
            return True, "Valid PayPal client_id+secret"

        return False, f"Invalid PayPal credentials (status {code})"
