import base64
import os

from ontologia_api.core.edge_security import InMemoryKeyRegistry, SignatureVerifier


def _set_verify():
    os.environ["EDGE_VERIFY_SIGNATURES"] = "1"


def test_verify_ecdsa_pem_roundtrip():
    _set_verify()
    try:
        from hashlib import sha256

        from ecdsa import NIST256p, SigningKey
        from ecdsa.util import sigencode_der
    except Exception:
        return  # skip if ecdsa not available

    sk = SigningKey.generate(curve=NIST256p)
    vk = sk.get_verifying_key()
    priv_pem = sk.to_pem()
    pub_pem = vk.to_pem().decode("utf-8")
    message = b"hello-ecdsa"
    sig = sk.sign_deterministic(message, hashfunc=sha256, sigencode=sigencode_der)
    sig_b64 = base64.b64encode(sig).decode("utf-8")

    reg = InMemoryKeyRegistry()
    verifier = SignatureVerifier(registry=reg)
    import asyncio

    asyncio.run(reg.set_key("node-ecdsa", pub_pem))
    ok = asyncio.run(verifier.verify("node-ecdsa", message, sig_b64, algo="ecdsa"))
    assert ok


def test_verify_ed25519_pem_roundtrip():
    _set_verify()
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ed25519
    except Exception:
        return  # skip if cryptography not available

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
    ).decode("utf-8")
    message = b"hello-ed25519"
    sig = sk.sign(message)
    sig_b64 = base64.b64encode(sig).decode("utf-8")

    reg = InMemoryKeyRegistry()
    verifier = SignatureVerifier(registry=reg)
    import asyncio

    asyncio.run(reg.set_key("node-ed25519", pub_pem))
    ok = asyncio.run(verifier.verify("node-ed25519", message, sig_b64, algo="ed25519"))
    assert ok
