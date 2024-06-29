import sys

from m27q import MonitorControl

if __name__ == "__main__":
    if sys.platform != "darwin":
        raise Exception("This script works only on MacOS.")

    with MonitorControl() as m:
        print("Brightness: ", m.get_brightness())
        print("Contrast: ", m.get_contrast())
        print("Sharpness: ", m.get_sharpness())
        print("Volume: ", m.get_volume())
        print("KVM Status: ", m.get_kvm_status())