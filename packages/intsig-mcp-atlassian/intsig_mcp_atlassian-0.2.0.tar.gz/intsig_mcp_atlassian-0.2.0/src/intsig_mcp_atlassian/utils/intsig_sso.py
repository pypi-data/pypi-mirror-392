"""INTSIG SSO support utilities.

This module provides:
- Password encryption required by INTSIG SSO
- SSO login flow to obtain `zerotrust-sso-token` cookie
- Helper to ensure `JSESSIONID` is established
- A response hook to auto re-auth on 401/403
"""

from __future__ import annotations

import base64
import binascii
import logging
from typing import Callable, Optional
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

logger = logging.getLogger("mcp-atlassian")


INTSIG_AES_KEY = b"UuTpos6bqTmfTYoM"  # 16-byte key


def encrypt_password(plaintext: str) -> str:
    """Encrypt password with AES-ECB + PKCS7 and return hex string.

    Args:
        plaintext: Raw password string

    Returns:
        Hex-encoded ciphertext string
    """
    cipher = AES.new(INTSIG_AES_KEY, AES.MODE_ECB)
    padded = pad(plaintext.encode("utf-8"), AES.block_size)
    ciphertext = cipher.encrypt(padded)
    return binascii.hexlify(ciphertext).decode("utf-8")


def _extract_redirect_and_platform_id(redirect_location: str) -> tuple[Optional[str], Optional[str]]:
    """Extract `redirect` URL and `platform_id` from first redirect location.

    Returns (redirect_url, platform_id) which can be None if not found.
    """
    try:
        parsed = urlparse(redirect_location)
        qs = parse_qs(parsed.query)
        platform_ids = qs.get("platform_id")
        redirect_values = qs.get("redirect")
        platform_id = platform_ids[0] if platform_ids else None
        redirect_url = redirect_values[0] if redirect_values else None
        return redirect_url, platform_id
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug(f"Failed to parse redirect location: {exc}")
        return None, None


def _append_token_to_url(url: str, token: str) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query["token"] = [token]
    new_query = urlencode({k: v[0] if isinstance(v, list) else v for k, v in query.items()})
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))


def perform_sso_login(
    session: requests.Session,
    base_url: str,
    username: str,
    password: str,
    *,
    ssl_verify: bool = True,
) -> None:
    """Execute INTSIG SSO dance and set cookies on the provided session.

    Flow:
    1) GET base_url to receive redirect with platform_id and redirect url
    2) POST login with encrypted password to obtain token and platform url
    3) Visit zerotrust redirect with token to receive `zerotrust-sso-token` cookie
    4) Touch base_url once to establish `JSESSIONID`
    """
    # Step 1: initial redirect
    resp = session.get(base_url, allow_redirects=False, verify=ssl_verify)
    location = resp.headers.get("Location") or resp.headers.get("location")
    if not location:
        # follow redirects once to try to capture final location
        follow = session.get(base_url, allow_redirects=True, verify=ssl_verify)
        location = getattr(follow, "history", [])[-1].headers.get("Location") if getattr(follow, "history", []) else None
        if not location:
            raise RuntimeError("INTSIG SSO: initial redirect location not found")

    redirect_url, platform_id = _extract_redirect_and_platform_id(location)
    if not platform_id or not redirect_url:
        raise RuntimeError("INTSIG SSO: platform_id or redirect url not found in redirect")

    # Step 2: login to obtain token
    enc_pwd = encrypt_password(password)
    login_body = {"email": username, "password": enc_pwd, "platform_id": platform_id}
    login_resp = session.post(
        "https://webapi-sso2.intsig.net/auth/login",
        json=login_body,
        verify=ssl_verify,
    )
    login_resp.raise_for_status()
    data = login_resp.json().get("data", {})
    token = data.get("token")
    if not token:
        raise RuntimeError("INTSIG SSO: token not returned from login API")

    # Step 3: visit zerotrust redirect with token to set zerotrust cookie
    with_token_url = _append_token_to_url(redirect_url, token)
    zr_resp = session.get(with_token_url, allow_redirects=True, verify=ssl_verify)
    # Expect cookie set
    if not any(c.name == "zerotrust-sso-token" for c in session.cookies):
        logger.warning("INTSIG SSO: zerotrust-sso-token cookie not found after redirect")

    # Step 4: establish JSESSIONID by touching base_url
    session.get(base_url, allow_redirects=True, verify=ssl_verify)


def set_basic_auth_header(session: requests.Session, username: str, password: str) -> None:
    creds = f"{username}:{password}".encode("utf-8")
    b64 = base64.b64encode(creds).decode("utf-8")
    session.headers["Authorization"] = f"Basic {b64}"


def wrap_session_with_reauth(
    session: requests.Session,
    base_url: str,
    username: str,
    password: str,
    *,
    ssl_verify: bool = True,
) -> None:
    """Monkey-patch session.request to auto re-auth on 401/403 once.

    This preserves semantics for callers of the session while providing transparent
    re-auth when cookies expire.
    """
    original_request = session.request

    def _request(method: str, url: str, *args, **kwargs):  # type: ignore[override]
        retried = kwargs.pop("_intsig_sso_retried", False)
        response = original_request(method, url, *args, **kwargs)
        if response is not None and response.status_code in (401, 403) and not retried:
            try:
                logger.info("INTSIG SSO: 401/403 detected, re-authenticating and retrying")
                perform_sso_login(session, base_url, username, password, ssl_verify=ssl_verify)
                # retry once
                kwargs["_intsig_sso_retried"] = True
                return original_request(method, url, *args, **kwargs)
            except Exception as exc:  # pragma: no cover - defensive
                logger.debug(f"INTSIG SSO re-auth failed: {exc}")
        return response

    session.request = _request  # type: ignore[assignment]


