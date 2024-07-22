# For Gigabyte M27Q KVM connected over USB
#
# Based on: https://gist.github.com/wadimw/4ac972d07ed1f3b6f22a101375ecac41

import typing as t
from dataclasses import dataclass
from time import sleep

#  pip install pyusb
import usb.core
import usb.util

from util.alert import show_alert
from util.logger import get_logger


@dataclass
class BasicProperty:
    minimum: int
    maximum: int
    message_a: int
    message_b: int = 0

    def clamp(self, v: int):
        return max(self.minimum, min(self.maximum, v))


@dataclass
class EnumProperty:
    allowed: t.List[int]
    message_a: int
    message_b: int = 0

    def clamp(self, v: int):
        if v not in self.allowed:
            raise Exception(f"Only allowed values: {self.allowed}")
        return v


Property = t.Union[BasicProperty, EnumProperty]


def display_alert(e: Exception):
    show_alert(
        "Error",
        repr(e) + ".\nTry restarting the app",
        "Dismiss",
        "warning"
    )


class MonitorControl:
    BRIGHTNESS = BasicProperty(0, 100, 0x10, 0x00)
    CONTRAST = BasicProperty(0, 100, 0x12, 0x00)
    SHARPNESS = BasicProperty(0, 10, 0x87, 0x00)
    TEMPERATURE = EnumProperty([4, 5, 6], 0x14, 0x00)  # 4 - cool, 5 - normal, 6 - warm
    VIBRANCE = BasicProperty(0, 20, 0xe0, 0x8)

    VOLUME = BasicProperty(0, 100, 0x62, 0x00)

    BLUE_LIGHT_REDUCTION = BasicProperty(0, 10, 0xe0, 0x0b)
    BLACK_EQUALIZER = BasicProperty(0, 10, 0xe0, 0x02)

    def __init__(self):
        self._logger = get_logger(__name__)
        self._VID = 0x2109  # (VIA Labs, Inc.)
        self._PID = 0x8883  # USB Billboard Device
        self._dev = None
        self._usb_delay = 50 / 1000  # 50 ms sleep after every usb op
        self._min_brightness = 0
        self._max_brightness = 100
        self._min_volume = 0
        self._max_volume = 100
        self._bm_request_type_read = 0xC0
        self._bm_request_type_write = 0x40

    # Find USB device, set config
    def __enter__(self):
        # Find device
        self._logger.info("Init MonitorControl")

        self._dev = usb.core.find(idVendor=self._VID, idProduct=self._PID)
        if self._dev is None:
            error_message = f"Device VID_{self._VID} & PID_{self._PID} not found"
            self._logger.error(error_message)
            raise IOError(error_message)

        # Detach kernel driver
        self._had_driver = False
        try:
            if self._dev.is_kernel_driver_active(0):
                self._dev.detach_kernel_driver(0)
                self._had_driver = True
        except usb.USBError:
            pass

        # Set config (1 as discovered with Wireshark)
        # self._dev.set_configuration(1)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._logger.info("Exit MonitorControl")

        # Reattach kernel driver
        if self._had_driver:
            self._dev.attach_kernel_driver(0)
        # Release device
        usb.util.dispose_resources(self._dev)

    def get_black_equalizer(self) -> int:
        return self.__get_property(MonitorControl.BLACK_EQUALIZER)

    def set_black_equalizer(self, black_equalizer: int) -> None:
        self.__set_property(MonitorControl.BLACK_EQUALIZER, black_equalizer)

    def get_blue_light_reduction(self) -> int:
        return self.__get_property(MonitorControl.BLUE_LIGHT_REDUCTION)

    def set_blue_light_reduction(self, blue_light_reduction: int) -> None:
        self.__set_property(MonitorControl.BLUE_LIGHT_REDUCTION, blue_light_reduction)

    def get_brightness(self) -> int:
        return self.__get_property(MonitorControl.BRIGHTNESS)

    def set_brightness(self, brightness: int) -> None:
        self.__set_property(MonitorControl.BRIGHTNESS, brightness)

    def get_contrast(self) -> int:
        return self.__get_property(MonitorControl.CONTRAST)

    def set_contrast(self, contrast: int) -> None:
        self.__set_property(MonitorControl.CONTRAST, contrast)

    def get_sharpness(self) -> int:
        return self.__get_property(MonitorControl.SHARPNESS)

    def set_sharpness(self, sharpness: int) -> None:
        self.__set_property(MonitorControl.SHARPNESS, sharpness)

    def get_temperature(self) -> int:
        return self.__get_property(MonitorControl.TEMPERATURE)

    def set_temperature(self, temperature: int) -> None:
        self.__set_property(MonitorControl.TEMPERATURE, temperature)

    def get_vibrance(self) -> int:
        return self.__get_property(MonitorControl.VIBRANCE)

    def set_vibrance(self, vibrance: int) -> None:
        self.__set_property(MonitorControl.VIBRANCE, vibrance)

    def get_volume(self) -> int:
        return self.__get_property(MonitorControl.VOLUME)

    def set_volume(self, volume: int) -> None:
        self.__set_property(MonitorControl.VOLUME, volume)

    def __usb_read(
            self,
            b_request: int,
            w_value: int,
            w_index: int,
            msg_length: int
    ):
        data = self._dev.ctrl_transfer(
            self._bm_request_type_read, b_request, w_value, w_index, msg_length
        )
        sleep(self._usb_delay)
        return data

    def __usb_write(
            self,
            b_request: int,
            w_value: int,
            w_index: int,
            message: bytes
    ):
        if not self._dev.ctrl_transfer(
                self._bm_request_type_write, b_request, w_value, w_index, message
        ) == len(message):
            error_message = "Transferred message length mismatch"
            self._logger.error(error_message)
            raise IOError(error_message)
        sleep(self._usb_delay)

    def __get_osd(self, data: t.List[int]):
        self.__usb_write(
            b_request=178,
            w_value=0,
            w_index=0,
            message=bytearray(
                [0x6E, 0x51, 0x81 + len(data), 0x01]
            ) + bytearray(data),
        )
        data = self.__usb_read(
            b_request=162,
            w_value=0,
            w_index=111,
            msg_length=12
        )
        return data[10]

    def __set_osd(self, data: bytearray):
        self.__usb_write(
            b_request=178,
            w_value=0,
            w_index=0,
            message=bytearray([0x6E, 0x51, 0x81 + len(data), 0x03] + data),
        )

    def __get_property(self, property_name: Property):
        try:
            return self.__get_osd(
                [property_name.message_a, property_name.message_b]
            )
        except Exception as e:
            display_alert(e)
            self._logger.error(e)

    def __set_property(self, property_name: Property, value: int):
        try:
            self.__set_osd([
                property_name.message_a,
                property_name.message_b,
                property_name.clamp(value)
            ])
        except Exception as e:
            display_alert(e)
            self._logger.error(e)
