import json
import socket


def list_devices(server_host="localhost", server_port=5000):
    """
    Request list of available USB devices from the server.

    Args:
        server_host: Server hostname or IP address
        server_port: Server port number

    Returns:
        List of dictionaries containing device information
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((server_host, server_port))

        request = {"command": "list"}
        sock.sendall(json.dumps(request).encode("utf-8"))

        response = sock.recv(4096).decode("utf-8")
        return json.loads(response)


def attach_device(device_id, server_host="localhost", server_port=5000):
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

        request = {"command": "attach", "device_id": device_id}
        sock.sendall(json.dumps(request).encode("utf-8"))

        response = sock.recv(4096).decode("utf-8")
        return json.loads(response)
