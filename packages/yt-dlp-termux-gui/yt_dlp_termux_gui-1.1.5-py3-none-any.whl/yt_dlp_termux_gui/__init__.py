from .cli import run as launch
from .constants import SETTINGS_PATH, WIDGET_SCRIPT_NAME, WIDGET_TITLE
from .utils import detect_termux, ensure_termux_widget, ensure_packages
from .settings import load_settings as get_settings, reset_settings


# launch the GUI
launch()

# get settings
settings = get_settings()

# reset settings
reset_settings()

# get settings file path
settings_path = SETTINGS_PATH

# get widget name (yt-dlp-gui.sh)
widget_name = WIDGET_SCRIPT_NAME

# get widget title (YT-DLP TERMUX GUI)
widget_name = WIDGET_TITLE

# create Termux:Widget shortcut
ensure_termux_widget(force=True)

# check if running inside Termux
is_termux = detect_termux()

# ensure dependencies are installed
#
# IMPORTANT:
# the plugins 'Termux:GUI' and 'Termux:Widget'
# must be installed the same way as Termux was installed
# Termux:GUI --> https://github.com/termux/termux-gui
# Termux:Widget --> https://github.com/termux/termux-widget
ensure_packages(force=True)