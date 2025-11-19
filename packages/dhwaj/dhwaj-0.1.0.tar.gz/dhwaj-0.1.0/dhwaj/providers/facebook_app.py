from __future__ import annotations
from typing import Tuple
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get


class FacebookAppSecretChecker(Provider):
    name = "facebook-appsecret"
    description = "Validate Facebook App ID + App Secret"
    args = [
        ("-cid", "--client_id", "Facebook App ID"),
        ("-cs", "--client_secret", "Facebook App Secret"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        client_id = args.client_id
        client_secret = args.client_secret

        url = (
            "https://graph.facebook.com/oauth/access_token"
            f"?client_id={client_id}"
            f"&client_secret={client_secret}"
            "&redirect_uri="
            "&grant_type=client_credentials"
        )

        code, body = http_get(url)

        if code is None:
            return False, f"Request error: {body}"

        # Facebook returns: {"access_token":"XYZ","token_type":"bearer"}
        if '"access_token"' in body:
            return True, "Valid Facebook AppSecret"

        # Invalid example: {"error":{"message":"Error validating client secret",...}}
        return False, f"Invalid AppSecret (status {code})"
