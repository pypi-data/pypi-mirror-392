"""
License and API key handling for ezib-mcp.

This module validates an API key (license token) and enforces simple
per-installation usage limits for MCP tools.

Design:
  - The API key is provided via the EZIB_MCP_KEY environment variable.
  - The key format is: base64url(payload) + "." + base64url(signature)
  - The payload is a JSON document that includes edition, validity window
    and optional rate limits and feature flags.
  - The signature is created with a private Ed25519 key; this module only
    needs the corresponding public key to verify it.

This implementation is intentionally minimal and file-based. For a production
system you would typically also keep usage stats in a database or add more
granular limits.
"""

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from datetime import datetime, date, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


# IMPORTANT:
#   - Replace this placeholder with your real Ed25519 public key in base64.
#   - The matching private key must be kept offline and only used by your
#     own license/key generation tooling.
PUBLIC_KEY_B64 = os.getenv("EZIB_MCP_PUBLIC_KEY_B64", "")


class LicenseError(Exception):
    """Raised when the API key is missing, invalid, or limits are exceeded."""


@dataclass
class RateLimit:
    max_calls_per_day: Optional[int] = None
    max_calls_total: Optional[int] = None


@dataclass
class LicenseInfo:
    product: str
    edition: str
    customer: str
    not_before: datetime
    expires_at: datetime
    rate_limit: RateLimit
    features: Dict[str, Dict[str, Any]]


class LicenseManager:
    """Validates and exposes information from the API key payload."""

    def __init__(self, info: LicenseInfo):
        self.info = info

    @staticmethod
    def _decode_key_parts(key: str) -> tuple[bytes, bytes]:
        try:
            payload_b64, sig_b64 = key.split(".")
        except ValueError:
            raise LicenseError("Invalid API key format") from None

        def b64url_decode(data: str) -> bytes:
            # Add padding if needed for base64.urlsafe_b64decode
            padding = "=" * (-len(data) % 4)
            return base64.urlsafe_b64decode(data + padding)

        payload_bytes = b64url_decode(payload_b64)
        sig_bytes = b64url_decode(sig_b64)
        return payload_bytes, sig_bytes

    @classmethod
    def from_env(cls, env_name: str = "EZIB_MCP_KEY") -> "LicenseManager":
        key = os.getenv(env_name)
        if not key:
            raise LicenseError(f"{env_name} is not set")

        if not PUBLIC_KEY_B64:
            raise LicenseError("EZIB_MCP_PUBLIC_KEY_B64 is not configured")

        payload_bytes, sig_bytes = cls._decode_key_parts(key)

        # Verify signature with Ed25519 public key
        public_key_bytes = base64.b64decode(PUBLIC_KEY_B64)
        public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
        public_key.verify(sig_bytes, payload_bytes)

        data = json.loads(payload_bytes)

        # Basic required fields
        product = data.get("product", "")
        if product != "ezib-mcp":
            raise LicenseError("API key product mismatch")

        edition = data.get("edition", "unknown")
        customer = data.get("customer", "unknown")

        nb_raw = data.get("not_before")
        exp_raw = data.get("expires_at")
        if not nb_raw or not exp_raw:
            raise LicenseError("API key missing validity window")

        def parse_dt(value: str) -> datetime:
            # Accept ISO8601 with or without trailing Z
            return datetime.fromisoformat(value.replace("Z", "+00:00"))

        nb = parse_dt(nb_raw)
        exp = parse_dt(exp_raw)

        now = datetime.now(timezone.utc)
        if now < nb:
            raise LicenseError("API key not yet valid")
        if now > exp:
            raise LicenseError("API key has expired")

        rl_data = data.get("rate_limit", {})
        rate_limit = RateLimit(
            max_calls_per_day=rl_data.get("max_calls_per_day"),
            max_calls_total=rl_data.get("max_calls_total"),
        )

        features = data.get("features", {})
        if not isinstance(features, dict):
            features = {}

        info = LicenseInfo(
            product=product,
            edition=edition,
            customer=customer,
            not_before=nb,
            expires_at=exp,
            rate_limit=rate_limit,
            features=features,
        )
        return cls(info)

    def has_feature(self, feature: str) -> bool:
        """Check whether a feature is enabled in the API key."""
        feat = self.info.features.get(feature)
        if not isinstance(feat, dict):
            return False
        enabled = feat.get("enabled", True)
        return bool(enabled)


class UsageTracker:
    """
    Simple file-based usage tracker.

    Tracks per-day and total call counts for the current installation. This is
    intentionally minimal and only meant to make bypassing limits non-trivial
    for casual users.
    """

    def __init__(self, license_info: LicenseInfo, path: Optional[Path] = None):
        self.license_info = license_info
        if path is None:
            # Default usage file under the user's home directory
            path = Path.home() / ".ezib_mcp_usage.json"
        self.path = path
        self._data: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text())
            except Exception:
                self._data = {}
        if "date" not in self._data:
            self._data = {
                "date": None,
                "total_calls_today": 0,
                "total_calls": 0,
                "by_feature": {},
            }

    def _save(self) -> None:
        try:
            self.path.write_text(json.dumps(self._data))
        except Exception:
            # In case of filesystem errors, do not crash the server;
            # just keep counters in memory.
            pass

    def _reset_if_new_day(self) -> None:
        today = date.today().isoformat()
        if self._data.get("date") != today:
            self._data["date"] = today
            self._data["total_calls_today"] = 0
            self._data["by_feature"] = {}

    def check_and_increment(self, feature: Optional[str] = None) -> None:
        """Check limits for the given feature and increment counters."""
        self._reset_if_new_day()
        rl = self.license_info.rate_limit

        total_today = int(self._data.get("total_calls_today", 0))
        total_all = int(self._data.get("total_calls", 0))

        if rl.max_calls_per_day is not None and total_today >= rl.max_calls_per_day:
            raise LicenseError("Daily call limit exceeded")

        if rl.max_calls_total is not None and total_all >= rl.max_calls_total:
            raise LicenseError("Total call limit exceeded")

        if feature:
            by_feature = self._data.setdefault("by_feature", {})
            feat_data = by_feature.setdefault(
                feature, {"today": 0, "total": 0}
            )
            feat_today = int(feat_data.get("today", 0))
            feat_limit = self.license_info.features.get(feature, {})
            max_feat_daily = feat_limit.get("max_calls_per_day")

            if (
                max_feat_daily is not None
                and feat_today >= int(max_feat_daily)
            ):
                raise LicenseError(
                    f"Daily call limit exceeded for feature '{feature}'"
                )

            feat_data["today"] = feat_today + 1
            feat_data["total"] = int(feat_data.get("total", 0)) + 1

        # Update global counters
        self._data["total_calls_today"] = total_today + 1
        self._data["total_calls"] = total_all + 1
        self._save()


# Global singletons, initialized lazily on first tool call.
_license_manager: Optional[LicenseManager] = None
_usage_tracker: Optional[UsageTracker] = None


def get_license_manager() -> LicenseManager:
    """Return the global LicenseManager, creating it from the environment if needed."""
    global _license_manager
    if _license_manager is None:
        _license_manager = LicenseManager.from_env()
    return _license_manager


def get_usage_tracker() -> UsageTracker:
    """Return the global UsageTracker, creating it if needed."""
    global _usage_tracker
    if _usage_tracker is None:
        lm = get_license_manager()
        _usage_tracker = UsageTracker(lm.info)
    return _usage_tracker


def require_quota(feature: Optional[str] = None):
    """
    Decorator for MCP tools to enforce API key limits.

    Usage:
        @mcp.tool()
        @require_quota("market_data")
        async def subscribe_market_data(...):
            ...
    """

    def decorator(fn):
        async def wrapper(*args, **kwargs):
            tracker = get_usage_tracker()
            tracker.check_and_increment(feature)
            return await fn(*args, **kwargs)

        return wrapper

    return decorator


def require_feature(feature: str):
    """
    Decorator to require a specific feature flag in the API key.

    If the feature is disabled or missing, the tool will raise LicenseError.
    """

    def decorator(fn):
        async def wrapper(*args, **kwargs):
            lm = get_license_manager()
            if not lm.has_feature(feature):
                raise LicenseError(
                    f"Feature '{feature}' is not enabled for this API key"
                )
            return await fn(*args, **kwargs)

        return wrapper

    return decorator

