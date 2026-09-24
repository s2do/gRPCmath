import socket
import threading
import os
import time

from nmath.bridge.main import serve


class FakeMathClient:
    def ping(self, message: str) -> str:
        return f"pong: {message}"

    def close(self) -> None:
        pass

def wait_for_socket(socket_path: str, timeout: float = 2.0) -> None:
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        if __import__("os").path.exists(socket_path):
            return
        time.sleep(0.01)

    raise AssertionError(
        f"Unix socket did not appear within {timeout} seconds: "
        f"{socket_path}"
    )


def test_unix_socket_ping(tmp_path):
    socket_path = str(tmp_path / "nmath-test.sock")

    client = FakeMathClient()

    thread = threading.Thread(
        target=serve,
        kwargs={
            "socket_path": socket_path,
            "server_address": "unused",
            "client": client,
        },
        daemon=True,
    )
    thread.start()

    wait_for_socket(socket_path)

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.connect(socket_path)
        sock.sendall(b"hello\n")

        response = sock.recv(4096)

    assert response.decode().strip() == "pong: hello"