import os
import sys
import re
import logging
import subprocess
from io import BytesIO
from typing import Literal, Callable
from PIL import Image
import requests
from . import constants


def run_cli_command(
    cmd: list[str],
    on_stdout: Callable[[str], None] = lambda x: None,
    on_stderr: Callable[[str], None] = lambda x: None
):
    errors = ""
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.stdout and on_stdout:
        for line in proc.stdout:
            on_stdout(line.strip())
    if proc.stderr and on_stderr:
        for line in proc.stderr:
            on_stderr(line.strip())
            errors += f"{line.strip()}\n"
    proc.wait()
    
    return errors


def run_cli_command_simple(cmd: list[str]):
    subprocess.run(cmd, check=True)


def get_cli_option_value(
    options: list[str],
    option: str,
    default: list[str] = None,
    allowed_values: list[str] = None
) -> str:
    value = default
    try:
        index = options.index(option)
        value = options[index + 1]
    except ValueError:
        pass
    if allowed_values and value not in allowed_values:
        raise ValueError(f"Invalid value for '{option}' option: '{value}'. Allowed values: {', '.join(allowed_values)}.")
    return value


def init_logger():
    logging.basicConfig(
        level = logging.DEBUG,
        format = "%(message)s"
    )


def get_logger_level():
    level = "debug"
    args = sys.argv[1:]
    options = [s for s in args if s.startswith("-")]
    silent = options.count("--silent") != 0
    
    if silent:
        level = "silent"
    elif options.count("--verbose"):
        level = get_cli_option_value(options, "--verbose", "debug", [
            "silent",
            "debug",
            "info",
            "warning",
            "error",
            "critical"
        ])
        
    return level
    

def create_logger(level: Literal["silent", "debug", "info", "warning", "error", "critical"] = "debug") -> logging.Logger:
    logger = logging.getLogger("yt-dlp-termux-gui")
        
    logger_level = level.upper()
    logger.setLevel(getattr(logging, logger_level if logger_level != "SILENT" else "DEBUG"))
    
    if logger_level == "SILENT":
        logger.disabled = True
        
    logger.addHandler(logging.NullHandler(logger.level))
    
    return logger
    

def is_valid_url(url: str) -> bool:
    url_pattern = re.compile(
        r'^(https?://)?'                        # optional http or https
        r'(([A-Za-z0-9-]+\.)+[A-Za-z]{2,})'     # domain (example.com)
        r'(:\d+)?'                              # optional port
        r'(/[\w\-.~:/?#[\]@!$&\'()*+,;%=]*)?$'  # optional path/query
    )
    return bool(url_pattern.match(url))


def ensure_termux_env_variables() -> bool | dict[str, str]:
    home_path = os.environ.get("HOME")
    prefix_path = os.environ.get("PREFIX")
    if not home_path.startswith(constants.TERMUX_HOME) or not prefix_path.startswith(constants.TERMUX_PREFIX):
        return False
    return {
        "HOME": home_path,
        "PREFIX": prefix_path
    }


def detect_termux() -> bool:
    print("Checking platform...")
    termux_env_variables = ensure_termux_env_variables()
    if not termux_env_variables:
        return False
    return termux_env_variables["PREFIX"].startswith(constants.TERMUX_PREFIX)
    
    
def ensure_ytdlp():
    print("\nEnsuring yt-dlp...")
    run_cli_command_simple([
        "pip",
        "install",
        "yt-dlp",
        "--upgrade"
    ])
    
    
def ensure_git():
    try:
        print("\nEnsuring git...")
        run_cli_command_simple(["git", "--version"])
        print("Git is already installed. Skipping...")
    except subprocess.CalledProcessError:
        print("Git not installed. Installing...")
        run_cli_command_simple(["pkg", "update", "-y"])
        run_cli_command_simple(["pkg", "install", "git", "-y"])
    
    
def ensure_curl():
    try:
        print("\nEnsuring curl...")
        run_cli_command_simple(["curl", "--version"])
        print("curl is already installed. Skipping...")
    except subprocess.CalledProcessError:
        print("Curl not installed. Installing...")
        run_cli_command_simple(["pkg", "update", "-y"])
        run_cli_command_simple(["pkg", "install", "curl", "-y"])
    
    
def ensure_curl_impersonate(force: bool = False):
    print("\nEnsuring curl-impersonate...")
    
    result = subprocess.run(
        ["ls", f"{constants.TERMUX_PREFIX}/lib"],
        capture_output=True,
        text=True
    )
    
    files = [
        "libcurl-impersonate-chrome.so",
        "libcurl-impersonate-chrome.so.4",
        "libcurl-impersonate-chrome.so.4.8.0",
        "libcurl-impersonate.so",
        "libcurl-impersonate.so.4",
        "libcurl-impersonate.so.4.8.0",
    ]
    
    exists = result.stdout.find("\n".join(files)) != -1
    if exists and not force:
        print("curl-impersonate is already installed. Skipping...")
        return
    elif exists and force:
        print("curl-impersonate is already installed. Overwriting...")
    else:
        print("curl-impersonate not installed. Installing...")
        
    install_dir = f"{constants.TERMUX_PREFIX}/curl-impersonate-android"
    include_dir = f"{constants.TERMUX_PREFIX}/include"
    lib_dir = f"{constants.TERMUX_PREFIX}/lib"
    
    if os.path.exists(install_dir):
        try:
            print(f"Removing {install_dir}...")
            run_cli_command_simple(["rm", "-rf", install_dir])
        except Exception as e:
            print(f"Error removing {install_dir}: {str(e)}")
    
    if exists and force:
        try:
            if os.path.exists(include_dir):
                print("Removing old include/curl...")
                run_cli_command_simple(["rm", "-rf", f"{include_dir}/curl"])
            for file in files:
                lib_file = f"{lib_dir}/{file}"
                if os.path.exists(lib_file):
                    print(f"Removing old lib/{file}...")
                    run_cli_command_simple(["rm", lib_file])
        except Exception as e:
            print(f"Error removing old binaries: {str(e)}")
    
    run_cli_command_simple([
        "git",
        "clone",
        "https://github.com/T0chi/curl-impersonate-android.git",
        install_dir
    ])
    
    try:
        run_cli_command_simple(["rm -f", f"{install_dir}/README.md"])
        run_cli_command_simple(["rm -rf", f"{install_dir}/.git"])
        run_cli_command_simple(["cp", "-rf", f"{install_dir}/", f"{constants.TERMUX_PREFIX}/"])
        run_cli_command_simple(["rm", "-rf", install_dir])
    except Exception as e:
        print(f"Error copying curl-impersonate files: {str(e)}")
    
    
def ensure_curl_cffi():
    print("\nEnsuring curl_cffi...")
    run_cli_command_simple([
        "pip",
        "install",
        "curl_cffi"
    ])
    
    
def ensure_termux_api():
    print("\nEnsuring termux-api...")
    run_cli_command_simple([
        "pip",
        "install",
        "termux-api"
    ])
    
    
def ensure_termuxgui():
    print("\nEnsuring termuxgui...")
    run_cli_command_simple([
        "pip",
        "install",
        "termuxgui"
    ])


def ensure_termux_widget():
    shortcut_path = os.path.join(constants.TERMUX_WIDGETS_TASKS_DIR, constants.WIDGET_SCRIPT_NAME)
    
    if os.path.exists(shortcut_path):
        return False

    os.makedirs(constants.TERMUX_WIDGETS_TASKS_DIR, exist_ok=True)
    
    shortcut_content = """#!/data/data/com.termux/files/usr/bin/sh
yt-dlp-termux-gui launch
"""
    
    with open(shortcut_path, "w") as f:
        f.write(shortcut_content)
        
    os.chmod(shortcut_path, 0o755)
    
    return True


def ensure_packages(force: bool = False):
    ensure_git()
    ensure_curl()
    ensure_curl_impersonate(force)
    ensure_ytdlp()
    ensure_curl_cffi()
    ensure_termux_api()
    ensure_termuxgui()

    
def get_image_bytes(image_url: str, size: Literal['thumbnail', 'default']):
    response = requests.get(image_url)
    response.raise_for_status()  # ensure it downloaded successfully
    
    buf_png = BytesIO()
    img = Image.open(BytesIO(response.content))

    if size == "default":
        img.save(buf_png, format="PNG", optimize=True)
        return buf_png.getvalue()
    
    target_ratio = 3 / 2
    width, height = img.size
    current_ratio = width / height

    if current_ratio > target_ratio:
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        right = left + new_width
        top = 0
        bottom = height
    else:
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        bottom = top + new_height
        left = 0
        right = width

    img_cropped = img.crop((left, top, right, bottom))
    img_cropped.save(buf_png, format="PNG", optimize=True)
    png_bytes = buf_png.getvalue()
    
    return png_bytes
