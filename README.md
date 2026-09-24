# nmath

nmath is a Python-based mathematical execution engine with a gRPC interface and a Unix domain socket bridge.

## Current status

Milestone M1 establishes the Unix domain socket bridge and implements the first mathematical execution functionality (`BinaryOperation`) backed by NumPy. 

## Requirements

- Python >= 3.11
- pip
- a virtual environment is recommended

## Installation

Create and activate a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install the project and development dependencies:

    pip install -e ".[dev]"

(Optional) Create a `.env` file in the project root to override default network configurations:

    NMATH_SOCKET=/tmp/nmath.sock
    NMATH_HOST=127.0.0.1
    NMATH_PORT=50051

## Run the server

Start the gRPC backend server:

    nmath-server

In a separate terminal, start the Unix socket bridge to handle client requests:

    nmath-bridge

## Usage & Expression Syntax

The `nmath` CLI communicates with the bridge over a Unix domain socket. It accepts binary operations consisting of two numbers and one operator (`+`, `-`, `*`, `/`).

You can pass the expression as a direct argument:

    nmath "3 + 2"
    nmath "10.5 / 2"
    nmath "-5 * 2.1"

Alternatively, you can pipe expressions directly to the CLI via `stdin`:

    echo "15 - 5" | nmath

Or pipe directly to the socket bypassing the Python CLI entirely using `nc` or `socat`:

    echo "3+2" | nc -U /tmp/nmath.sock

**Diagnostic Fallback:** If you pass an invalid expression (e.g., `nmath "hello"`), the bridge will fall back to a `Ping` request to verify if the gRPC backend is reachable.

## Testing

Run the complete test suite (Unit, Integration, E2E):

    pytest

Run tests with coverage:

    pytest --cov=nmath --cov-report=term-missing

## Protocol

The gRPC API is defined in:

    proto/math.proto

The API currently exposes:

    MathService.Ping(PingRequest) -> PingResponse
    MathService.BinaryOperation(BinaryOperationRequest) -> BinaryOperationResponse

## Repository structure

    proto/       Protocol Buffer definitions
    src/nmath/   Application source code
    tests/       Automated tests
    tools/       Development utilities
    docs/        Project documentation

## Development

Protocol Buffer and gRPC Python files are generated from `proto/math.proto`.

To regenerate them:

    python tools/generate_proto.py