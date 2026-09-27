from pathlib import Path


BASE = Path(__file__).parent


def create_account_file(
    username,
    role,
    display_name,
    password
):

    folder = (
        BASE
        / "users"
        / username
    )

    folder.mkdir(
        parents=True,
        exist_ok=True
    )

    file = (
        folder
        / "identifiants.txt"
    )

    content = f"""==================================================
                COMPTE ARTHUR
==================================================

Nom d'utilisateur : {username}
Nom affiche       : {display_name}
Role              : {role}

Mot de passe      : {password}

==================================================
"""

    file.write_text(
        content,
        encoding="utf-8"
    )
