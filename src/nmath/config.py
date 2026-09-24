import os

from dotenv import load_dotenv


load_dotenv()

DEFAULT_SOCKET = "/tmp/nmath.sock"
DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = "50051"

NMATH_SOCKET = os.getenv(
    "NMATH_SOCKET",
    DEFAULT_SOCKET,
    )

NMATH_HOST = os.getenv(
    "NMATH_HOST", 
    DEFAULT_IP,
    )

NMATH_PORT = int(
    os.getenv(
        "NMATH_PORT", 
        DEFAULT_PORT,
        )
    )

# Pre-formatted string for gRPC connections (e.g., "127.0.0.1:50051")
NMATH_SERVER_ADDRESS = f"{NMATH_HOST}:{NMATH_PORT}"