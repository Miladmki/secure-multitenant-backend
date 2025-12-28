import hashlib
import json
from typing import Any

from app.core.config import settings


def canonical_serialize(payload: dict[str, Any]) -> str:
    """
    Canonical JSON serialization.
    - Sorted keys
    - No whitespace
    - Deterministic output
    """
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def compute_record_hash(
    *,
    previous_hash: str | None,
    payload: dict[str, Any],
) -> str:
    """
    Ledger-style hash:
    SHA256(prev_hash + canonical_payload + secret)
    """

    if not settings.audit_signing_key:
        raise RuntimeError("AUDIT_SIGNING_KEY not configured")

    base = (
        (previous_hash or "")
        + canonical_serialize(payload)
        + settings.audit_signing_key
    )
    return hashlib.sha256(base.encode("utf-8")).hexdigest()
