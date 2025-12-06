import json
import socket

from awusb_client.usbdevice import UsbDevice


def send_request(sock, request):
    sock.sendall(json.dumps(request).encode("utf-8"))

    response = sock.recv(4096).decode("utf-8")
    decoded = json.loads(response)

    return decoded


def list_devices(server_host="localhost", server_port=5000) -> list[UsbDevice]:
    """
    Request list of available USB devices from the server.

    Args:
        server_host: Server hostname or IP address
        server_port: Server port number

    Returns:
        List of UsbDevice instances
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((server_host, server_port))

        request = {"command": "list"}
        response = send_request(sock, request)

        return [UsbDevice.model_validate(device) for device in response.get("data", [])]


def attach_device(id, server_host="localhost", server_port=5000):
    """
    Request to attach a USB device from the server.

    Args:
        device_id: ID of the device to attach
        server_host: Server hostname or IP address
        server_port: Server port number

    Returns:
        Dictionary containing the result of the attach operation
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((server_host, server_port))

        request = {"command": "attach", "id": id}
        print(f"Request: {request}")
        response = send_request(sock, request)

        return response
