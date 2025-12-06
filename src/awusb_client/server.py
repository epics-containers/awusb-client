import json
import socket
import threading

from .usbdevice import UsbDevice, get_devices


class CommandServer:
    def __init__(self, host: str = "localhost", port: int = 5000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False

    def handle_list(self) -> list[UsbDevice]:
        """Handle the 'list' command."""
        # TODO: Implement list logic
        result = get_devices()
        return result

    def handle_attach(
        self,
        id: str | None = None,
        bus: str | None = None,
        serial_no: str | None = None,
    ) -> bool:
        """Handle the 'attach' command with optional arguments."""
        # TODO: Implement attach logic
        print(f"Attaching device with id={id}, bus={bus}, serial_no={serial_no}")
        return True

    def _send_response(self, client_socket: socket.socket, response: dict):
        """Send a JSON response to the client."""
        client_socket.sendall(json.dumps(response).encode("utf-8") + b"\n")

    def handle_client(self, client_socket: socket.socket, address):
        """Handle individual client connections."""

        try:
            data = client_socket.recv(1024).decode("utf-8")
            command_data = json.loads(data)

            if not command_data or "command" not in command_data:
                response = {"status": "error", "message": "Empty or invalid command"}
                self._send_response(client_socket, response)
                return

            command = command_data["command"]

            if command == "list":
                print(f"List from: {address}")
                result = self.handle_list()
                data = json.dumps(result)
                response = {"status": "success", "data": result}

            elif command == "attach":
                print(f"Attach from : {address} [{command_data.get('args', {})}]")
                kwargs = command_data.get("args", {})
                result = self.handle_attach(**kwargs)
                response = {"status": "success" if result else "failure"}
                self._send_response(client_socket, response)

            else:
                response = {"status": "error", "message": "Unknown command"}
                self._send_response(client_socket, response)

        except json.JSONDecodeError as e:
            response = {"status": "error", "message": f"Invalid JSON: {str(e)}"}
            self._send_response(client_socket, response)

        except Exception as e:
            response = {"status": "error", "message": str(e)}
            self._send_response(client_socket, response)

        finally:
            client_socket.close()

    def _respond_to_client(self, client_socket, response):
        self._send_response(client_socket, response)

    def start(self):
        """Start the server."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True

        print(f"Server listening on {self.host}:{self.port}")

        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client, args=(client_socket, address)
                )
                client_thread.start()
            except OSError:
                break

    def stop(self):
        """Stop the server."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
