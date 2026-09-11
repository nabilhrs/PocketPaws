import hashlib
import hmac
import os

# Salted PBKDF2-SHA256, stored as "pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>".
# Older saves hold a bare unsalted SHA-256 hex digest; those still verify and get
# upgraded to the new format on the next successful login.
ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 200_000


def hash_password(password):
    """Returns a salted PBKDF2 hash string for storing in the database."""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"{ALGORITHM}${ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password, stored_hash):
    """Checks a password against a stored hash (new or legacy format)."""
    if needs_rehash(stored_hash):
        legacy = hashlib.sha256(password.encode()).hexdigest()
        return hmac.compare_digest(legacy, stored_hash)

    try:
        algorithm, iterations, salt_hex, digest_hex = stored_hash.split("$")
    except ValueError:
        return False
    if algorithm != ALGORITHM:
        return False

    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations)
    )
    return hmac.compare_digest(digest.hex(), digest_hex)


def needs_rehash(stored_hash):
    """True for legacy unsalted SHA-256 hashes that should be upgraded."""
    return not stored_hash.startswith(ALGORITHM + "$")
