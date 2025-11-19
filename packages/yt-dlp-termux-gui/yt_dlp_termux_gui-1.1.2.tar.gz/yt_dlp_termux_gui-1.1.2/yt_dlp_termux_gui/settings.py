import os
import json
from . import constants
from . import utils


defaults = {
    "Video URL": "https://example.com/video",
    "Output Directory": "~/storage/downloads",
    "Start Time (optional)": "*00:00",
    "End Time (optional)": "inf",
    "Cookies File (optional)": os.path.join(constants.SETTINGS_DIR, "cookies.txt"),
    "Filename Template": "%(uploader).30B - %(title)s (%(extractor)s) [%(upload_date>%Y-%m-%d)s].%(ext)s",
    "Additional Arguments": " ".join(constants.ADDITIONAL_ARGS_TEMPLATE),
}


def load_settings(with_defaults: bool = True) -> dict:
    existing_settings: dict = {}
    if os.path.exists(constants.SETTINGS_PATH):
        with open(constants.SETTINGS_PATH, "r") as f:
            existing_settings = json.load(f)
            if not with_defaults:
                return existing_settings
            settings: dict = {}
            for k, v in existing_settings.items():
                settings[k] = v
            for k, v in defaults.items():
                if k not in settings:
                    settings[k] = v
            return settings
    if not with_defaults:
        return {}
    return defaults


def save_settings(settings: dict):
    settings_dir = os.path.dirname(constants.SETTINGS_PATH)
    os.makedirs(settings_dir, exist_ok=True)
    utils.assign_permissions_to_path(settings_dir, ["read", "write"])
    to_save = {k: v for k, v in settings.items() if k != "Video URL"}
    with open(constants.SETTINGS_PATH, "w") as f:
        json.dump(to_save, f, indent=2)


def reset_settings():
    save_settings(defaults)
