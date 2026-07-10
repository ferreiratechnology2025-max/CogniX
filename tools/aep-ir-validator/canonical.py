"""
Single source of truth for AEP-IR canonicalization.

Both the runner (envelope creation, §6.2) and the validator (ENV-5 checksum
verification) MUST import canonicalization from here, so their checksums cannot
drift apart. The Canonicalization Standard named by SPEC/AEP-IR-1.0.md is
RFC 8785 (JCS); this module implements it via the `rfc8785` library. It is a
HARD dependency — there is no silent fallback, because a divergent encoder
(e.g. integer-only canonicaljson) would produce checksums that disagree with
the frozen standard on numeric payloads (LLM-generated plans contain floats).
"""

import hashlib

try:
    import rfc8785 as _rfc8785
    _AVAILABLE = True
except ImportError:  # pragma: no cover
    _rfc8785 = None
    _AVAILABLE = False

CANONICAL_LIBRARY = "rfc8785"
CANONICAL_STANDARD = "RFC 8785 (JCS)"


def _require() -> None:
    if not _AVAILABLE:
        raise RuntimeError(
            "rfc8785 (RFC 8785 JCS canonicalization) is required but not "
            "installed. Install it with: pip install rfc8785==0.1.4"
        )


def canonical_bytes(obj) -> bytes:
    """Return the RFC 8785 canonical JSON encoding of obj, as bytes."""
    _require()
    return _rfc8785.dumps(obj)


def checksum(obj) -> str:
    """Return the SHA256 hex digest of the canonical JSON of obj."""
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def library_version() -> str:
    import importlib.metadata as _m
    return _m.version("rfc8785")
