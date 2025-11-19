from __future__ import annotations
from typing import Tuple, Dict, Any
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_post


class AzureTenantChecker(Provider):
    name: str = "azure-tenant"
    description: str = "Validate Azure AD Client ID / Client Secret / Tenant ID"
    args = [
        ("-cid", "--client-id", "Azure Client ID"),
        ("-cs", "--client-secret", "Azure Client Secret"),
        ("-t", "--tenant-id", "Azure Tenant ID"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        url = f"https://login.microsoftonline.com/{args.tenant_id}/oauth2/v2.0/token"

        headers: Dict[str, str] = {"Content-Type": "application/x-www-form-urlencoded"}

        # Typed + correct payload
        data: Dict[str, Any] = {
            "client_id": args.client_id,
            "scope": "https://graph.microsoft.com/.default",
            "client_secret": args.client_secret,
            "grant_type": "client_credentials",
        }

        code, body = http_post(url, headers=headers, data=data)

        if code == 200 and '"access_token"' in (body or ""):
            return True, "Valid Azure Tenant credentials"

        return False, f"Invalid Azure credentials (status {code})"
