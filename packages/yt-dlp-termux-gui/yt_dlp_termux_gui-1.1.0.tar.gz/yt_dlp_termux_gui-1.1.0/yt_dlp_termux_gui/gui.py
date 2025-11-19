from typing import Literal
import sys
import subprocess
import threading
import traceback
import logging
from datetime import datetime
import termuxgui as tg
from . import utils
from . import utils_gui
from . import assets
from . import command
from . import constants
from . import settings
    
    
def get_timestamp():
    return datetime.now().strftime("%H:%M:%S")
    
    
def print_msg(logger: logging.Logger, message: str, level: Literal["debug", "info", "warning", "error", "critical"] = "debug"):
    logger = getattr(logger, level, "debug")
    logger(f"[{get_timestamp()}] {message}")
    
    
def print_error_toast(logger: logging.Logger, connection: tg.Connection, message: str = None):
    verbose = not logger.disabled
    connection.toast(f"An error occurred{verbose and ' (check Termux logs)' or ''}" if message is None else message)
    
    
def print_event_error(
    error: Exception,
    logger: logging.Logger,
    connection: tg.Connection,
    event_name: str,
    message: str = None
):
    msg = f"GUI Event '{event_name}' error: {str(error)}" if message is None else message
    print_msg(logger, msg, "error")
    print_error_toast(logger, connection)

def handle_lifecycle_events(logger: logging.Logger, connection: tg.Connection, event: tg.Event):
    if event.type == tg.Event.create:
        try:
            print_msg(logger, "Starting GUI...")
        except Exception as e:
            print_event_error(e, logger, connection, "create")
            
    if event.type == tg.Event.start:
        try:
            print_msg(logger, "GUI gained focus")
        except Exception as e:
            print_event_error(e, logger, connection, "start")
            
    if event.type == tg.Event.resume:
        try:
            print_msg(logger, "GUI is active")
        except Exception as e:
            print_event_error(e, logger, connection, "resume")
            
    if event.type == tg.Event.pause:
        try:
            print_msg(logger, "GUI is inactive")
        except Exception as e:
            print_event_error(e, logger, connection, "pause")
            
    if event.type == tg.Event.stop:
        try:
            print_msg(logger, "GUI lost focus")
        except Exception as e:
            print_event_error(e, logger, connection, "stop")
            
    if event.type == tg.Event.destroy:
        try:
            print_msg(logger, "GUI was destroyed")
            if event.value["finishing"]:
                logging.shutdown()
                sys.exit()
        except Exception as e:
            print_event_error(e, logger, connection, "destroy")
            
    if event.type == tg.Event.userleavehint:
        try:
            print_msg(logger, "User hints to go back")
        except Exception as e:
            print_event_error(e, logger, connection, "userleavehint")
            
    if event.type == tg.Event.pipchanged:
        try:
            print_msg(logger, "Picture-in-picture mode changed")
        except Exception as e:
            print_event_error(e, logger, connection, "pipchanged")
            
    if event.type == tg.Event.config:
        try:
            print_msg(logger, "State changed")
        except Exception as e:
            print_event_error(e, logger, connection, "config")
            
    if event.type == tg.Event.back:
        try:
            print_msg(logger, "User pressed back")
        except Exception as e:
            print_event_error(e, logger, connection, "back")
                

def get_gui_logger(disable: bool = False):
    level = utils.get_logger_level()
    gui_logger = utils.create_logger(level)
    if disable:
        gui_logger.disabled = True
    return gui_logger


def build_gui(
    connection: tg.Connection,
    logger: logging.Logger,
    logger_activity: logging.Logger,
    logger_init: logging.Logger
):
    threadlock = threading.Lock()
                            
    print_msg(logger, "Loading existing settings...")
    existing_settings = settings.load_settings()
    
    print_msg(logger, "Initializing GUI...")
    activity = tg.Activity(connection)
    activity.interceptbackbutton(True)
    
    print_msg(logger, "Building GUI...")
    root_container = tg.LinearLayout(activity)

    print_msg(logger_init, "GUI: Initializing container...")
    scroll_container = tg.NestedScrollView(activity, root_container)
    container = tg.LinearLayout(activity, scroll_container)
    container.setmargin(10, 'top')
    container.setmargin(10, 'right')
    container.setmargin(80, 'bottom')
    container.setmargin(10, 'left')

    print_msg(logger_init, "GUI: Initializing title...")
    title = tg.TextView(activity, constants.WIDGET_TITLE, container)
    title.settextsize(25)
    
    title_desc = tg.TextView(activity, "by tochiResources", container)
    title_desc.settextsize(10)
    title_desc.setmargin(20, 'bottom')
    
    print_msg(logger_init, "GUI: Initializing metadata container...")
    metadata_container_scroll = tg.NestedScrollView(activity, container)
    metadata_container = tg.LinearLayout(activity, metadata_container_scroll)
    metadata_container.setheight(200)
    metadata_container.setmargin(10, 'bottom')
    
    paste_btn: tg.Button | None = None
    input_fields: dict[str, tg.EditText] = {}
    inputs: dict[str, str | list[str]] = {label: placeholder for label, placeholder in settings.defaults.items()}
    
    input_field_index = 0
    textareas = ["Filename Template"]
    print_msg(logger_init, "GUI: Initializing input fields...")
    for (label, placeholder) in inputs.items():
        print_msg(logger_init, f"GUI: Initializing label #{input_field_index + 1} -> \"{label}\"...")
        input_field_label = tg.TextView(activity, label, container)
        input_field_label.settextsize(18)
        input_field_label.setmargin(6, 'top')
        
        print_msg(logger_init, "GUI: Initializing field...")
        height = tg.View.WRAP_CONTENT if label in textareas else None
        input_text = existing_settings.get(label, placeholder)
        input_fields[label] = tg.EditText(activity, input_text, container, True)
        input_fields[label].settextsize(16)
        input_fields[label].setmargin(2, 'top')
        if height:
            input_fields[label].setheight(height)
        
        if label == "Video URL":
            print_msg(logger_init, "GUI: Initializing clipboard button...")
            paste_btn = tg.Button(activity, "📋 Paste URL from clipboard", container)
            paste_btn.setmargin(6, 'bottom')
            input_field_index += 1
            continue
        
        input_fields[label].setmargin(6, 'bottom')
        input_field_index += 1

    print_msg(logger_init, "GUI: Initializing checkbox #1...")
    force_keyframes_cbx = tg.Checkbox(activity, "Force keyframes at cuts", container)
    force_keyframes_cbx.setmargin(6, 'bottom')
    force_keyframes_cbx.settextsize(16)
    force_keyframes_cbx.setchecked(existing_settings.get("Force Keyframes at Cuts", True))
    
    print_msg(logger_init, "GUI: Initializing checkbox #2...")
    verbose_cbx = tg.Checkbox(activity, "Verbose logging", container)
    verbose_cbx.setmargin(6, 'bottom')
    verbose_cbx.settextsize(16)
    verbose_cbx.setchecked(existing_settings.get("Verbose", False))
    
    print_msg(logger_init, "GUI: Initializing button #1...")
    reset_settings_btn = tg.Button(activity, "Reset Settings", container)
    
    print_msg(logger_init, "GUI: Initializing button row...")
    run_row = tg.LinearLayout(activity, container, False)
    
    print_msg(logger_init, "GUI: Initializing button #2...")
    exit_btn = tg.Button(activity, "Exit", run_row)
    
    print_msg(logger_init, "GUI: Initializing button #3...")
    run_btn = tg.Button(activity, "Run", run_row)

    print_msg(logger_init, "GUI: Initializing status container...")
    status_text_container = tg.LinearLayout(activity, container)
    status_text_title = tg.TextView(activity, "Status", status_text_container)
    status_text_title.settextsize(18)
    status_text_title.setmargin(10, 'top')
    status_text_title.setmargin(5, 'bottom')
            
    def handle_ui_events(event: tg.Event):
        if event.type == tg.Event.text:
            input_id = event.value["id"]
            
            if input_id == input_fields["Video URL"]:
                try:
                    media_url = event.value["text"]
                    if utils.is_valid_url(media_url):
                        def update_metadata():
                            with threadlock:
                                print_msg(logger, "GUI: Fetching metadata...")
                                metadata = command.get_metadata(media_url)
                                media_thumbnail_url = metadata.get("thumbnail")
                                media_uploader = metadata.get("uploader")
                                media_title = metadata.get("title")
                                media_duration = metadata.get("duration")
                                
                                metadata_container.clearchildren()
                                
                                if media_thumbnail_url:
                                    thumbnail_view = utils_gui.get_thumbnail_view(activity, metadata_container, media_thumbnail_url)
                                    thumbnail_view.setmargin(6, 'bottom')
                                
                                if media_uploader:
                                    media_uploader_view = tg.TextView(activity, f"Uploader: {media_uploader}", metadata_container)
                                    media_uploader_view.settextsize(14)
                                    media_uploader_view.setmargin(2, 'bottom')
                                
                                if media_title:
                                    media_title_view = tg.TextView(activity, f"Title: {media_title}", metadata_container)
                                    media_title_view.settextsize(14)
                                    media_title_view.setmargin(2, 'bottom')
                                
                                if media_duration:
                                    media_duration_view = tg.TextView(activity, f"Duration: {media_duration}", metadata_container)
                                    media_duration_view.settextsize(14)
                                
                        threading.Thread(target=update_metadata, daemon=True).start()
                except Exception as e:
                    print_event_error(e, logger, connection, "text")
                
        if event.type == tg.Event.click:
            btn_id = event.value["id"]

            if btn_id == paste_btn:
                try:
                    def paste_clipboard():
                        with threadlock:
                            try:
                                clip = subprocess.check_output(["termux-clipboard-get"], text=True).strip()
                                if clip and "\n" not in clip:
                                    input_fields["Video URL"].settext(clip)
                                else:
                                    utils_gui.append_text(logger, activity, status_text_container, "Clipboard is empty or multi-line")
                            except Exception as _e:
                                print_event_error(_e, logger, connection, "click", f"Clipboard unavailable: {str(_e)}")
                        
                    threading.Thread(target=paste_clipboard, daemon=True).start()
                except Exception as e:
                    print_event_error(e, logger, connection, "click")

            if btn_id == reset_settings_btn:
                try:
                    def reset_settings():
                        with threadlock:
                            utils_gui.append_text(logger, activity, status_text_container, "Resetting settings...")
                            settings.reset_settings()
                            inputs_defaults = settings.defaults
                            for item in input_fields.items():
                                label = item[0]
                                if label == "Video URL":
                                    continue
                                input_fields[label].settext(inputs_defaults[label])
                            utils_gui.append_text(logger, activity, status_text_container, "Settings has been reset!")
                        
                    threading.Thread(target=reset_settings, daemon=True).start()
                except Exception as e:
                    print_event_error(e, logger, connection, "click")

            if btn_id == run_btn:
                try:
                    def download_media():
                            with threadlock:
                                try:
                                    status_text_container.clearchildren()
                                    sanitized_inputs = {label: value.gettext().strip() for label, value in input_fields.items()}
                                    command.run_yt_dlp(
                                        sanitized_inputs,
                                        verbose_cbx.checked,
                                        force_keyframes_cbx.checked,
                                        activity,
                                        status_text_container,
                                        logger,
                                    )
                                    settings.save_settings(sanitized_inputs)
                                except Exception as e:
                                    utils_gui.append_text(logger, activity, status_text_container, f"GUI error: {str(e)}")
                        
                    threading.Thread(target=download_media, daemon=True).start()
                except Exception as e:
                    print_event_error(e, logger, connection, "click")

            if btn_id == exit_btn:
                try:
                    utils_gui.append_text(logger, activity, status_text_container, "Exiting...")
                    logging.shutdown()
                    sys.exit(0)
                except Exception as e:
                    print_event_error(e, logger, connection, "click")

    print_msg(logger_init, "GUI: Initializing event listeners...")
    
    for event in connection.events():
        handle_lifecycle_events(logger_activity, connection, event)
        handle_ui_events(event)
            
def launch_gui(
    logger: logging.Logger,
    activity_logs: bool = True,
    init_logs: bool = False
):
    try:
        print_msg(logger, f"GUI logs in Termux is {'enabled' if not logger.disabled else 'disabled'}")
        print_msg(logger, f"GUI activity logging is {'enabled' if activity_logs else 'disabled'}")
        print_msg(logger, f"GUI initialization logging is {'enabled' if init_logs else 'disabled'}")
            
        if not utils.detect_termux():
            print_msg(logger, "This script must run inside Termux. Make sure '$HOME' and '$PREFIX' environment variables are set.", "error")
            logging.shutdown()
            sys.exit(1)
            
        logger.debug("Initializing Activity logger...")
        logger_activity = get_gui_logger(not activity_logs)
        
        logger.debug("Initializing Initialization logger...")
        logger_init = get_gui_logger(not init_logs)
            
        logger.debug("Creating connection...")
        
        with tg.Connection() as connection:
            build_gui(connection, logger, logger_activity, logger_init)
            
        logging.debug("Exiting GUI...")
        logging.shutdown()
        sys.exit(0)
        
    except Exception:
        e = traceback.format_exc()
        print_msg(logger, f"GUI critical error: {e}", "critical")
        logging.shutdown()
        sys.exit(1)