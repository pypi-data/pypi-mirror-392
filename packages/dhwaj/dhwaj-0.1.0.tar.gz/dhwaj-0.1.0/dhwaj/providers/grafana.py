from __future__ import annotations
from typing import Tuple, Dict, Optional
from argparse import Namespace
from .base import Provider
from dhwaj.utils.http import http_get
import base64


class GrafanaChecker(Provider):
    name = "grafana"
    description = "Validate Grafana API key or Basic Auth credentials"
    args = [
        ("-u", "--url", "Grafana base URL"),
        ("-k", "--key", "Grafana API key (Bearer)"),
        ("--basic", "--basic", "Enable Basic Auth mode"),
        ("--userpass", "--userpass", "Basic auth as 'user:pass'"),
    ]

    def run(self, args: Namespace) -> Tuple[bool, str]:
        if not args.url:
            return False, "Grafana base URL required"

        headers: Dict[str, str] = {}
        code: Optional[int]

        # Case 1: API key
        if args.key:
            headers["Authorization"] = f"Bearer {args.key}"
            code, _ = http_get(f"{args.url}/api/user", headers=headers)

        # Case 2: Basic Auth mode
        elif args.userpass:
            auth = base64.b64encode(args.userpass.encode()).decode()
            headers["Authorization"] = f"Basic {auth}"
            code, _ = http_get(f"{args.url}/api/user", headers=headers)

        else:
            return False, "Provide -k API key OR --userpass user:pass"

        # Success check
        if code == 200:
            return True, "Valid Grafana credentials"

        return False, f"Invalid Grafana credentials (status {code})"
