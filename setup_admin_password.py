from getpass import getpass
from account_files import create_account_file


password = getpass(
    "Entre le mot de passe du compte Zacharie : "
)

confirm = getpass(
    "Confirme le mot de passe : "
)

if not password:
    raise SystemExit(
        "Mot de passe vide."
    )

if password != confirm:
    raise SystemExit(
        "Les deux mots de passe sont différents."
    )

create_account_file(
    "zacharie",
    "admin",
    "Zacharie",
    password
)

print()
print(
    "Fichier users\\zacharie\\identifiants.txt créé."
)
