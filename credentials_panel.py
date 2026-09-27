from pathlib import Path
import json
import streamlit as st


BASE = Path(__file__).parent


def render_credentials_panel(account):

    if account is None:
        return

    if account.get("role") != "admin":
        return

    with st.expander(
        "👑 ADMIN — Identifiants des comptes"
    ):

        st.write(
            "Seul un compte administrateur peut voir "
            "cette section."
        )

        accounts_file = (
            BASE
            / "users"
            / "accounts.json"
        )

        if not accounts_file.exists():

            st.info(
                "Aucun compte trouvé."
            )

            return

        try:

            accounts = json.loads(
                accounts_file.read_text(
                    encoding="utf-8"
                )
            )

        except Exception:

            st.error(
                "Impossible de lire les comptes."
            )

            return


        usernames = list(
            accounts.keys()
        )


        if not usernames:

            st.info(
                "Aucun utilisateur."
            )

            return


        selected = st.selectbox(
            "Utilisateur",
            usernames,
            key="admin_credentials_user"
        )


        user = accounts[selected]

        st.write(
            "Nom : "
            + user.get(
                "display_name",
                selected
            )
        )

        st.write(
            "Rôle : "
            + user.get(
                "role",
                "user"
            )
        )


        credentials_file = (
            BASE
            / "users"
            / selected
            / "identifiants.txt"
        )


        if credentials_file.exists():

            content = (
                credentials_file.read_text(
                    encoding="utf-8"
                )
            )

            st.text_area(
                "Identifiants",
                value=content,
                height=180,
                key="admin_credentials_text"
            )

        else:

            st.warning(
                "Aucun fichier d'identifiants pour cet utilisateur."
            )

            st.caption(
                "Le fichier sera créé lors de sa prochaine "
                "création ou modification de mot de passe."
            )
