import base64
import json
import os
from typing import Any


def canonical_bytes(payload: dict[str, Any], mode: str = "json") -> bytes:
    # Default to canonical JSON; CBOR canonical optional
    m = (mode or "json").lower()
    if m == "json":
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if m == "cbor":
        try:
            import cbor2  # type: ignore

            return cbor2.dumps(payload, canonical=True)
        except Exception as e:  # pragma: no cover - optional dependency
            raise RuntimeError("CBOR canonical requires cbor2") from e
    raise ValueError("Unsupported canonical mode: " + mode)


def ensure_keys_ecdsa(path: str) -> tuple[bytes, bytes]:
    try:
        from ecdsa import NIST256p, SigningKey
    except Exception as e:  # pragma: no cover - import guard
        raise RuntimeError("ecdsa package is required for ECDSA signing") from e

    priv_path = path + ".ecdsa.pem"
    pub_path = path + ".ecdsa.pub.pem"
    if os.path.exists(priv_path) and os.path.exists(pub_path):
        with open(priv_path, "rb") as f:
            priv_pem = f.read()
        with open(pub_path, "rb") as f:
            pub_pem = f.read()
        return priv_pem, pub_pem

    sk = SigningKey.generate(curve=NIST256p)
    vk = sk.get_verifying_key()
    priv_pem = sk.to_pem()
    pub_pem = vk.to_pem()
    with open(priv_path, "wb") as f:
        f.write(priv_pem)
    with open(pub_path, "wb") as f:
        f.write(pub_pem)
    return priv_pem, pub_pem


def sign_ecdsa(priv_pem: bytes, message: bytes) -> str:
    from hashlib import sha256

    from ecdsa import SigningKey
    from ecdsa.util import sigencode_der

    sk = SigningKey.from_pem(priv_pem)
    sig = sk.sign_deterministic(message, hashfunc=sha256, sigencode=sigencode_der)
    return base64.b64encode(sig).decode("utf-8")


def ensure_keys_ed25519(path: str) -> tuple[bytes, bytes]:
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ed25519
    except Exception as e:  # pragma: no cover - import guard
        raise RuntimeError("cryptography package is required for Ed25519 signing") from e

    priv_path = path + ".ed25519.pem"
    pub_path = path + ".ed25519.pub.pem"
    if os.path.exists(priv_path) and os.path.exists(pub_path):
        with open(priv_path, "rb") as f:
            priv_pem = f.read()
        with open(pub_path, "rb") as f:
            pub_pem = f.read()
        return priv_pem, pub_pem

    sk = ed25519.Ed25519PrivateKey.generate()
    vk = sk.public_key()
    priv_pem = sk.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_pem = vk.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    with open(priv_path, "wb") as f:
        f.write(priv_pem)
    with open(pub_path, "wb") as f:
        f.write(pub_pem)
    return priv_pem, pub_pem


def sign_ed25519(priv_pem: bytes, message: bytes) -> str:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519

    sk = serialization.load_pem_private_key(priv_pem, password=None)
    assert isinstance(sk, ed25519.Ed25519PrivateKey)
    sig = sk.sign(message)
    return base64.b64encode(sig).decode("utf-8")


def ensure_keys(path: str, algo: str = "ecdsa") -> tuple[str, str, str]:
    # Returns (algo, private_repr, public_repr)
    algo = (algo or "ecdsa").lower()
    if algo == "ecdsa":
        priv_pem, pub_pem = ensure_keys_ecdsa(path)
        return "ecdsa", priv_pem.decode("utf-8"), pub_pem.decode("utf-8")
    if algo == "ed25519":
        priv_pem, pub_pem = ensure_keys_ed25519(path)
        return "ed25519", priv_pem.decode("utf-8"), pub_pem.decode("utf-8")
    raise RuntimeError("Unsupported algo for this stub: " + algo)


def sign_canonical(
    payload: dict[str, Any], algo: str, private_repr: str, canonical: str = "json"
) -> str:
    message = canonical_bytes(
        {k: v for k, v in payload.items() if k != "signature"}, mode=canonical
    )
    if algo == "ecdsa":
        return sign_ecdsa(private_repr.encode("utf-8"), message)
    if algo == "ed25519":
        return sign_ed25519(private_repr.encode("utf-8"), message)
    raise RuntimeError("Unsupported algo for this stub: " + algo)
