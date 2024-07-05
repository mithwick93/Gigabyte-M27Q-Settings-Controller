from logging import Logger

import rumps

from core.m27q import MonitorControl


class BrightnessControlApp(rumps.App):
    def __init__(self, monitor_control: MonitorControl, logger: Logger):
        self._monitor_control = monitor_control
        self._logger = logger
        super(BrightnessControlApp, self).__init__(name="Gigabyte M27Q SC", icon="resources/icon.png")

        # brightness
        brightness_value = self._monitor_control.get_brightness()
        self.brightness_menu_item = rumps.MenuItem(title=f"Brightness: {brightness_value}")
        self.brightness_slider = rumps.SliderMenuItem(
            value=brightness_value,
            min_value=MonitorControl.BRIGHTNESS.minimum,
            max_value=MonitorControl.BRIGHTNESS.maximum,
            callback=self.adjust_brightness,
            dimensions=(200, 30)
        )

        # contrast
        contrast_value = self._monitor_control.get_contrast()
        self.contrast_menu_item = rumps.MenuItem(title=f"Contrast: {contrast_value}")
        self.contrast_slider = rumps.SliderMenuItem(
            value=contrast_value,
            min_value=MonitorControl.CONTRAST.minimum,
            max_value=MonitorControl.CONTRAST.maximum,
            callback=self.adjust_contrast,
            dimensions=(200, 30)
        )

        # vibrance
        vibrance_value = self._monitor_control.get_vibrance()
        self.vibrance_menu_item = rumps.MenuItem(title=f"Vibrance: {vibrance_value}")
        self.vibrance_slider = rumps.SliderMenuItem(
            value=vibrance_value,
            min_value=MonitorControl.COLOR_VIBRANCE.minimum,
            max_value=MonitorControl.COLOR_VIBRANCE.maximum,
            callback=self.adjust_vibrance,
            dimensions=(200, 30)
        )

        # sharpness
        sharpness_value = self._monitor_control.get_sharpness()
        self.sharpness_menu_item = rumps.MenuItem(title=f"Sharpness: {sharpness_value}")
        self.sharpness_slider = rumps.SliderMenuItem(
            value=sharpness_value,
            min_value=MonitorControl.SHARPNESS.minimum,
            max_value=MonitorControl.SHARPNESS.maximum,
            callback=self.adjust_sharpness,
            dimensions=(200, 30)
        )

        self.menu = [
            self.brightness_menu_item,
            self.brightness_slider,
            rumps.separator,
            self.contrast_menu_item,
            self.contrast_slider,
            rumps.separator,
            self.vibrance_menu_item,
            self.vibrance_slider,
            rumps.separator,
            self.sharpness_menu_item,
            self.sharpness_slider,
            rumps.separator,
        ]

    def adjust_brightness(self, sender):
        brightness_value = int(sender.value)
        self._logger.debug("Set brightness to: " + str(brightness_value))
        self.brightness_menu_item.title = f"Brightness: {brightness_value}"
        self._monitor_control.set_brightness(brightness_value)

    def adjust_contrast(self, sender):
        contrast_value = int(sender.value)
        self._logger.debug("Set contrast to: " + str(contrast_value))
        self.contrast_menu_item.title = f"Contrast: {contrast_value}"
        self._monitor_control.set_contrast(contrast_value)

    def adjust_vibrance(self, sender):
        vibrance_value = int(sender.value)
        self._logger.debug("Set vibrance to: " + str(vibrance_value))
        self.vibrance_menu_item.title = f"Vibrance: {vibrance_value}"
        self._monitor_control.set_vibrance(vibrance_value)

    def adjust_sharpness(self, sender):
        sharpness_value = int(sender.value)
        self._logger.debug("Set sharpness to: " + str(sharpness_value))
        self.sharpness_menu_item.title = f"Sharpness: {sharpness_value}"
        self._monitor_control.set_sharpness(sharpness_value)
