import re
import subprocess
from dataclasses import dataclass


@dataclass
class UsbDevice:
    bus_id: str
    vendor: str
    product: str
    details: dict[str, str]

    def __repr__(self):
        return (
            f"UsbDevice(bus_id={self.bus_id!r}, "
            f"vendor={self.vendor!r}, product={self.product!r})"
        )


def get_udev_details(bus_id: str) -> dict[str, str]:
    """
    Retrieve udev details for a given USB device bus ID.

    Args:
        bus_id (str): The bus ID of the USB device.
    Returns:
        dict: A dictionary of udev properties for the device.
    """
    result = subprocess.run(
        ["udevadm", "info", "--query=all", f"--name=/dev/bus/usb/{bus_id}"],
        capture_output=True,
        text=True,
        check=True,
    )
    details: dict[str, str] = {}
    pattern = r"E: (\w+)=(.+)"
    for match in re.finditer(pattern, result.stdout):
        details[match.group(1)] = match.group(2)
    return details


def get_devices() -> list[UsbDevice]:
    """
    Retrieve a list of connected USB devices that can be shared over usbip.

    Returns:
        list: A list of connected USB devices.
    """
    # Call the system CLI usbip list -lp and parse the output
    result = subprocess.run(
        ["usbip", "list", "-pl"],
        capture_output=True,
        text=True,
        check=True,
    )
    pattern = r"busid=([^#]+)#usbid=([0-9a-f]+):([0-9a-f]+)#"

    devices: list[UsbDevice] = []
    for match in re.finditer(pattern, result.stdout, re.DOTALL):
        details = get_udev_details(match.group(1))
        devices.append(
            UsbDevice(
                bus_id=match.group(1),
                vendor=match.group(2),
                product=match.group(3),
                details=details,
            )
        )
    return devices
