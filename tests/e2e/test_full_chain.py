import socket
import threading
import os
import time

from nmath.server.main import create_server
from nmath.bridge.main import serve as serve_bridge


def wait_for_socket(socket_path: str, timeout: float = 2.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if os.path.exists(socket_path):
            return
        time.sleep(0.01)
    raise AssertionError(f"Unix socket timeout: {socket_path}")


def test_full_chain_execution(tmp_path):
    # 1. Start echter gRPC Server auf dynamischem Port
    grpc_server, port = create_server(port=0)
    grpc_server.start()
    server_address = f"127.0.0.1:{port}"

    # 2. Start echte Bridge mit Unix Socket
    socket_path = str(tmp_path / "e2e.sock")
    bridge_thread = threading.Thread(
        target=serve_bridge,
        kwargs={
            "socket_path": socket_path,
            "server_address": server_address,
        },
        daemon=True,
    )
    bridge_thread.start()
    wait_for_socket(socket_path)

    try:
        # 3. Simuliere CLI (Client-Socket verbindet sich zur Bridge)
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect(socket_path)
            sock.sendall(b"15.5 / 2.0\n")
            response = sock.recv(4096).decode().strip()
            
            assert response == "7.75"
            
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect(socket_path)
            sock.sendall(b"10 / 0\n")
            response = sock.recv(4096).decode().strip()
            
            assert response == "error: division by zero"

    finally:
        grpc_server.stop(grace=0)