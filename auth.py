from pathlib import Path
import json
import hashlib
import hmac
import secrets

BASE = Path(__file__).parent
USERS_FILE = BASE / "users" / "accounts.json"


def load_accounts():
    if not USERS_FILE.exists():
        return {}

    try:
        return json.loads(
            USERS_FILE.read_text(encoding="utf-8")
        )
    except Exception:
        return {}


def save_accounts(accounts):
    USERS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    USERS_FILE.write_text(
        json.dumps(
            accounts,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_bytes(32)

    result = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000
    )

    return salt.hex(), result.hex()


def verify_password(password, salt_hex, hash_hex):
    try:
        salt = bytes.fromhex(salt_hex)

        result = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            200_000
        )

        return hmac.compare_digest(
            result.hex(),
            hash_hex
        )

    except Exception:
        return False


def authenticate(username, password):
    accounts = load_accounts()

    username = username.strip().lower()

    account = accounts.get(username)

    if account is None:
        return None

    if not verify_password(
        password,
        account["salt"],
        account["password_hash"]
    ):
        return None

    return {
        "username": username,
        "display_name": account.get(
            "display_name",
            username
        ),
        "role": account.get(
            "role",
            "user"
        )
    }


def is_admin(account):
    return (
        account is not None
        and account.get("role") == "admin"
    )
