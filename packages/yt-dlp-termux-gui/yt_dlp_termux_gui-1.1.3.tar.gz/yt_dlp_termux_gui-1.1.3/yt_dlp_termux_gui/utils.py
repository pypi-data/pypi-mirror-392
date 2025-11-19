import os
import sys
import re
import stat
import logging
import subprocess
import shutil
from typing import Literal, Callable
from . import assets
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


def run_cli_command_simple(cmd: list[str], cwd: str = None):
    subprocess.run(cmd, check=True, cwd=cwd)


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


def assign_permissions_to_path(path: str, perms: list[Literal["read", "write", "execute"]] = ["read", "write", "execute"]):
    mode = 0
    if "read" in perms:
        mode |= stat.S_IRUSR
    if "write" in perms:
        mode |= stat.S_IWUSR
    if "execute" in perms:
        mode |= stat.S_IXUSR
    os.chmod(path, mode)
    

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
    print("\nEnsuring platform...")
    termux_env_variables = ensure_termux_env_variables()
    if not termux_env_variables:
        return False
    return termux_env_variables["PREFIX"].startswith(constants.TERMUX_PREFIX)
    
    
def ensure_ytdlp():
    print("\nEnsuring yt-dlp...")
    run_cli_command_simple([
        "pip",
        "install",
        "yt-dlp"
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
    curl_dir = f"{constants.TERMUX_PREFIX}/include/curl"
    lib_dir = f"{constants.TERMUX_PREFIX}/lib"
    
    if os.path.exists(install_dir):
        try:
            shutil.rmtree(install_dir)
        except Exception as e:
            print(f"Error removing {install_dir}: {str(e)}")
    
    if exists and force:
        try:
            if os.path.exists(curl_dir):
                print("Removing old include/curl...")
                shutil.rmtree(curl_dir)
            for file in files:
                lib_file = f"{lib_dir}/{file}"
                if os.path.exists(lib_file):
                    print(f"Removing old lib/{file}...")
                    os.remove(lib_file)
        except Exception as e:
            print(f"Error removing old binaries: {str(e)}")
    
    run_cli_command_simple([
        "git",
        "clone",
        "https://github.com/T0chi/curl-impersonate-android.git",
        install_dir
    ])
    
    assign_permissions_to_path(install_dir, ["read", "write"])
    
    try:
        shutil.copytree(f"{install_dir}/include/curl", curl_dir)
        for file in files:
            lib_file_src = f"{install_dir}/lib/{file}"
            lib_file_dest = f"{lib_dir}/{file}"
            if os.path.exists(lib_file_src):
                os.rename(lib_file_src, lib_file_dest)
        shutil.rmtree(install_dir)
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


def ensure_termux_widget(force: bool = False):
    shortcut_path = os.path.join(constants.TERMUX_WIDGETS_DIR, constants.WIDGET_SCRIPT_NAME)
    shortcut_icon_path = f"{os.path.join(constants.TERMUX_WIDGETS_ICONS_DIR, constants.WIDGET_SCRIPT_NAME)}.png"
    
    shortcut_file_exists = os.path.exists(shortcut_path)
    shortcut_icon_file_exists = os.path.exists(shortcut_icon_path)
    
    if not force and shortcut_file_exists and shortcut_icon_file_exists:
        return False

    for p in [
        constants.TERMUX_WIDGETS_DIR,
        constants.TERMUX_WIDGETS_ICONS_DIR,
        constants.TERMUX_WIDGETS_TASKS_DIR,
    ]:
        try:
            os.makedirs(p, exist_ok=True)
            assign_permissions_to_path(p)
        except Exception as e:
            print(f"Error setting permissions for {p}: {str(e)}")
    
    if not shortcut_file_exists or force:
        shortcut_content = """#!"""
        shortcut_content += f"{constants.TERMUX_PREFIX}/bin/sh"
        shortcut_content += "\n\nyt-dlp-termux-gui launch\n"
        
        try:
            with open(shortcut_path, "w") as f:
                f.write(shortcut_content)
        except Exception as e:
            print(f"Error writing {shortcut_path}: {str(e)}")
            
    if not shortcut_icon_file_exists or force:
        try:
            assets.copy_resource(f"icons/{constants.WIDGET_SCRIPT_NAME}.png", shortcut_icon_path)
        except Exception as e:
            print(f"Error copying resource {shortcut_icon_path}: {str(e)}")
    return True


def ensure_packages(force: bool = False):
    ensure_git()
    ensure_curl()
    ensure_curl_impersonate(force)
    ensure_ytdlp()
    ensure_curl_cffi()
    ensure_termux_api()
    ensure_termuxgui()
