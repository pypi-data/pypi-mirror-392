from __future__ import annotations

import requests
import urllib3
from typing import Dict, Optional, Tuple, Any

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HttpResponse = Tuple[Optional[int], str]


def http_get(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, str]] = None,
) -> HttpResponse:
    """Send a GET request and return (status_code, body) or (None, error)."""

    try:
        r = requests.get(url, headers=headers, params=params, timeout=10, verify=False)
        return r.status_code, r.text
    except Exception as e:
        return None, str(e)


def http_post(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
) -> HttpResponse:
    """Send a POST request and return (status_code, body) or (None, error)."""

    try:
        r = requests.post(
            url, headers=headers, json=json, data=data, timeout=10, verify=False
        )
        return r.status_code, r.text
    except Exception as e:
        return None, str(e)
