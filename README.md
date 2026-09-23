# nmath

nmath is a Python-based mathematical execution engine with a gRPC interface.

## Current status

Milestone M0 establishes the basic client/server architecture and verifies
gRPC connectivity through a simple `Ping` operation.

M0 does not yet provide mathematical execution functionality.

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

## Run the server

Start the gRPC server:

    nmath-server

The server listens on:

    127.0.0.1:50051

## Test connectivity

In another terminal:

    nmath ping

Expected output:

    pong: hello

A custom message can be supplied:

    nmath ping --message "hello nmath"

## Testing

Run the complete test suite:

    pytest

Run tests with coverage:

    pytest --cov=nmath --cov-report=term-missing

## Protocol

The gRPC API is defined in:

    proto/math.proto

M0 currently exposes:

    MathService.Ping(PingRequest) -> PingResponse

## Repository structure

    proto/       Protocol Buffer definitions
    src/nmath/   Application source code
    tests/       Automated tests
    tools/       Development utilities
    docs/        Project documentation

## Development

Protocol Buffer and gRPC Python files are generated from
`proto/math.proto`.

To regenerate them:

    python tools/generate_proto.py