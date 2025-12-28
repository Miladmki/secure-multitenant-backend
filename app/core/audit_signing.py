# app/core/audit_signing.py

import hmac
import hashlib
from typing import Any

from app.core.config import settings


def _canonical_serialize(payload: dict[str, Any]) -> str:
    """
    Deterministic, canonical serialization.
    - Sorted keys
    - Stable string representation
    - NO JSON ambiguity
    """

    parts: list[str] = []

    for key in sorted(payload.keys()):
        value = payload[key]

        if isinstance(value, dict):
            value = _canonical_serialize(value)

        parts.append(f"{key}={value}")

    return "|".join(parts)


def compute_signature(payload: dict[str, Any]) -> str:
    """
    HMAC over canonical payload.
    """

    canonical = _canonical_serialize(payload)

    return hmac.new(
        settings.audit_signing_key.encode(),
        canonical.encode(),
        hashlib.sha256,
    ).hexdigest()


def compute_entry_hash(
    *,
    prev_hash: str | None,
    signature: str,
) -> str:
    """
    Hash-chain link:
    HMAC(secret, prev_hash || signature)
    """

    base = f"{prev_hash or ''}|{signature}"

    return hmac.new(
        settings.audit_signing_key.encode(),
        base.encode(),
        hashlib.sha256,
    ).hexdigest()


def verify_entry(
    *,
    payload: dict[str, Any],
    signature: str,
    prev_hash: str | None,
    entry_hash: str,
) -> bool:
    """
    Offline verification helper (used later for audit checks).
    """

    expected_signature = compute_signature(payload)
    if not hmac.compare_digest(signature, expected_signature):
        return False

    expected_entry_hash = compute_entry_hash(
        prev_hash=prev_hash,
        signature=signature,
    )

    return hmac.compare_digest(entry_hash, expected_entry_hash)
