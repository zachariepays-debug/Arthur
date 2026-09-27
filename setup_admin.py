from pathlib import Path
import json
import getpass
import secrets
import hashlib

BASE = Path(__file__).parent
USERS_FILE = BASE / "users" / "accounts.json"

USERS_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

if USERS_FILE.exists():
    try:
        accounts = json.loads(
            USERS_FILE.read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        accounts = {}
else:
    accounts = {}


password = getpass.getpass(
    "\nMot de passe du compte Zacharie : "
)

confirm = getpass.getpass(
    "Confirme le mot de passe : "
)

if not password:
    print("ERREUR : mot de passe vide.")
    raise SystemExit(1)

if password != confirm:
    print("ERREUR : les mots de passe ne correspondent pas.")
    raise SystemExit(1)

salt = secrets.token_bytes(32)

hashed = hashlib.pbkdf2_hmac(
    "sha256",
    password.encode("utf-8"),
    salt,
    200_000
)

accounts["zacharie"] = {
    "display_name": "Zacharie",
    "role": "admin",
    "salt": salt.hex(),
    "password_hash": hashed.hex()
}

USERS_FILE.write_text(
    json.dumps(
        accounts,
        ensure_ascii=False,
        indent=2
    ),
    encoding="utf-8"
)

print("\nCompte Zacharie cree avec le role ADMIN.")
print("Le mot de passe n'est pas stocke en clair.")
