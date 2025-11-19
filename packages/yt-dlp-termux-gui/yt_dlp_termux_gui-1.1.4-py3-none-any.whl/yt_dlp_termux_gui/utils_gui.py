import threading
import logging
from datetime import datetime
import termuxgui as tg


def append_text(logger: logging.Logger, activity: tg.Activity, status_container: tg.LinearLayout, message: str): 
    def create_log():
        threadlock = threading.Lock()
        with threadlock:
            timestamp = datetime.now().strftime("%H:%M:%S")
            try:
                formatted_message = f"[{timestamp}] {message}"
                logger.info(formatted_message)
                text_view = tg.TextView(activity, formatted_message, status_container)
                text_view.settextsize(15)
                text_view.setmargin(10, 'bottom')
                text_view.setclickable(True)
            except Exception as e:
                logger.error(f"[{timestamp}] Failed to append log: {str(e)}") 
    threading.Thread(target=create_log, daemon=True).start()
    

def get_thumbnail_view(activity: tg.Activity, parent: tg.View | None, url: str) -> tg.ImageView:
    from .assets import get_image_bytes
    img = get_image_bytes(url, "thumbnail")
    thumbnail_view = tg.ImageView(activity, parent)
    thumbnail_view.setimage(img)
    thumbnail_view.setbackgroundcolor(0)
    return thumbnail_view
