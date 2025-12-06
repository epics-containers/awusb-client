import re
import subprocess

import usb.core
import usb.util


class UsbDevice:
    def __init__(self, bus_id: str, vendor_id: str, product_id: str):
        self.bus_id = bus_id
        self.vendor_id = vendor_id
        self.product_id = product_id
        # Split bus_id into bus and port numbers
        bus_str, port_str = bus_id.split("-")
        self.bus = int(bus_str)
        self.port_numbers = tuple(int(p) for p in port_str.split("."))

        # Find the device
        device = usb.core.find(
            idVendor=int(vendor_id, 16),
            idProduct=int(product_id, 16),
            bus=self.bus,
            custom_match=lambda d: self._filter_on_port_numbers(d, self.port_numbers),
        )
        assert type(device) is usb.core.Device, "Device not found"

        self.device_name = f"/dev/bus/usb/{device.bus:03d}/{device.address:03d}"
        try:
            self.serial = getattr(device, "serial_number", "")
        except (ValueError, usb.core.USBError):
            self.serial = ""

        # it is very hard to get vendor and product strings due to permissions
        # so call out to lsusb which has no issue extracting them
        self.description = "unknown"
        try:
            lsusb_result = subprocess.run(
                ["lsusb", "-s", f"{device.bus:03d}:{device.address:03d}"],
                capture_output=True,
                text=True,
                check=True,
            )
            lsusb_output = lsusb_result.stdout.strip()
            desc_match = re.search(rf".*{vendor_id}:{product_id} (.+)$", lsusb_output)
            if desc_match:
                self.description = desc_match.group(1)
        except subprocess.CalledProcessError:
            pass  # leave description as "unknown"

    def __repr__(self):
        ser = f" [serial_no={self.serial}]" if self.serial else ""
        return (
            f"id={self.vendor_id}:{self.product_id} bus={self.bus_id:13} "
            f"dev={self.device_name:20} "
            f"desc={self.description}{ser}"
        )

    @classmethod
    def _filter_on_port_numbers(
        cls, device: usb.core.Device, port_numbers: tuple[int, ...]
    ) -> bool:
        """
        Custom filter function to match USB devices based on port numbers.

        e.g. When the bus ID is "1-2.3.4",
            the bus is 1 and the port numbers are (2, 3, 4).
        """
        device_ports = getattr(device, "port_numbers", ())
        return device_ports == port_numbers


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
        devices.append(UsbDevice(busid, vendor, product))
    return devices
