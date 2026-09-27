import streamlit as st

from auth import (
    authenticate,
    load_accounts,
    save_accounts
)

from arthur import Arthur
from admin_panel import render_admin_panel
from account_files import create_account_file
from credentials_panel import render_credentials_panel
from brain import LocalBrain
from control import (
    is_online,
    set_online
)

from pathlib import Path
import hashlib
import secrets


BASE = Path(__file__).parent


# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="Arthur",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# =========================================================
# STYLE
# =========================================================

st.markdown("""
<style>

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

.stApp {
    background: #0b141a;
}

.main .block-container {
    max-width: 820px;
    padding-top: 1rem;
    padding-bottom: 6rem;
}

h1, h2, h3 {
    color: #e9edef !important;
}

p, label {
    color: #d1d7db !important;
}


/* Header */

.arthur-title {
    font-size: 24px;
    font-weight: 700;
}

.arthur-online {
    color: #53d769;
    font-size: 12px;
}

.arthur-offline {
    color: #ff5c5c;
    font-size: 14px;
    font-weight: 600;
}


/* Messages */

[data-testid="stChatMessage"] {
    border: 0 !important;
    padding: 2px 0 !important;
    background: transparent !important;
}


/* Bulle utilisateur */

[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-user"]
) [data-testid="stChatMessageContent"] {

    background: #005c4b !important;

    border-radius:
        16px 16px 4px 16px !important;

    padding:
        9px 13px !important;

    margin-left: auto !important;

    max-width: 78% !important;
}


/* Bulle Arthur */

[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-assistant"]
) [data-testid="stChatMessageContent"] {

    background: #202c33 !important;

    border-radius:
        16px 16px 16px 4px !important;

    padding:
        9px 13px !important;

    max-width: 78% !important;
}


/* Texte messages */

[data-testid="stChatMessageContent"] p {
    margin: 0 !important;
    color: #e9edef !important;
    line-height: 1.5;
}


/* Input */

[data-testid="stChatInput"] {
    background: transparent !important;
}

[data-testid="stChatInput"] textarea {
    background: #202c33 !important;
    color: #e9edef !important;
    border-radius: 22px !important;
    border: 1px solid #334047 !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #8696a0 !important;
}


/* Boutons */

.stButton button {
    border-radius: 12px !important;
}


/* Offline */

.offline-title {
    text-align: center;
    font-size: 32px;
    font-weight: 700;
    color: #e9edef;
}

.offline-text {
    text-align: center;
    color: #8696a0;
    font-size: 14px;
    line-height: 1.6;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# CERVEAU UNIQUE PARTAGE
# =========================================================

@st.cache_resource
def get_brain():

    return LocalBrain(
        BASE / "models"
    )


def stop_shared_brain():

    try:

        brain = get_brain()

        brain.close()

    except Exception:
        pass

    try:

        get_brain.clear()

    except Exception:
        pass


def restart_shared_brain():

    try:

        get_brain.clear()

    except Exception:
        pass


# =========================================================
# INSCRIPTION
# =========================================================

def register_user(
    username,
    password
):

    username = (
        username
        .strip()
        .lower()
    )

    if len(username) < 2:

        return (
            False,
            "Le nom doit contenir au moins 2 caractères."
        )

    if not password:

        return (
            False,
            "Choisis un mot de passe."
        )

    accounts = load_accounts()

    if username in accounts:

        return (
            False,
            "Ce nom existe déjà."
        )

    salt = secrets.token_bytes(32)

    password_hash = (
        hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            200_000
        )
    )

    accounts[username] = {
        "display_name": username,
        "role": "user",
        "salt": salt.hex(),
        "password_hash": password_hash.hex()
    }

    save_accounts(accounts)

    create_account_file(
        username,
        "user",
        username,
        password
    )

    return (
        True,
        "Compte créé."
    )


# =========================================================
# SI ARTHUR EST ETEINT
# =========================================================

if not is_online():

    st.write("")
    st.write("")
    st.write("")

    st.markdown(
        """
        <div class="offline-title">
            🤖 Arthur est hors ligne
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="offline-text">
            Arthur a été éteint par l'administrateur
            pour tout le monde.<br><br>
            Entre le code d'accès administrateur
            pour le redémarrer.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    with st.form(
        "restart_form"
    ):

        restart_code = st.text_input(
            "Code d'accès",
            type="password",
            placeholder="Code de redémarrage"
        )

        restart = st.form_submit_button(
            "▶️ Redémarrer Arthur",
            use_container_width=True
        )

        if restart:

            account = authenticate(
                "zacharie",
                restart_code
            )

            if (
                account is not None
                and account["role"] == "admin"
            ):

                set_online(True)

                restart_shared_brain()

                st.success(
                    "Arthur va redémarrer..."
                )

                st.rerun()

            else:

                st.error(
                    "Code incorrect."
                )

    st.stop()


# =========================================================
# CONNEXION
# =========================================================

if "account" not in st.session_state:

    st.title("🤖 Arthur")

    st.write(
        "IA personnelle locale."
    )

    login_tab, register_tab = st.tabs(
        [
            "Se connecter",
            "Inscription"
        ]
    )


    with login_tab:

        st.subheader(
            "Se connecter"
        )

        username = st.text_input(
            "Nom d'utilisateur",
            key="login_user"
        )

        password = st.text_input(
            "Mot de passe",
            type="password",
            key="login_pass"
        )

        if st.button(
            "Se connecter",
            use_container_width=True
        ):

            account = authenticate(
                username,
                password
            )

            if account is None:

                st.error(
                    "Identifiants incorrects."
                )

            else:

                st.session_state.account = account

                st.rerun()


    with register_tab:

        st.subheader(
            "Créer un compte"
        )

        new_username = st.text_input(
            "Nom d'utilisateur",
            key="register_user"
        )

        new_password = st.text_input(
            "Mot de passe",
            type="password",
            key="register_pass"
        )

        confirm_password = st.text_input(
            "Confirmer le mot de passe",
            type="password",
            key="register_confirm"
        )

        if st.button(
            "Créer mon compte",
            use_container_width=True
        ):

            if new_password != confirm_password:

                st.error(
                    "Les mots de passe sont différents."
                )

            else:

                success, message = register_user(
                    new_username,
                    new_password
                )

                if success:

                    st.success(
                        message
                    )

                else:

                    st.error(
                        message
                    )


    st.stop()


# =========================================================
# COMPTE
# =========================================================

account = st.session_state.account

render_credentials_panel(account)

render_admin_panel(account)

username = account["username"]
role = account["role"]


# =========================================================
# ARTHUR DE LA SESSION
# =========================================================

if "arthur" not in st.session_state:

    st.session_state.arthur = Arthur(
        username,
        role,
        brain=get_brain()
    )


arthur = st.session_state.arthur


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="arthur-title">🤖 Arthur</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="arthur-online">● En ligne</div>',
    unsafe_allow_html=True
)

st.write(
    f"Connecté : {account['display_name']}"
    + (
        " 👑 ADMIN"
        if role == "admin"
        else ""
    )
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.write(
        "**Compte**"
    )

    st.write(
        account["display_name"]
    )

    if role == "admin":

        st.divider()

        st.write(
            "👑 **Administration**"
        )

        st.write(
            "Commande disponible dans le chat :"
        )

        st.code(
            "/stop"
        )

        st.caption(
            "Arrête Arthur pour tous les utilisateurs."
        )

    st.divider()

    if st.button(
        "🚪 Se déconnecter",
        use_container_width=True
    ):

        for key in list(
            st.session_state.keys()
        ):

            del st.session_state[key]

        st.rerun()


# =========================================================
# HISTORIQUE COMPLET
# =========================================================

messages = (
    arthur.memory.load_all_chat()
)


for message in messages:

    role_message = message["role"]

    if role_message == "user":

        with st.chat_message(
            "user",
            avatar="👤"
        ):

            st.write(
                message["content"]
            )

    else:

        with st.chat_message(
            "assistant",
            avatar="🤖"
        ):

            st.write(
                message["content"]
            )


# =========================================================
# NOUVEAU MESSAGE
# =========================================================

prompt = st.chat_input(
    "Écris un message..."
)


if prompt:

    clean = (
        prompt
        .strip()
        .lower()
    )


    # -----------------------------------------------------
    # /STOP
    # -----------------------------------------------------

    if clean == "/stop":

        arthur.memory.add_message(
            "user",
            prompt
        )


        if not arthur.is_admin:

            answer = (
                "La commande /stop est réservée "
                "à l'administrateur."
            )

            arthur.memory.add_message(
                "assistant",
                answer
            )

            st.error(
                answer
            )

        else:

            answer = (
                "Arthur est maintenant hors ligne "
                "pour tout le monde."
            )

            arthur.memory.add_message(
                "assistant",
                answer
            )

            set_online(False)

            stop_shared_brain()

            st.session_state.pop(
                "arthur",
                None
            )

            st.rerun()


    # -----------------------------------------------------
    # MESSAGE NORMAL
    # -----------------------------------------------------

    else:

        with st.chat_message(
            "user",
            avatar="👤"
        ):

            st.write(
                prompt
            )

        with st.chat_message(
            "assistant",
            avatar="🤖"
        ):

            with st.spinner(
                "Arthur écrit..."
            ):

                answer = (
                    arthur.respond(
                        prompt
                    )
                )

            st.write(
                answer
            )



