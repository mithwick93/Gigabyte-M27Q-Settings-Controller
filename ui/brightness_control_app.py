from logging import Logger

import rumps

from core.m27q import MonitorControl


class BrightnessControlApp(rumps.App):
    def __init__(self, monitor_control: MonitorControl, logger: Logger):
        super(BrightnessControlApp, self).__init__(name="Gigabyte M27Q Settings Controller", icon="resources/icon.png")
        self._monitor_control = monitor_control
        self._logger = logger

        self._create_slider_menu_item('brightness')
        self._create_slider_menu_item('contrast')
        self._create_slider_menu_item('vibrance')
        self._create_slider_menu_item('sharpness')
        self._create_slider_menu_item('volume')

    def _create_slider_menu_item(self, name: str) -> None:
        property_name = getattr(MonitorControl, name.upper())
        value = getattr(self._monitor_control, f'get_{name.lower()}')()
        menu_item = rumps.MenuItem(title=f"{name.capitalize()}: {value}")
        slider = rumps.SliderMenuItem(
            value=value,
            min_value=property_name.minimum,
            max_value=property_name.maximum,
            callback=lambda sender: self._adjust_slider_property(name, sender),
            dimensions=(200, 25)
        )
        self.menu.add(menu_item)
        self.menu.add(slider)
        self.menu.add(rumps.separator)
        setattr(self, f'{name.lower()}_menu_item', menu_item)
        setattr(self, f'{name.lower()}_slider', slider)

    def _adjust_slider_property(self, name: str, sender: rumps.SliderMenuItem) -> None:
        value = int(sender.value)
        self._logger.debug(f"Set {name.capitalize()} to: {value}")
        getattr(self, f'{name.lower()}_menu_item').title = f"{name.capitalize()}: {value}"
        getattr(self._monitor_control, f'set_{name.lower()}')(value)
