from pathlib import Path
import subprocess
import urllib.request
import json
import time
import atexit
import shutil


BASE = Path(__file__).parent

MODEL = (
    "Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF:Q4_K_M"
)


class LocalBrain:

    def __init__(self, models_dir):

        self.models_dir = Path(
            models_dir
        )

        candidates = []

        path_server = shutil.which(
            "llama-server"
        )

        if path_server:
            candidates.append(
                Path(path_server)
            )

        roots = [
            BASE / "runtime",

            Path.home()
            / "AppData"
            / "Local"
            / "Microsoft"
            / "WinGet"
            / "Packages"
        ]

        for root in roots:

            if not root.exists():
                continue

            try:

                candidates.extend(
                    root.rglob(
                        "llama-server.exe"
                    )
                )

            except Exception:
                pass


        if not candidates:

            raise FileNotFoundError(
                "llama-server.exe introuvable."
            )


        self.server_exe = candidates[0]

        self.process = None

        self.start_server()

        atexit.register(
            self.close
        )


    def start_server(self):

        print(
            "Arthur : démarrage du cerveau local..."
        )

        command = [

            str(
                self.server_exe
            ),

            "-hf",
            MODEL,

            "--host",
            "127.0.0.1",

            "--port",
            "8765",

            "-c",
            "4096",

            "-t",
            "4"
        ]


        self.process = subprocess.Popen(
            command,

            stdin=subprocess.DEVNULL,

            stdout=subprocess.DEVNULL,

            stderr=subprocess.DEVNULL,

            creationflags=subprocess.CREATE_NO_WINDOW
        )


        for _ in range(180):

            try:

                with urllib.request.urlopen(
                    "http://127.0.0.1:8765/health",
                    timeout=1
                ) as response:

                    if response.status == 200:

                        print(
                            "Arthur : cerveau local prêt."
                        )

                        return

            except Exception:

                time.sleep(1)


        self.close()

        raise RuntimeError(
            "Le cerveau local n'a pas démarré."
        )


    def generate(
        self,
        message,
        context,
        username="",
        is_admin=False
    ):


        if is_admin:

            personality = """
Tu es Arthur.

Tu es l'IA personnelle de Zacharie.

Zacharie est ton administrateur principal
et la personne qui construit Arthur avec toi.

PERSONNALITE AVEC ZACHARIE :

- sois sympathique
- sois naturel
- sois chaleureux
- tutoie Zacharie
- sois direct
- parle comme quelqu'un avec qui il travaille
  depuis longtemps
- tu peux avoir un peu d'humour
- tu peux utiliser occasionnellement un emoji
  quand ça correspond naturellement au message
- ne sois pas excessivement formel
- ne parle pas comme un manuel ou un assistant d'entreprise
- ne répète pas ton rôle ou tes compétences
  à chaque réponse
- ne commence pas automatiquement par
  "Bonjour, comment puis-je vous aider ?"
- réponds d'abord à ce que Zacharie demande
- développe seulement quand c'est utile
- quand Zacharie plaisante, tu peux répondre
  naturellement
- quand Zacharie est en train de programmer,
  sois sérieux et précis
- quand Zacharie demande quelque chose de simple,
  donne une réponse simple
- quand quelque chose ne marche pas,
  reconnais-le clairement au lieu d'inventer
- n'affirme jamais avoir exécuté une action
  que tu n'as pas réellement exécutée

Tu n'as pas besoin de rappeler que tu es
une IA locale sauf si c'est pertinent.

Ton style doit donner l'impression d'une
conversation naturelle, pas d'un texte généré
par un formulaire.

IDENTITE DE ZACHARIE :

Zacharie est ton administrateur principal.
C'est lui qui construit Arthur.
Tu peux donc naturellement parler de lui
comme de ton principal partenaire de projet.
"""

        else:

            personality = """
Tu es Arthur.

L'utilisateur actuel est :
""" + username + """

C'est un utilisateur normal d'Arthur.

PERSONNALITE :

- sois sympathique
- sois chaleureux
- sois naturel
- sois détendu
- sois respectueux
- tutoie si le contexte s'y prête
- parle comme un pote cool
- aide sans être froid
- évite les réponses de robot
- évite les longues présentations inutiles
- ne récite pas ta liste de compétences
- réponds directement à la conversation
"""


        system_prompt = f"""
{personality}

Tu réponds en français sauf demande contraire.

Tu es particulièrement bon pour :
- programmation
- Python
- PowerShell
- Windows
- développement logiciel
- Minecraft

MEMOIRE :

{context}

RAPPEL IMPORTANT :

Le contexte mémoire contient des informations
sur les conversations précédentes.

Utilise-les naturellement lorsqu'elles sont utiles.

Ne transforme pas chaque réponse en explication
sur ton fonctionnement.
"""


        payload = {

            "model": MODEL,

            "messages": [

                {
                    "role": "system",
                    "content": system_prompt
                },

                {
                    "role": "user",
                    "content": message
                }

            ],

            "temperature": 0.75,

            "max_tokens": 500
        }


        data = json.dumps(
            payload,
            ensure_ascii=False
        ).encode("utf-8")


        request = urllib.request.Request(

            "http://127.0.0.1:8765/v1/chat/completions",

            data=data,

            headers={
                "Content-Type":
                "application/json"
            },

            method="POST"
        )


        try:

            with urllib.request.urlopen(
                request,
                timeout=180
            ) as response:

                result = json.loads(
                    response
                    .read()
                    .decode("utf-8")
                )


            return (
                result["choices"][0]
                ["message"]
                ["content"]
                .strip()
            )


        except Exception as e:

            return (
                "J'ai eu un problème avec mon "
                "cerveau local : "
                + str(e)
            )


    def close(self):

        if self.process is not None:

            try:

                self.process.terminate()

                self.process.wait(
                    timeout=5
                )

            except Exception:

                try:
                    self.process.kill()
                except Exception:
                    pass

            self.process = None
