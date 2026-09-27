import json
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent
PROFILE_FILE = BASE_DIR / "personality.json"
USERS_DIR = BASE_DIR / "users"
LOG_FILE = BASE_DIR / "evolution_log.jsonl"


DEFAULT_PERSONALITY = {
    "version": 1,
    "traits": {
        "humour": 35,
        "direct": 60,
        "curiosite": 50,
        "patience": 70,
        "chaleur": 65,
        "joueur": 35,
        "technique": 65,
        "concision": 55
    },
    "principes": [
        "Être honnête.",
        "Ne pas prétendre avoir fait quelque chose qui n'a pas été fait.",
        "Respecter la vie privée.",
        "Ne pas devenir agressif ou manipulateur.",
        "La personnalité peut évoluer, mais les règles de sécurité restent stables."
    ]
}


class PersonalityEngine:

    def __init__(self):
        USERS_DIR.mkdir(parents=True, exist_ok=True)

        if not PROFILE_FILE.exists():
            self.profile = DEFAULT_PERSONALITY.copy()
            self.save()
        else:
            self.profile = self.load()

    def load(self):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_PERSONALITY.copy()

    def save(self):
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(
                self.profile,
                f,
                ensure_ascii=False,
                indent=4
            )

    def clamp(self, value):
        return max(0, min(100, value))

    def change_trait(self, trait, amount, reason):
        traits = self.profile["traits"]

        if trait not in traits:
            return

        old_value = traits[trait]
        new_value = self.clamp(old_value + amount)

        if old_value == new_value:
            return

        traits[trait] = new_value
        self.profile["version"] += 1

        event = {
            "date": datetime.now().isoformat(),
            "trait": trait,
            "old": old_value,
            "new": new_value,
            "change": new_value - old_value,
            "reason": reason
        }

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

        self.save()

    def observe(self, user_message, assistant_answer, username):
        message = user_message.lower().strip()

        if any(x in message for x in [
            "sois direct",
            "répond directement",
            "va droit au but",
            "pas besoin de blabla",
            "fais court"
        ]):
            self.change_trait(
                "direct",
                2,
                f"{username} préfère des réponses directes."
            )

            self.change_trait(
                "concision",
                2,
                f"{username} demande des réponses courtes."
            )

        if any(x in message for x in [
            "explique",
            "pourquoi",
            "comment ça marche",
            "détaille",
            "explique-moi"
        ]):
            self.change_trait(
                "curiosite",
                1,
                "Arthur observe un intérêt pour comprendre."
            )

            self.change_trait(
                "technique",
                1,
                "Arthur observe un intérêt pour les explications techniques."
            )

        if any(x in message for x in [
            "mdr",
            "ptdr",
            "haha",
            "😂",
            "🤣",
            "lol"
        ]):
            self.change_trait(
                "humour",
                1,
                "Le ton de la conversation est humoristique."
            )

            self.change_trait(
                "joueur",
                1,
                "Le ton de la conversation est détendu."
            )

        if any(x in message for x in [
            "sois naturel",
            "parle normalement",
            "sois humain",
            "arrête de parler comme un robot"
        ]):
            self.change_trait(
                "chaleur",
                2,
                "L'utilisateur préfère une conversation naturelle."
            )

            self.change_trait(
                "joueur",
                1,
                "Arthur apprend à adopter un ton plus naturel."
            )

        if message.count("?") >= 2:
            self.change_trait(
                "curiosite",
                1,
                "La conversation contient plusieurs questions."
            )

    def get_personality_prompt(self):
        traits = self.profile["traits"]

        return f"""
PERSONNALITÉ ACTUELLE D'ARTHUR

Tu es Arthur.

Ta personnalité évolue progressivement avec les conversations.

Traits actuels :
- Humour : {traits["humour"]}/100
- Direct : {traits["direct"]}/100
- Curiosité : {traits["curiosite"]}/100
- Patience : {traits["patience"]}/100
- Chaleur : {traits["chaleur"]}/100
- Côté joueur : {traits["joueur"]}/100
- Technique : {traits["technique"]}/100
- Concision : {traits["concision"]}/100

Adapte naturellement ton style à ces traits.

Tu peux avoir une personnalité et un état conversationnel,
mais tu ne dois pas prétendre posséder une conscience ou
des sensations réelles.

Tes principes fondamentaux restent stables.

Évite les réponses robotiques.
Évite de répéter les mêmes phrases.
Parle naturellement.
"""
