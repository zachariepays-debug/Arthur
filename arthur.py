from pathlib import Path

from memory.memory import Memory
from brain import LocalBrain
from evolution import EvolutionManager


BASE = Path(__file__).parent


class Arthur:

    def __init__(
        self,
        username="zacharie",
        role="admin",
        brain=None
    ):

        self.username = username
        self.role = role

        self.memory = Memory(
            BASE / "memory",
            username
        )

        if brain is None:
            self.brain = LocalBrain(
                BASE / "models"
            )
        else:
            self.brain = brain

        self.evolution = EvolutionManager(
            BASE
        )


    @property
    def is_admin(self):
        return self.role == "admin"


    def direct_response(self, message):

        text = (
            message
            .strip()
            .lower()
        )


        # -------------------------------------------------
        # IDENTITE DE ZACHARIE
        # -------------------------------------------------

        if self.is_admin:

            if text in (
                "qui je suis",
                "qui je suis pour toi",
                "tu sais qui je suis",
                "tu sais qui je suis pour toi",
                "qui suis-je",
            ):

                return (
                    "Zacharie, t'es mon admin principal, "
                    "mais surtout la personne avec qui je "
                    "construis Arthur depuis le début. 😄"
                )


        # -------------------------------------------------
        # SALUTATIONS
        # -------------------------------------------------

        if self.is_admin:

            if text in (
                "salut",
                "slt",
                "yo",
                "coucou",
                "hey"
            ):

                return (
                    "Yo Zacharie 😄"
                )


        return None


    def respond(self, message):

        self.memory.add_message(
            "user",
            message
        )


        # Réponses importantes gérées directement
        direct = self.direct_response(
            message
        )

        if direct is not None:

            self.memory.add_message(
                "assistant",
                direct
            )

            return direct


        text = (
            message
            .strip()
            .lower()
        )


        # -------------------------------------------------
        # EVOLUTION
        # -------------------------------------------------

        update_commands = [
            "fais ta mise à jour",
            "fait ta mise à jour",
            "mets toi à jour",
            "met toi à jour",
            "améliore toi",
            "ameliore toi"
        ]


        if any(
            command in text
            for command in update_commands
        ):

            if not self.is_admin:

                answer = (
                    "Cette fonction est réservée "
                    "à Zacharie, l'administrateur."
                )

            else:

                backup = (
                    self.evolution.create_backup()
                )

                answer = (
                    "Oui 👍 Je passe en mode évolution. "
                    "J'ai créé une sauvegarde de sécurité : "
                    + backup.name
                    + "."
                )

            self.memory.add_message(
                "assistant",
                answer
            )

            return answer


        # -------------------------------------------------
        # MEMOIRE
        # -------------------------------------------------

        context = (
            self.memory.build_context(
                message
            )
        )


        # -------------------------------------------------
        # CERVEAU
        # -------------------------------------------------

        answer = self.brain.generate(
            message,
            context,
            username=self.username,
            is_admin=self.is_admin
        )


        self.memory.add_message(
            "assistant",
            answer
        )


        return answer
