import sys

from core.m27q import MonitorControl
from ui.brightness_control_app import BrightnessControlApp
from util.logger import get_logger

if __name__ in {"__main__", "__mp_main__"}:
    main_logger = get_logger(__name__)

    if sys.platform != "darwin":
        error_message = "This script works only on MacOS."
        main_logger.error(error_message)
        raise Exception(error_message)

    with MonitorControl() as monitor_Control:
        BrightnessControlApp(monitor_Control, main_logger).run()
