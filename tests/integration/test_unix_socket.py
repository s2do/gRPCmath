import socket
import threading
import os
import time
import pytest

from nmath.bridge.main import serve


class FakeMathClient:
    def ping(self, message: str) -> str:
        return f"pong: {message}"

    def binary_operation(self, left: float, right: float, operator: str) -> str:
        if operator == "+": return f"{left + right:g}"
        if operator == "-": return f"{left - right:g}"
        if operator == "*": return f"{left * right:g}"
        if operator == "/": return f"{left / right:g}" if right != 0 else "error: division by zero"
        return "error: unknown"

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

    assert response.decode().strip() == "error: unknown expression. Server is reachable (pong: hello)"

def test_unix_socket_binary_operation(tmp_path):
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
        # Teste Regex-Parsing (inklusive Leerzeichen)
        sock.sendall(b"  3.5   +  2 \n")
        response = sock.recv(4096)

    assert response.decode().strip() == "5.5"

@pytest.mark.parametrize("expression, expected", [
    # Valid regex matches (routed to binary_operation)
    (b"10 - 5\n", "5"),
    (b" -3.5 * -2 \n", "7"),
    (b"+10 / +2\n", "5"),
    (b".5 + .5\n", "1"),
    (b"  100   *   2  \n", "200"),
    
    # Invalid regex matches (routed to Ping fallback)
    (b"3 ^ 2\n", "error: unknown expression. Server is reachable (pong: 3 ^ 2)"),
    (b"3 + 2 + 1\n", "error: unknown expression. Server is reachable (pong: 3 + 2 + 1)"),
    (b"3.1.4 + 2\n", "error: unknown expression. Server is reachable (pong: 3.1.4 + 2)"),
    (b"3a + 2\n", "error: unknown expression. Server is reachable (pong: 3a + 2)"),
    (b"3 +\n", "error: unknown expression. Server is reachable (pong: 3 +)"),
    (b"+ 3\n", "error: unknown expression. Server is reachable (pong: + 3)"),
])
def test_unix_socket_regex_handling(tmp_path, expression, expected):
    socket_path = str(tmp_path / "nmath-regex.sock")
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
        sock.sendall(expression)
        
        response = sock.recv(4096).decode().strip()

    assert response == expected