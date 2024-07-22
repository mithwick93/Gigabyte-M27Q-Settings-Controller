import sys

from core.m27q import MonitorControl
from ui.brightness_control_app import BrightnessControlApp
from util.alert import show_alert
from util.logger import get_logger

if __name__ in {"__main__", "__mp_main__"}:
    main_logger = get_logger(__name__)

    if sys.platform != "darwin":
        error_message = "This script works only on MacOS."
        main_logger.error(error_message)
        raise Exception(error_message)

    try:
        with MonitorControl() as monitor_Control:
            BrightnessControlApp(monitor_Control, main_logger).run()
    except Exception as e:
        show_alert("Critical Error", repr(e), "Exit", "critical")
        raise e
