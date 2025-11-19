"""
Secure Element (HSM) Signing Stub
---------------------------------
Abstracts signing via a secure element (e.g., ATECC608A) or SoC keystore.

For production hardware, implement the following hooks to:
- Generate or import device keypair in HSM
- Export public key (PEM or base64 raw) for HELLO
- Compute signature over canonical bytes (JSON or CBOR)

This stub falls back to software signing (crypto_sign) if HSM is unavailable.
"""

from __future__ import annotations

from typing import Any

try:  # Optional import of vendor-specific HSM library
    import hsm_vendor  # type: ignore
except Exception:  # pragma: no cover - HSM not present in dev
    hsm_vendor = None  # type: ignore

from .crypto_sign import ensure_keys, sign_canonical


def ensure_device_keys(path: str, algo: str) -> tuple[str, str, str]:
    """Return (algo, private_repr, public_repr).

    Replace this with HSM provisioning. For dev, falls back to software keys.
    """
    # Example for HSM:
    # if hsm_vendor is not None:
    #     return (algo, "HSM:KEYSLOT0", hsm_vendor.export_public_pem(slot=0))
    return ensure_keys(path, algo)


def hsm_sign(payload: dict[str, Any], algo: str, private_ref: str, canonical: str = "json") -> str:
    """Compute signature via HSM; fall back to software path.

    private_ref: HSM slot or PEM string for dev mode.
    """
    # Example for HSM:
    # if hsm_vendor is not None and private_ref.startswith("HSM:"):
    #     data = canonical_bytes(payload, mode=canonical)
    #     return base64.b64encode(hsm_vendor.sign(slot=0, message=data)).decode("utf-8")
    return sign_canonical(payload, algo, private_ref, canonical)
