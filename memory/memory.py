import json
import re
from pathlib import Path
from datetime import datetime


class Memory:

    def __init__(self, folder, username):

        self.root = Path(folder)
        self.username = username

        self.folder = (
            self.root
            / "users"
            / username
        )

        self.folder.mkdir(
            parents=True,
            exist_ok=True
        )

        self.chat_file = (
            self.folder
            / "conversation.json"
        )

        self.chat_text_file = (
            self.folder
            / "conversation.txt"
        )

        self.mem_file = (
            self.folder
            / "memories.json"
        )

        if not self.chat_file.exists():

            self.chat_file.write_text(
                "[]",
                encoding="utf-8"
            )

        if not self.mem_file.exists():

            self.mem_file.write_text(
                "[]",
                encoding="utf-8"
            )

        # Création / mise à jour du fichier lisible
        self.sync_text_file()


    def load(self, file):

        try:

            return json.loads(
                file.read_text(
                    encoding="utf-8"
                )
            )

        except Exception:

            return []


    def save(self, file, data):

        file.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )


    def sync_text_file(self):

        messages = self.load(
            self.chat_file
        )

        lines = []

        lines.append(
            "=================================================="
        )

        lines.append(
            "CONVERSATION ARTHUR - "
            + self.username
        )

        lines.append(
            "=================================================="
        )

        lines.append("")

        for message in messages:

            role = message.get(
                "role",
                "assistant"
            )

            content = message.get(
                "content",
                ""
            )

            time = message.get(
                "time",
                ""
            )

            if role == "user":
                label = "UTILISATEUR"
            else:
                label = "ARTHUR"

            lines.append(
                f"[{time}] {label} :"
            )

            lines.append(
                content
            )

            lines.append("")

        self.chat_text_file.write_text(
            "\n".join(lines),
            encoding="utf-8"
        )


    def add_message(self, role, content):

        data = self.load(
            self.chat_file
        )

        data.append({
            "role": role,
            "content": content,
            "time": datetime.now().isoformat()
        })

        self.save(
            self.chat_file,
            data
        )

        self.sync_text_file()


    def load_all_chat(self):

        data = self.load(
            self.chat_file
        )

        return [
            {
                "role": x.get(
                    "role",
                    "assistant"
                ),
                "content": x.get(
                    "content",
                    ""
                )
            }
            for x in data
        ]


    def load_recent_chat(self, limit=20):

        data = self.load(
            self.chat_file
        )

        selected = data[-limit:]

        return [
            {
                "role": x.get(
                    "role",
                    "assistant"
                ),
                "content": x.get(
                    "content",
                    ""
                )
            }
            for x in selected
        ]


    def remember(self, text):

        data = self.load(
            self.mem_file
        )

        data.append({
            "text": text,
            "time": datetime.now().isoformat()
        })

        self.save(
            self.mem_file,
            data
        )


    def search(self, query):

        memories = self.load(
            self.mem_file
        )

        words = set(
            re.findall(
                r"\w+",
                query.lower()
            )
        )

        results = []

        for memory in memories:

            memory_words = set(
                re.findall(
                    r"\w+",
                    memory["text"].lower()
                )
            )

            score = len(
                words & memory_words
            )

            if score > 0:

                results.append(
                    (score, memory)
                )

        results.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return [
            memory
            for score, memory in results[:8]
        ]


    def build_context(self, query):

        memories = self.search(query)

        recent = self.load_recent_chat(
            limit=12
        )

        result = []

        if memories:

            result.append(
                "SOUVENIRS :"
            )

            for memory in memories:

                result.append(
                    "- "
                    + memory["text"]
                )

        if recent:

            result.append(
                "\nCONVERSATION RECENTE :"
            )

            for message in recent:

                result.append(
                    message["role"]
                    + " : "
                    + message["content"]
                )

        if not result:

            return "Aucune mémoire."

        return "\n".join(result)
