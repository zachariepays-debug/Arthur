from pathlib import Path
from datetime import datetime
import shutil
import compileall
import json


class EvolutionManager:

    PROTECTED = {
        "auth.py",
        "evolution.py",
        "setup_admin.py",
        "users/accounts.json"
    }

    def __init__(self, base):

        self.base = Path(base)

        self.root = (
            self.base / "data" / "evolution"
        )

        self.staging = (
            self.root / "staging"
        )

        self.backups = (
            self.root / "backups"
        )

        self.logs = (
            self.root / "logs"
        )

        for folder in (
            self.staging,
            self.backups,
            self.logs
        ):
            folder.mkdir(
                parents=True,
                exist_ok=True
            )

    def timestamp(self):

        return datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

    def create_backup(self):

        destination = (
            self.backups
            / ("arthur_" + self.timestamp())
        )

        destination.mkdir(
            parents=True,
            exist_ok=True
        )

        ignored = {
            ".venv",
            "__pycache__",
            "models",
            "runtime",
            "data/evolution/backups",
            "data/evolution/staging",
            "data/evolution/logs"
        }

        for item in self.base.rglob("*"):

            if not item.is_file():
                continue

            relative = item.relative_to(
                self.base
            )

            relative_text = str(
                relative
            ).replace("\\", "/")

            if any(
                relative_text == x
                or relative_text.startswith(x + "/")
                for x in ignored
            ):
                continue

            target = (
                destination / relative
            )

            target.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            try:
                shutil.copy2(
                    item,
                    target
                )
            except Exception:
                pass

        return destination

    def check_path(self, relative_path):

        relative_path = str(
            relative_path
        ).replace("\\", "/")

        if relative_path in self.PROTECTED:
            return False, "Fichier protege."

        if relative_path.startswith("."):
            return False, "Chemin interdit."

        if ".." in Path(relative_path).parts:
            return False, "Chemin interdit."

        allowed = {
            ".py",
            ".json",
            ".txt",
            ".md",
            ".toml"
        }

        if Path(
            relative_path
        ).suffix.lower() not in allowed:
            return False, "Type de fichier interdit."

        return True, "OK"

    def stage_file(self, relative_path, content):

        valid, reason = self.check_path(
            relative_path
        )

        if not valid:
            raise ValueError(reason)

        target = (
            self.staging
            / relative_path
        )

        target.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        target.write_text(
            content,
            encoding="utf-8"
        )

        return target

    def test_staging(self):

        files = list(
            self.staging.rglob("*.py")
        )

        for file in files:

            if not compileall.compile_file(
                str(file),
                quiet=1
            ):
                return False, (
                    "Erreur Python : "
                    + str(file)
                )

        return True, (
            f"{len(files)} fichier(s) teste(s)."
        )
