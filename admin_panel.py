from pathlib import Path
import json
import streamlit as st


BASE = Path(__file__).parent


def render_admin_panel(account):

    if account is None:
        return

    if account.get("role") != "admin":
        return


    with st.expander(
        "👑 ADMIN — Conversations des utilisateurs"
    ):

        st.write(
            "En tant qu'administrateur, tu peux "
            "consulter les conversations enregistrées "
            "sur le PC."
        )


        accounts_file = (
            BASE
            / "users"
            / "accounts.json"
        )


        if not accounts_file.exists():

            st.info(
                "Aucun compte disponible."
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
            "Choisir un utilisateur",
            usernames
        )


        account_data = accounts[
            selected
        ]


        st.write(
            f"Utilisateur : **{account_data.get('display_name', selected)}**"
        )

        st.write(
            f"Role : **{account_data.get('role', 'user')}**"
        )


        conversation_file = (
            BASE
            / "memory"
            / "users"
            / selected
            / "conversation.txt"
        )


        st.write(
            "Fichier local :"
        )

        st.code(
            str(conversation_file)
        )


        if not conversation_file.exists():

            st.info(
                "Aucune conversation enregistrée."
            )

            return


        content = (
            conversation_file.read_text(
                encoding="utf-8"
            )
        )


        st.text_area(
            "Conversation complète",
            value=content,
            height=500
        )


        st.download_button(
            "📄 Copier la conversation",
            data=content,
            file_name=(
                "conversation_"
                + selected
                + ".txt"
            ),
            mime="text/plain"
        )


        credentials = (
            BASE
            / "users"
            / selected
            / "identifiants.txt"
        )


        if credentials.exists():

            st.write(
                "Informations du compte :"
            )

            st.text(
                credentials.read_text(
                    encoding="utf-8"
                )
            )
