from __future__ import annotations
from typing import Tuple, Dict, Any
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_post


class FirebaseCustomTokenChecker(Provider):
    name = "firebase-custom"
    description = "Validate Firebase Custom Token + API Key"
    args = [
        ("-k", "--api_key", "Firebase API key"),
        ("-ct", "--custom_token", "Firebase custom token"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        api_key = args.api_key
        custom_token = args.custom_token

        # ------------------------------
        # Step 1: custom token -> idToken
        # ------------------------------
        url_step1 = (
            "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken"
            f"?key={api_key}"
        )

        headers = {"content-type": "application/json"}
        payload_step1: Dict[str, Any | bool] = {
            "token": custom_token,
            "returnSecureToken": True,
        }

        code1, body1 = http_post(url_step1, headers=headers, json=payload_step1)

        if code1 is None:
            return False, f"Request error: {body1}"

        if '"idToken"' not in body1:
            return (
                False,
                f"Invalid Firebase Custom Token / API Key (Step1 status {code1})",
            )

        # Extract idToken
        import json

        try:
            id_token = json.loads(body1).get("idToken")
        except Exception:
            return False, "Failed to parse idToken from response"

        if not id_token:
            return False, "Failed to extract idToken"

        # ------------------------------
        # Step 2: verify idToken
        # ------------------------------
        url_step2 = (
            "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyCustomToken"
            f"?key={api_key}"
        )

        payload_step2 = {"idToken": id_token}

        code2, body2 = http_post(url_step2, headers=headers, json=payload_step2)

        if code2 is None:
            return False, f"Request error: {body2}"

        # Valid responses contain an auth token or "valid" fields
        if '"kind"' in body2 or '"verified"' in body2.lower():
            return True, "Valid Firebase Custom Token + API Key"

        return False, f"Invalid Firebase credentials (Step2 status {code2})"
