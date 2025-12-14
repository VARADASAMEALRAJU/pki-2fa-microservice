#!/usr/bin/env python3

import os
import time
import base64
import pyotp
from datetime import datetime, timezone

SEED_PATH = "/data/seed.txt"
LOG_PATH = "/cron/last_code.txt"


def read_seed():
    if not os.path.exists(SEED_PATH):
        raise RuntimeError("Seed not found")

    with open(SEED_PATH, "r") as f:
        return f.read().strip()


def generate_totp(hex_seed: str) -> str:
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")

    totp = pyotp.TOTP(
        base32_seed,
        digits=6,
        interval=30
    )

    return totp.now()


def main():
    try:
        hex_seed = read_seed()
        code = generate_totp(hex_seed)

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        log_line = f"{timestamp} - 2FA Code: {code}\n"

        with open(LOG_PATH, "a") as f:
            f.write(log_line)

    except Exception as e:
        print(f"Cron error: {e}", file=os.sys.stderr)


if __name__ == "__main__":
    main()
