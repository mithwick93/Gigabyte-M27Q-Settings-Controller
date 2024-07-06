import typing as t
from logging import Logger

import rumps

from core.m27q import MonitorControl, Property


class BrightnessControlApp(rumps.App):
    def __init__(self, monitor_control: MonitorControl, logger: Logger):
        super(BrightnessControlApp, self).__init__(name="Gigabyte M27Q Settings Controller", icon="resources/icon.png")
        self._monitor_control = monitor_control
        self._logger = logger

        self._create__slider_menu_item('brightness', MonitorControl.BRIGHTNESS, self.adjust_brightness)
        self._create__slider_menu_item('contrast', MonitorControl.CONTRAST, self.adjust_contrast)
        self._create__slider_menu_item('vibrance', MonitorControl.COLOR_VIBRANCE, self.adjust_vibrance)
        self._create__slider_menu_item('sharpness', MonitorControl.SHARPNESS, self.adjust_sharpness)

    def adjust_brightness(self, sender: rumps.SliderMenuItem) -> None:
        self._adjust_property('brightness', sender)

    def adjust_contrast(self, sender: rumps.SliderMenuItem) -> None:
        self._adjust_property('contrast', sender)

    def adjust_vibrance(self, sender: rumps.SliderMenuItem) -> None:
        self._adjust_property('vibrance', sender)

    def adjust_sharpness(self, sender: rumps.SliderMenuItem) -> None:
        self._adjust_property('sharpness', sender)

    def _create__slider_menu_item(self, name: str, property_name: Property, callback: t.Callable) -> None:
        value = getattr(self._monitor_control, f'get_{name.lower()}')()
        menu_item = rumps.MenuItem(title=f"{name.capitalize()}: {value}")
        slider = rumps.SliderMenuItem(
            value=value,
            min_value=property_name.minimum,
            max_value=property_name.maximum,
            callback=callback,
            dimensions=(200, 25)
        )
        self.menu.add(menu_item)
        self.menu.add(slider)
        self.menu.add(rumps.separator)
        setattr(self, f'{name.lower()}_menu_item', menu_item)
        setattr(self, f'{name.lower()}_slider', slider)

    def _adjust_property(self, name: str, sender: rumps.SliderMenuItem) -> None:
        value = int(sender.value)
        self._logger.debug(f"Set {name.capitalize()} to: {value}")
        getattr(self, f'{name.lower()}_menu_item').title = f"{name.capitalize()}: {value}"
        getattr(self._monitor_control, f'set_{name.lower()}')(value)
