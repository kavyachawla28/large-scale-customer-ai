import hashlib
import secrets


def hash_password(password):
    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100_000,
    )

    return f"{salt.hex()}:{password_hash.hex()}"


def verify_password(password, stored_hash):
    try:
        salt_hex, password_hash_hex = stored_hash.split(":")

        salt = bytes.fromhex(salt_hex)

        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            100_000,
        )

        return secrets.compare_digest(
            calculated_hash.hex(),
            password_hash_hex,
        )

    except (ValueError, TypeError):
        return False