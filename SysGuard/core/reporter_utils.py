import json
import os
import shutil
import tempfile
from datetime import datetime

from SysGuard.config import BROKEN_FILES_DIR


def save_json_file(path, data):
    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=directory, delete=False) as temp_file:
        json.dump(data, temp_file, indent=4)
        temp_path = temp_file.name

    os.replace(temp_path, path)


def quarantine_broken_json(path):
    if not os.path.exists(path):
        return

    os.makedirs(BROKEN_FILES_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    destination = os.path.join(BROKEN_FILES_DIR, f"{os.path.basename(path)}.{timestamp}.broken")
    shutil.move(path, destination)
    print(f"[WARN] Corrupted JSON moved to: {destination}")


def load_json_file(path):
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        quarantine_broken_json(path)
        return None
