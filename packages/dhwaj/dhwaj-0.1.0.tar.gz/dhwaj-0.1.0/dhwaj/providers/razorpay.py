from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get
import base64


class RazorpayChecker(Provider):
    name = "razorpay"
    description = "Validate Razorpay key ID and secret"
    args = [
        ("-id", "--key-id", "Razorpay key ID"),
        ("-s", "--secret", "Razorpay secret key"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        auth = base64.b64encode(f"{args.key_id}:{args.secret}".encode()).decode()
        headers = {"Authorization": f"Basic {auth}"}
        url = "https://api.razorpay.com/v1/payments"
        code, _ = http_get(url, headers=headers)
        if code == 200:
            return True, "Valid Razorpay credentials"
        return False, f"Invalid Razorpay credentials (status {code})"
