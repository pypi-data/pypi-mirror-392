from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class InMemoryKeyRegistry:
    """Simple in-memory registry for node_id -> public_key."""

    def __init__(self) -> None:
        self._keys: dict[str, str] = {}

    async def set_key(self, node_id: str, public_key: str) -> None:
        self._keys[node_id] = public_key

    async def get_key(self, node_id: str) -> str | None:
        return self._keys.get(node_id)


@dataclass(slots=True)
class _DedupEntry:
    expires_at: float


class InMemoryDedupStore:
    """Track processed message ids with TTL to avoid duplicates/loops."""

    def __init__(self) -> None:
        self._entries: dict[str, _DedupEntry] = {}
        self._lock = asyncio.Lock()

    async def seen(self, msg_id: str) -> bool:
        now = time.time()
        async with self._lock:
            entry = self._entries.get(msg_id)
            if entry and entry.expires_at > now:
                return True
            # Cleanup occasionally
            to_delete = [k for k, v in self._entries.items() if v.expires_at <= now]
            for k in to_delete:
                del self._entries[k]
            return False

    async def remember(self, msg_id: str, ttl: int | None) -> None:
        expiry = time.time() + (ttl if ttl and ttl > 0 else 60)
        async with self._lock:
            self._entries[msg_id] = _DedupEntry(expires_at=expiry)


class SignatureVerifier:
    """Pluggable signature verification with environment flags.

    ENV:
      EDGE_VERIFY_SIGNATURES: '1' to enforce, default disabled
      EDGE_SIG_ALGO: 'ed25519' (default) or 'ecdsa' or 'none'
    """

    def __init__(self, registry: InMemoryKeyRegistry | None = None) -> None:
        self._registry = registry or InMemoryKeyRegistry()
        self._verify = os.getenv("EDGE_VERIFY_SIGNATURES", "0") in {"1", "true", "True"}
        self._algo = os.getenv("EDGE_SIG_ALGO", "ed25519").lower()

    async def ensure_key(self, node_id: str, public_key: str) -> None:
        existing = await self._registry.get_key(node_id)
        if existing and existing != public_key:
            logger.warning("Public key mismatch for node_id=%s (keeping existing)", node_id)
            return
        if not existing:
            await self._registry.set_key(node_id, public_key)

    async def verify(
        self, node_id: str, message_bytes: bytes, signature_b64: str, *, algo: str | None = None
    ) -> bool:
        algo_to_use = (algo or self._algo or "ed25519").lower()
        if not self._verify or algo_to_use == "none":
            return True
        public_key = await self._registry.get_key(node_id)
        if not public_key:
            logger.warning("No public key registered for node_id=%s", node_id)
            return False
        import base64

        sig_bytes = b""
        try:
            sig_bytes = base64.b64decode(signature_b64)
        except Exception:
            logger.warning("Invalid base64 signature for node_id=%s", node_id)
            return False

        if algo_to_use in {"ed25519", "eddsa"}:
            # Support both PEM-encoded public keys and base64/raw 32-byte keys
            # 1) If PEM detected, use cryptography backend
            if public_key.strip().startswith("-----BEGIN "):
                try:
                    from cryptography.hazmat.primitives import serialization
                    from cryptography.hazmat.primitives.asymmetric import ed25519 as _ed

                    pub = serialization.load_pem_public_key(public_key.encode("utf-8"))
                    if not isinstance(pub, _ed.Ed25519PublicKey):
                        logger.warning("Public key is not Ed25519 for node_id=%s", node_id)
                        return False
                    pub.verify(sig_bytes, message_bytes)
                    return True
                except Exception:
                    logger.exception("Ed25519 verification failed (PEM)")
                    return False
            # 2) Try base64 or raw 32-byte key with PyNaCl
            try:
                from nacl.exceptions import BadSignatureError  # type: ignore
                from nacl.signing import VerifyKey  # type: ignore

                raw = None
                try:
                    raw = base64.b64decode(public_key)
                except Exception:
                    raw = None
                if not raw:
                    # if not base64, attempt to interpret as raw bytes (unlikely in text env)
                    raw = public_key.encode("utf-8")
                if len(raw) != 32:
                    logger.warning("Ed25519 public key length invalid for node_id=%s", node_id)
                    return False
                verify_key = VerifyKey(raw)
                verify_key.verify(message_bytes, sig_bytes)
                return True
            except ModuleNotFoundError:
                logger.error(
                    "PyNaCl required for raw/base64 Ed25519 keys. Provide PEM or install pynacl."
                )
                return False
            except BadSignatureError:
                return False
            except Exception:
                logger.exception("Ed25519 verification error (raw/base64)")
                return False

        # Default to ECDSA over SHA256 (curve inferred from PEM)
        try:
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import ec
            from cryptography.hazmat.primitives.asymmetric.utils import (
                encode_dss_signature,
            )

            pub = serialization.load_pem_public_key(public_key.encode("utf-8"))

            # Ensure signature in DER; if 64-byte raw, convert to DER
            der_sig = sig_bytes
            if len(sig_bytes) in (64, 66):  # raw r||s (32 each) or plus 2 bytes
                try:
                    half = len(sig_bytes) // 2
                    r = int.from_bytes(sig_bytes[:half], "big")
                    s = int.from_bytes(sig_bytes[half:], "big")
                    der_sig = encode_dss_signature(r, s)
                except Exception:
                    pass

            pub.verify(der_sig, message_bytes, ec.ECDSA(hashes.SHA256()))
            return True
        except Exception:
            logger.exception("ECDSA verification failed")
            return False


__all__ = [
    "InMemoryKeyRegistry",
    "InMemoryDedupStore",
    "SignatureVerifier",
]
