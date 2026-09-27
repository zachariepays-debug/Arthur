from pathlib import Path
import json


BASE = Path(__file__).parent

STATE_FILE = (
    BASE
    / "data"
    / "arthur_state.json"
)


def _ensure():

    STATE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if not STATE_FILE.exists():

        STATE_FILE.write_text(
            json.dumps(
                {"online": True},
                indent=2
            ),
            encoding="utf-8"
        )


def is_online():

    _ensure()

    try:

        data = json.loads(
            STATE_FILE.read_text(
                encoding="utf-8"
            )
        )

        return bool(
            data.get(
                "online",
                True
            )
        )

    except Exception:

        return True


def set_online(value):

    _ensure()

    STATE_FILE.write_text(
        json.dumps(
            {"online": bool(value)},
            indent=2
        ),
        encoding="utf-8"
    )
