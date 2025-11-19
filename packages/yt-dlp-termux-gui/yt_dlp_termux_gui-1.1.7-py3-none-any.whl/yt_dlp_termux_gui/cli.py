import re
import sys
import logging
from .utils import detect_termux, ensure_packages, init_logger, get_logger_level, create_logger, ensure_termux_widget
from .constants import METADATA, SETTINGS_PATH, WIDGET_SCRIPT_NAME, WIDGET_TITLE


init_logger()


def print_help(prefix: list[str] = []):
    contents: list[str] = []
    contents.extend(prefix)
    contents.extend([
        "Usage: yt-dlp-termux-gui [OPTIONS...] [COMMAND]\n",
        
        "Commands:",
        "deps --> Ensure dependencies (install missing packages)",
        "launch --> Launch the GUI",
        "widget --> Ensure Termux:Widget shortcut for the GUI\n",
        
        "Options:",
        "--verbose <silent|debug|info|warning|error|critical> --> Set logging level",
        "--silent --> Disable ALL GUI logs in Termux",
        "--widget-name --> Print widget name",
        "--widget-script-name --> Print widget script filename",
        "--settings --> Print current settings",
        "--settings-path --> Print settings path",
        "--settings-reset --> Reset settings",
        "-h, --help --> Show this help message",
        "-v, -V, --version --> Print version\n",
        
        "Options [deps]:",
        "--force --> Overwrite 'curl-impersonate' compiled binaries if they already exist\n",
        
        "Options [launch]:",
        "--no-activity-logs --> Disable GUI activity logs in Termux",
        "--init-logs --> Enable GUI initialization logs in Termux by the GUI\n",
        
        "Options [widget]:",
        "--force --> Overwrite existing widget if it already exist\n",
    ])
    logging.info("\n".join(contents))
    
    
def handle_commands(commands: list[str], options: list[str]):
    level = get_logger_level()
    silent = level == "silent"
        
    logger = create_logger(level)
    verbose = True if not logger.disabled else False
        
    if commands.count("deps"):
        if not detect_termux():
            logging.error("This command must run inside Termux. Make sure '$HOME' and '$PREFIX' environment variables are set.")
            logging.shutdown()
            sys.exit(1)
        force = options.count("--force") != 0
        ensure_packages(force)
        if ensure_termux_widget(force):
            print(f"Termux:Widget script '{WIDGET_SCRIPT_NAME}' has been created.")
        else:
            print(f"Termux:Widget script '{WIDGET_SCRIPT_NAME}' already exists.")
        print(
            "\n".join([
                "\nPlease make sure the plugins 'Termux:GUI' and 'Termux:Widget' were installed the same way as Termux was installed (ignore if already installed):",
                "- Termux:GUI --> https://github.com/termux/termux-gui",
                "- Termux:Widget --> https://github.com/termux/termux-widget\n",
            ])
        )
    
    elif commands.count("launch"):
        from .gui import launch_gui
        if not silent:
            logger.debug("Launching GUI...")
        activity_logs = options.count("--no-activity-logs") == 0
        init_logs = options.count("--init-logs") != 0
        launch_gui(logger, verbose and activity_logs, verbose and init_logs)
        
    elif commands.count("widget"):
        force = options.count("--force") != 0
        if ensure_termux_widget(force):
            logging.info(f"Termux:Widget script '{WIDGET_SCRIPT_NAME}' has been created.")
        else:
            logging.info(f"Termux:Widget script '{WIDGET_SCRIPT_NAME}' already exists.")
    
    
def handle_options(options: list[str]):
    ignored = [s for s in options if re.match(r"^(--verbose|--silent|--init-logs|--no-activity-logs)$", s)]
    try:
        for option in ignored:
            options.remove(option)
    except ValueError:
        pass
        
    if options.count("--widget-script-name"):
        logging.info(WIDGET_SCRIPT_NAME)
        
    if options.count("--widget-name"):
        logging.info(WIDGET_TITLE)
        
    if options.count("--settings-path"):
        logging.info(SETTINGS_PATH)
        
    if options.count("--settings"):
        from .settings import load_settings
        settings = load_settings()
        logging.info(settings)
        
    if options.count("--settings-reset"):
        from .settings import reset_settings
        reset_settings()
        logging.info("Settings has been reset.")
        

def run():
    try:
        args = sys.argv[1:]
        commands = [s for s in args if re.match(r"^(deps|launch|widget)$", s)]
        options = [s for s in args if s.startswith("-")]
        
        if commands == [] and options == []:
            print_help(["Need help with yt-dlp-termux-gui?\n"])
            logging.shutdown()
            sys.exit(1)
    
        if options.count("-v") or options.count("-V") or options.count("--version"):
            logging.info(f"v{METADATA.get('version')}")
            logging.shutdown()
            sys.exit(0)
    
        if options.count("-h") or options.count("--help"):
            print_help([f"yt-dlp-termux-gui (v{METADATA.get('version')}) Help Information\n"])
            logging.shutdown()
            sys.exit(0)
            
        handle_commands(commands, options)
        handle_options(options)
        
    except Exception as e:
        logging.error("CLI error:", str(e))
        logging.shutdown()
        sys.exit(1)
        
        
if __name__ == "__main__":
    run()