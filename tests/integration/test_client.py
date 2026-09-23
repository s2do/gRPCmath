from nmath.client.service import MathClient
from nmath.server.main import create_server
from nmath.server.service import MathService
from nmath.cli.main import main

def test_client_ping():
    server, port = create_server(port=0)
    server.start()

    try:
        client = MathClient(f"127.0.0.1:{port}")

        response = client.ping("hello")

        assert response == "pong: hello"
    finally:
        server.stop(grace=0)

def test_cli_ping(capsys, monkeypatch):
    server, port = create_server(port=0)
    server.start()

    try:
        monkeypatch.setattr(
            "sys.argv",
            [
                "nmath",
                "ping",
                "--server",
                f"127.0.0.1:{port}",
                "--message",
                "cli test",
            ],
        )

        main()

        captured = capsys.readouterr()

        assert captured.out.strip() == "pong: cli test"
    finally:
        server.stop(grace=0)