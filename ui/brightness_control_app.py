import threading
import time
from logging import Logger

import rumps

from core.m27q import MonitorControl


def get_capitalized_setting(setting: str):
    return setting.replace('_', ' ').capitalize()


class BrightnessControlApp(rumps.App):
    def __init__(self, monitor_control: MonitorControl, logger: Logger):
        super(BrightnessControlApp, self).__init__(name="Gigabyte M27Q Settings Controller", icon="resources/icon.png")
        self._monitor_control = monitor_control
        self._logger = logger
        self._settings = [
            'brightness',
            'contrast',
            'vibrance',
            'sharpness',
            'black_equalizer',
            'blue_light_reduction',
            'volume'
        ]

        self._setting_data = {}
        self._auto_setting_refresh = False
        self._auto_setting_refresh_interval_seconds = 10

        for setting in self._settings:
            self._create_slider_menu_item(setting)

        auto_refresh_toggle_menu_item = rumps.MenuItem(
            title=self._get_auto_refresh_toggle_menu_item_title(),
            callback=self._toggle_auto_refresh
        )
        self._auto_refresh_toggle_menu_item = auto_refresh_toggle_menu_item
        self.menu.add(auto_refresh_toggle_menu_item)

        self._polling_thread = threading.Thread(target=self._poll_monitor_settings, daemon=True)
        self._polling_thread.start()
        self._update_ui_timer = rumps.Timer(self._update_ui_from_polling, self._auto_setting_refresh_interval_seconds)
        self._update_ui_timer.start()

    def _create_slider_menu_item(self, setting: str) -> None:
        property_name = getattr(MonitorControl, setting.upper())
        value = getattr(self._monitor_control, f'get_{setting}')()
        capitalized_setting_name = get_capitalized_setting(setting)
        menu_item = rumps.MenuItem(title=f"{capitalized_setting_name}: {value}")
        slider = rumps.SliderMenuItem(
            value=value,
            min_value=property_name.minimum,
            max_value=property_name.maximum,
            callback=lambda sender: self._adjust_slider_property(setting, sender),
            dimensions=(200, 25)
        )
        self.menu.add(menu_item)
        self.menu.add(slider)
        self.menu.add(rumps.separator)
        self._setting_data[setting] = value
        setattr(self, f'_{setting}_menu_item', menu_item)
        setattr(self, f'_{setting}_slider', slider)

    def _adjust_slider_property(self, setting: str, sender: rumps.SliderMenuItem) -> None:
        value = int(sender.value)
        capitalized_setting_name = get_capitalized_setting(setting)
        self._logger.debug(f"Set {capitalized_setting_name} to: {value}")
        getattr(self, f'_{setting}_menu_item').title = f"{capitalized_setting_name}: {value}"
        getattr(self._monitor_control, f'set_{setting}')(value)

    def _toggle_auto_refresh(self, _):
        self._auto_setting_refresh = not self._auto_setting_refresh
        title = self._get_auto_refresh_toggle_menu_item_title()
        self._logger.debug("Set " + title)
        self._auto_refresh_toggle_menu_item.title = title

    def _poll_monitor_settings(self):
        while True:
            time.sleep(self._auto_setting_refresh_interval_seconds)
            if not self._auto_setting_refresh:
                continue

            self._logger.debug("Polling monitor settings...")
            for setting in self._settings:
                current_value = getattr(self._monitor_control, f'get_{setting}')()
                self._setting_data[setting] = current_value

    def _update_ui_from_polling(self, _):
        if not self._auto_setting_refresh:
            return

        for setting, value in self._setting_data.items():
            menu_item = getattr(self, f'_{setting}_menu_item')
            slider = getattr(self, f'_{setting}_slider')
            self._update_ui(setting, value, menu_item, slider)

    def _update_ui(self, setting: str, value: int, menu_item: rumps.MenuItem, slider: rumps.SliderMenuItem):
        if value == slider.value:
            return

        capitalized_setting_name = get_capitalized_setting(setting)
        self._logger.debug(f"Updating {capitalized_setting_name} to: {value}")
        menu_item.title = f"{capitalized_setting_name}: {value}"
        slider.value = value

    def _get_auto_refresh_toggle_menu_item_title(self):
        return f"Auto Refresh: {'ON' if self._auto_setting_refresh else 'OFF'}"
