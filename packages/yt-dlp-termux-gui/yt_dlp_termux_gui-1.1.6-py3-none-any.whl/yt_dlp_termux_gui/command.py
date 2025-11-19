from typing import Literal
import os
import logging
import subprocess
import threading
import json
import termuxgui as tg
from . import utils
from . import utils_gui
from . import settings


def get_metadata(url: str) -> dict[Literal['thumbnail_url', 'title', 'uploader', 'duration'], str]:
        result = subprocess.run(
            ["yt-dlp", "--skip-download", "--dump-json", url],
            capture_output=True,
            text=True
        )

        return json.loads(result.stdout)


def prepare(output_dir: str, cookies_file: str, additional_args: list):
    output_dir = os.path.expanduser(output_dir or settings.defaults["Output Directory"])
    cookies_file = os.path.expanduser(
        cookies_file or settings.defaults["Cookies File (optional)"]
    )

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.dirname(cookies_file), exist_ok=True)
    
    cmd = []
    
    if additional_args != []:
        cmd.extend(additional_args)
        
    cmd.extend(["--cookies", cookies_file])
    
    return {"args": cmd, "output_dir": output_dir}


def run_yt_dlp(
    config: list[str],
    enable_logs: bool,
    force_keyframes: bool,
    logs_activity: tg.Activity,
    status_container: tg.LinearLayout,
    logger: logging.Logger,
):
    video_url = config["Video URL"]
    output_dir = config["Output Directory"]
    filename_template = config["Filename Template"]
    start_time = config["Start Time (optional)"]
    end_time = config["End Time (optional)"]
    cookies_file = config["Cookies File (optional)"]
    additional_args: list[str] = config["Additional Arguments"].split(" ")
    
    if not video_url:
        utils_gui.append_text(logger, logs_activity, status_container, 'error', "Error: No video URL provided")
        return

    cmd: list = ["yt-dlp"]
    cmd_prepare = prepare(output_dir, cookies_file, additional_args)
    
    output_dir: str = cmd_prepare["output_dir"]

    if force_keyframes:
        cmd.append("--force-keyframes-at-cuts")
    if enable_logs:
        cmd.append("--verbose")
    if start_time and end_time:
        cmd.extend(["--download-sections", f"{start_time}-{end_time}"])
        
    cmd.extend(cmd_prepare["args"])
    cmd.extend(["-o", f"{output_dir}/${filename_template}"])
    cmd.append(video_url)
        
    utils_gui.append_text(logger, logs_activity, status_container, f"Running command:\n{' '.join(cmd)}")

    def _run():
        try:
            utils_gui.append_text(logger, logs_activity, status_container, "\nRunning...\n")
            def on_stdout(line: str):
                utils_gui.append_text(logger, logs_activity, status_container, line.strip())
            errors = utils.run_cli_command(cmd, on_stdout)
            if (errors):
                utils_gui.append_text(logger, logs_activity, status_container, f"\nCompleted with error(s):\n{errors}")
            else:
                utils_gui.append_text(logger, logs_activity, status_container, "\nCompleted.")
        except Exception as e:
            utils_gui.append_text(logger, logs_activity, status_container, f"Failed to run yt-dlp: {str(e)}")

    threading.Thread(target=_run).start()