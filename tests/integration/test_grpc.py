from nmath.client.service import MathClient
from nmath.server.main import create_server


def test_client_ping():
    server, port = create_server(port=0)
    server.start()

    client = MathClient(f"127.0.0.1:{port}")

    try:
        response = client.ping("hello")

        assert response == "pong: hello"
    finally:
        client.close()
        server.stop(grace=0)