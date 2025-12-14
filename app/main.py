from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import os
import time

import pyotp
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

# ---------- CONFIG ----------
PRIVATE_KEY_PATH = "student_private.pem"
SEED_PATH = "/data/seed.txt"

app = FastAPI(title="PKI 2FA Microservice")


# ---------- REQUEST MODELS ----------
class DecryptSeedRequest(BaseModel):
    encrypted_seed: str


class Verify2FARequest(BaseModel):
    code: str


# ---------- LOAD PRIVATE KEY ----------
def load_private_key():
    try:
        with open(PRIVATE_KEY_PATH, "rb") as f:
            return serialization.load_pem_private_key(
                f.read(),
                password=None
            )
    except Exception as e:
        raise RuntimeError(f"Failed to load private key: {e}")


# ---------- DECRYPT SEED ----------
def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    ciphertext = base64.b64decode(encrypted_seed_b64)

    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    seed = plaintext.decode("utf-8").strip()

    # Validate: 64-char hex string
    if len(seed) != 64 or not all(c in "0123456789abcdef" for c in seed):
        raise ValueError("Invalid seed format")

    return seed


# ---------- READ SEED ----------
def read_seed() -> str:
    if not os.path.exists(SEED_PATH):
        raise RuntimeError("Seed not decrypted yet")

    with open(SEED_PATH, "r") as f:
        return f.read().strip()


# ---------- TOTP GENERATION ----------
def generate_totp(hex_seed: str):
    # HEX → BYTES
    seed_bytes = bytes.fromhex(hex_seed)

    # BYTES → BASE32
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")

    totp = pyotp.TOTP(
        base32_seed,
        digits=6,
        interval=30
    )

    code = totp.now()
    valid_for = 30 - (int(time.time()) % 30)

    return code, valid_for


# ---------- TOTP VERIFICATION ----------
def verify_totp(hex_seed: str, code: str) -> bool:
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")

    totp = pyotp.TOTP(
        base32_seed,
        digits=6,
        interval=30
    )

    # ±1 period tolerance (±30s)
    return totp.verify(code, valid_window=1)


# ---------- API ENDPOINTS ----------

@app.post("/decrypt-seed")
def decrypt_seed_endpoint(payload: DecryptSeedRequest):
    try:
        private_key = load_private_key()
        seed = decrypt_seed(payload.encrypted_seed, private_key)

        os.makedirs(os.path.dirname(SEED_PATH), exist_ok=True)

        with open(SEED_PATH, "w") as f:
            f.write(seed)

        return {"status": "ok"}

    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed")


@app.get("/generate-2fa")
def generate_2fa():
    try:
        hex_seed = read_seed()
        code, valid_for = generate_totp(hex_seed)

        return {
            "code": code,
            "valid_for": valid_for
        }

    except Exception:
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")


@app.post("/verify-2fa")
def verify_2fa(payload: Verify2FARequest):
    if not payload.code:
        raise HTTPException(status_code=400, detail="Missing code")

    try:
        hex_seed = read_seed()
        is_valid = verify_totp(hex_seed, payload.code)

        return {"valid": is_valid}

    except Exception:
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
