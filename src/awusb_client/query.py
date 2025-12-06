import re
import subprocess
from dataclasses import dataclass

import usb.core
import usb.util


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


def _filter_on_port_numbers(
    device: usb.core.Device, port_numbers: tuple[int, ...]
) -> bool:
    device_ports = getattr(device, "port_numbers", ())
    return device_ports == port_numbers


def get_udev_details(id: str, product: str, bus_id: str) -> dict[str, str]:
    """
    Retrieve udev details for a given USB device bus ID using pyusb.

    Args:
        bus_id (str): The bus ID of the USB device (format: "bus-port").
    Returns:
        dict: A dictionary of udev properties for the device.
    """

    # Split bus_id into bus and port numbers
    bus_str, port_str = bus_id.split("-")
    bus = int(bus_str)
    port_numbers = tuple(int(p) for p in port_str.split("."))

    # # Find the device
    # device = usb.core.find(idVendor=int(id, 16), idProduct=int(product, 16))
    device = usb.core.find(
        idVendor=int(id, 16),
        idProduct=int(product, 16),
        bus=bus,
        custom_match=lambda d: _filter_on_port_numbers(d, port_numbers),
    )

    assert type(device) is usb.core.Device, "Device not found"

    details: dict[str, str] = {}
    details["BUSNUM"] = f"{device.bus:03d}"
    details["DEVNUM"] = f"{device.address:03d}"
    details["DEVNAME"] = f"/dev/bus/usb/{device.bus:03d}/{device.address:03d}"
    # use getattr for fields not know to the type checker)
    details["PORTNUMS"] = ".".join(str(p) for p in getattr(device, "port_numbers", []))
    details["ID_VENDOR_ID"] = f"{getattr(device, 'idVendor', 0):04x}"
    details["ID_MODEL_ID"] = f"{getattr(device, 'idProduct', 0):04x}"

    try:
        details["ID_VENDOR"] = getattr(device, "manufacturer", "")
        details["ID_MODEL"] = getattr(device, "product", "")
        details["ID_SERIAL_SHORT"] = getattr(device, "serial_number", "")
    except (ValueError, usb.core.USBError):
        # May fail if device requires specific permissions
        pass

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
        busid, vendor, product = match.groups()
        details = get_udev_details(vendor, product, busid)
        devices.append(UsbDevice(busid, vendor, product, details))
    return devices
