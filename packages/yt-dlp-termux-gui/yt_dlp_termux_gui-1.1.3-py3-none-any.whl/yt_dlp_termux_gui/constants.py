import os
import importlib.metadata as lib_metadata

METADATA = lib_metadata.metadata("yt-dlp-termux-gui")

PACKAGE_CONFIG_DIR = os.path.expanduser("~/.config/yt_dlp_termux_gui").replace("\\", "/")

SETTINGS_PATH = f"{PACKAGE_CONFIG_DIR}/settings.json"
SETTINGS_DIR = os.path.dirname(SETTINGS_PATH).replace("\\", "/")

TERMUX_PACKAGE_DIR = "/data/data/com.termux"
TERMUX_HOME = f"{TERMUX_PACKAGE_DIR}/files/home"
TERMUX_PREFIX = f"{TERMUX_PACKAGE_DIR}/files/usr"

TERMUX_CURL_IMPERSONATE_DIR = os.path.join(TERMUX_HOME, "curl-impersonate-android")

TERMUX_WIDGETS_DIR = os.path.expanduser("~/.shortcuts").replace("\\", "/")
TERMUX_WIDGETS_ICONS_DIR = os.path.join(TERMUX_WIDGETS_DIR, "icons").replace("\\", "/")
TERMUX_WIDGETS_TASKS_DIR = os.path.join(TERMUX_WIDGETS_DIR, "tasks").replace("\\", "/")

WIDGET_TITLE = "YT-DLP TERMUX GUI"
WIDGET_SCRIPT_NAME = "yt-dlp-gui.sh"

ADDITIONAL_ARGS_TEMPLATE = [
    "--newline",
    "-N", "3",
    "--retries", "3",
    "--fragment-retries", "3",
    "--restrict-filenames",
    "--embed-metadata",
    "--embed-thumbnail",
    "--impersonate", "Chrome-99",
    "--no-overwrites",
    "--no-post-overwrites",
]