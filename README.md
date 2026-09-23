# gRPC-Connected NumPy Math Engine

A small, test-driven mathematical execution system that accepts a restricted LaTeX-like mathematical language at the CLI, compiles it into a typed intermediate representation (IR), translates that representation into gRPC requests, and executes the operations remotely using NumPy.

The project starts deliberately small:

```text
CLI
  ↓
LaTeX parser
  ↓
Math AST / IR
  ↓
Execution planner
  ↓
gRPC
  ↓
NumPy server
  ↓
Result
```

The long-term goal is to evolve this from a simple remote calculator into a small **distributed numerical execution engine** with a math-language frontend.

---

## 1. Vision

The central idea is to separate **mathematical notation**, **mathematical meaning**, **wire representation**, and **numerical execution**.

```text
LaTeX        = input / presentation language
AST / IR     = mathematical meaning
protobuf     = network representation
NumPy        = execution backend
gRPC         = transport / remote execution
```

The server should **not** understand LaTeX.

Instead, the client side parses and compiles mathematical expressions into a stable, typed representation. The server receives that representation and executes it.

This separation is important because it lets the project evolve independently:

- the frontend can become more expressive without changing the numerical runtime;
- the runtime can change from NumPy to another backend without changing the parser;
- a future Python, JSON, or other frontend can reuse the same IR;
- unit tests can isolate parsing, compilation, networking, and numerical execution.

---

# 2. High-Level Architecture

```text
                         Local process
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│  CLI                                                          │
│  nmath "2 + 3"                                                │
│       │                                                       │
│       ▼                                                       │
│  LaTeX parser / normalizer                                    │
│       │                                                       │
│       ▼                                                       │
│  Typed Math IR / AST                                          │
│       │                                                       │
│       ▼                                                       │
│  Execution planner                                            │
│       │                                                       │
│       ▼                                                       │
│  gRPC client / bridge                                         │
│                                                               │
└───────────────────────────┬───────────────────────────────────┘
                            │
                          gRPC
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                        NumPy Server                           │
│                                                               │
│  gRPC service                                                 │
│       │                                                       │
│       ▼                                                       │
│  Operation dispatcher                                         │
│       │                                                       │
│       ▼                                                       │
│  NumPy runtime                                                │
│       │                                                       │
│       ▼                                                       │
│  Result / structured error                                    │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

A key design rule is:

> **Do not make the NumPy server parse LaTeX.**

The server should receive a typed mathematical representation.

---

# 3. Core Design Principle: Treat This as a Compiler

The project is easier to reason about as a tiny compiler pipeline than as a "LaTeX-to-gRPC parser".

```text
                Frontend
                  │
            LaTeX input
                  │
                  ▼
             Lexer / Parser
                  │
                  ▼
              Math AST
                  │
                  ▼
             Typed IR
                  │
                  ▼
          Execution planner
                  │
                  ▼
              protobuf
                  │
                  ▼
                gRPC
                  │
                  ▼
              NumPy runtime
```

This creates three major software layers.

## Frontend

Responsible for:

```text
LaTeX → AST
```

Examples:

```latex
2 + 3
```

```latex
\frac{2+3}{4}
```

```latex
\sin(2) + 3^2
```

The frontend should initially support only a deliberately small subset of LaTeX.

## Compiler

Responsible for:

```text
AST → typed IR → execution plan
```

This is where the system can eventually perform:

- syntax validation;
- type validation;
- shape validation;
- constant folding;
- common-subexpression elimination;
- operation fusion;
- execution planning;
- graph optimization.

## Runtime

Responsible for:

```text
execution plan → NumPy computation
```

The runtime can be accessed:

- locally for unit tests and debugging;
- remotely through gRPC for integration and distributed execution.

---

# 4. Start With a Very Small Language

Do **not** attempt to support arbitrary LaTeX.

LaTeX is a huge typesetting language and supporting all mathematical syntax would create unnecessary complexity.

Instead, define a small mathematical DSL represented using LaTeX-like notation.

The first language could support:

```text
NUMBER
+
-
*
/
()
```

Examples:

```latex
2 + 3
```

```latex
10 - 4
```

```latex
6 * 7
```

```latex
8 / 2
```

```latex
(2 + 3) * 4
```

Later, add mathematical notation such as:

```latex
\frac{a}{b}
```

```latex
a^b
```

```latex
\sqrt{a}
```

```latex
\sin(a)
```

```latex
\cos(a)
```

```latex
\log(a)
```

Eventually, vector and matrix notation can be introduced.

---

# 5. The Mathematical Intermediate Representation

The IR is the most important abstraction in the system.

A useful conceptual model is:

```text
Expression
├── Scalar
├── Complex
├── Tensor
├── UnaryOp
└── BinaryOp
```

For a simple expression:

```latex
2 + 3
```

the IR could be:

```text
BinaryOp(
    operation = ADD,
    left = Scalar(2),
    right = Scalar(3)
)
```

For:

```latex
(2 + 3) * 4
```

the tree becomes:

```text
Multiply
├── Add
│   ├── Scalar(2)
│   └── Scalar(3)
└── Scalar(4)
```

The parser creates the IR.

The gRPC bridge serializes the IR.

The server executes the IR.

This means the IR should not contain parser-specific details such as raw LaTeX strings.

---

# 6. Proposed Value Model

A future generic numerical value should support different mathematical types.

```text
Value
├── Scalar
├── Complex
└── Tensor
```

with metadata such as:

```text
dtype
shape
```

For example:

```text
Value
    type: tensor
    dtype: float64
    shape: [1024, 1024]
```

A protobuf representation could conceptually look like:

```protobuf
message Value {
    oneof kind {
        double scalar = 1;
        Complex complex = 2;
        Tensor tensor = 3;
    }
}
```

This makes it possible for the same operation to work across different value types.

For example:

```text
ADD
```

could represent:

```text
scalar + scalar
vector + vector
matrix + matrix
```

provided the type and shape rules allow it.

Prefer a generic operation model over separate APIs such as:

```text
AddScalar()
AddVector()
AddMatrix()
```

A single semantic `ADD(Value, Value)` is easier to extend.

---

# 7. Proposed gRPC API

For the first milestone, keep the service simple.

Conceptually:

```protobuf
enum BinaryOp {
    ADD = 0;
    SUB = 1;
    MUL = 2;
    DIV = 3;
}

message Scalar {
    double value = 1;
}

message BinaryRequest {
    BinaryOp op = 1;
    Scalar left = 2;
    Scalar right = 3;
}

message ScalarResponse {
    double value = 1;
}

service MathService {
    rpc Ping(PingRequest) returns (PingResponse);
    rpc Binary(BinaryRequest) returns (ScalarResponse);
}
```

This does not have to be the final protocol.

The protocol should evolve together with the IR.

---

# 8. Why Start With a `Ping` Milestone?

Before implementing mathematical behavior, verify that the infrastructure works.

Example:

```bash
nmath ping
```

Expected:

```text
server: OK
```

This isolates:

- CLI problems;
- process startup problems;
- gRPC connection problems;
- protobuf generation problems;
- server lifecycle problems

from mathematical correctness.

---

# 9. Milestone Plan

## M0 — gRPC Connectivity

### Goal

Establish a working CLI → gRPC server connection.

### Example

```bash
nmath ping
```

### Expected behavior

```text
server: OK
```

### Tests

- CLI starts;
- client can connect;
- gRPC service responds;
- server can be started independently;
- connection failure produces a useful error.

---

## M1 — Basic Scalar Math With Two Operands

### Goal

Support basic binary scalar arithmetic.

Supported operations:

```text
+
-
*
/
```

Examples:

```latex
2 + 3
```

```latex
5 - 2
```

```latex
4 * 7
```

```latex
8 / 2
```

### Data flow

```text
2 + 3
  ↓
Add(2, 3)
  ↓
BinaryRequest(ADD, 2, 3)
  ↓
gRPC
  ↓
5
```

### Parser behavior

```text
"2 + 3"
→ Add(2, 3)
```

```text
"5 - 2"
→ Sub(5, 2)
```

```text
"4 * 7"
→ Mul(4, 7)
```

```text
"8 / 2"
→ Div(8, 2)
```

### Invalid syntax

These should fail predictably:

```text
2 +
```

```text
foo
```

```text
2 ++ 3
```

### Error semantics

Define explicitly what happens for:

```text
1 / 0
```

Do not allow low-level Python exceptions to become the public API.

---

# 10. M1 TDD Strategy

The project should be developed vertically.

For the feature:

```latex
2 + 3
```

write tests for each boundary.

## Parser test

```text
"2 + 3"
→ Add(2, 3)
```

## IR test

Verify the semantic node:

```text
BinaryOp(
    operation = ADD,
    left = Scalar(2),
    right = Scalar(3)
)
```

## Bridge test

Mock the gRPC client and verify that the IR becomes:

```text
BinaryRequest(
    op = ADD,
    left = 2,
    right = 3
)
```

## Runtime test

Verify:

```text
ADD(2, 3) = 5
```

## Integration test

Run the complete path:

```text
CLI
→ parser
→ IR
→ bridge
→ gRPC
→ NumPy server
→ result
```

Expected:

```text
5
```

This is the first complete vertical slice of the system.

---

# 11. M2 — Recursive Scalar Expressions

Once two-operand expressions work, introduce nested expressions.

Examples:

```latex
(2 + 3) * 4
```

```latex
\frac{2+3}{5}
```

```latex
(10 - 2) / (3 + 1)
```

The parser must now create recursive expression trees.

For:

```latex
\frac{3^2 + \sqrt{16}}{2}
```

the structure could conceptually be:

```text
Divide
├── Add
│   ├── Pow(3, 2)
│   └── Sqrt(16)
└── 2
```

The exact AST representation can differ, but the semantic structure should be explicit.

---

# 12. M3 — Rich Scalar Mathematics

Add more unary and binary operations.

## Binary operations

```text
+
-
*
/
^
```

## Unary operations

```text
sqrt
sin
cos
tan
exp
log
```

Example:

```latex
\frac{\sin(2) + 3^2}{4}
```

The language is now becoming a small mathematical expression language.

This milestone should focus on:

- recursive parsing;
- operator precedence;
- associativity;
- unary expressions;
- numeric semantics;
- predictable errors.

---

# 13. Complex Numbers

Complex numbers can be added as a separate type-system milestone.

Example:

```latex
(2 + 3i)(4 - i)
```

The value model then becomes:

```text
Scalar
Complex
Tensor
```

The parser and compiler should distinguish:

```text
2
```

from:

```text
2 + 3i
```

This should be treated as a type-system extension rather than mixed into the parser without a clear model.

---

# 14. M4 — Vector Math

This is the point where NumPy becomes especially useful.

Example:

```latex
[1,2,3] + [4,5,6]
```

Result:

```text
[5,7,9]
```

The runtime now needs values with:

```text
dtype
shape
data
```

For example:

```text
Tensor<float64>
shape = [3]
```

### Important vector tests

Valid:

```text
[1,2,3] + [4,5,6]
```

Invalid:

```text
[1,2,3] + [4,5]
```

Also test:

- empty vectors;
- scalar/vector operations;
- dtype conversion;
- NaN;
- infinity;
- shape compatibility;
- unsupported operations.

---

# 15. Broadcasting

NumPy supports broadcasting, but the project should decide whether to inherit all NumPy broadcasting rules immediately.

For the first vector milestone, it may be better to make shape compatibility explicit and conservative.

For example:

```text
[1,2,3] + [4,5,6]
```

is clearly valid.

But:

```text
[1,2,3] + [4,5]
```

should produce a structured shape error unless broadcasting semantics have explicitly been implemented.

Later, broadcasting can become a deliberate compiler/runtime feature.

---

# 16. M5 — Matrices and General Tensors

Once vectors are supported, extend the same `Tensor` abstraction to matrices and higher-dimensional arrays.

Example matrix notation:

```latex
\begin{bmatrix}
1 & 2 \\
3 & 4
\end{bmatrix}
```

The IR does not need separate vector and matrix operation classes if both are tensors.

Conceptually:

```text
Tensor
    dtype = float64
    shape = [2, 2]
```

This naturally leads to:

```text
vector
matrix
3D tensor
N-D tensor
```

being instances of the same fundamental numerical value model.

---

# 17. M6 — Complete Execution Graphs

The initial prototype may execute an expression as multiple RPC calls.

For:

```latex
(2 + 3) * 4
```

a naïve implementation could do:

```text
RPC 1: ADD(2, 3)
RPC 2: MUL(result, 4)
```

This is easy to implement and useful as a first step.

However, many RPC round trips will become inefficient for large expressions.

The longer-term architecture should send a complete computation graph in one request.

For example:

```text
node 0 = CONST(2)
node 1 = CONST(3)
node 2 = ADD(0,1)
node 3 = CONST(4)
node 4 = MUL(2,3)

root = 4
```

The server can then execute the complete graph.

Conceptually:

```protobuf
message Expression {
    repeated Node nodes = 1;
    uint32 root = 2;
}
```

This design is much closer to a numerical execution engine.

---

# 18. Execution Graph Benefits

Once expressions are represented as graphs, future optimizations become possible.

Examples:

```text
constant folding
common-subexpression elimination
operation fusion
caching
parallel execution
batching
```

For example:

```latex
(2+3)^2 + (2+3)^3
```

could initially calculate `2+3` twice.

A later compiler could transform it into:

```text
t0 = 2 + 3
t1 = t0^2
t2 = t0^3
t3 = t1 + t2
```

The same IR therefore becomes a foundation for optimization.

---

# 19. Error Model

The public API should use structured mathematical errors rather than leaking Python exceptions.

A useful error taxonomy is:

```text
INVALID_SYNTAX
UNSUPPORTED_OPERATION
TYPE_MISMATCH
SHAPE_MISMATCH
DIVISION_BY_ZERO
INVALID_VALUE
SERVER_ERROR
```

Examples:

### Syntax error

```text
2 +
```

### Type error

```text
scalar + unsupported_object
```

### Shape error

```text
[1,2,3] + [4,5]
```

### Numerical error

```text
1 / 0
```

Errors should be stable enough that clients can handle them programmatically.

---

# 20. CLI Design

Keep the CLI intentionally simple.

Basic evaluation:

```bash
nmath "2 + 3"
```

Result:

```text
5
```

More complex:

```bash
nmath "\frac{2+3}{5}"
```

Result:

```text
1
```

Specify a server:

```bash
nmath --server localhost:50051 "2 + 3"
```

A debug mode is very useful during development.

For example:

```bash
nmath --debug "\frac{2+3}{5}"
```

could show:

```text
Input:
  \frac{2+3}{5}

AST:
  DIV(ADD(2,3),5)

Plan:
  node0 = CONST(2)
  node1 = CONST(3)
  node2 = ADD(0,1)
  node3 = CONST(5)
  node4 = DIV(2,3)

Result:
  1
```

This makes parser and compiler behavior observable.

---

# 21. Suggested Repository Layout

```text
nmath/
├── pyproject.toml
├── README.md
│
├── proto/
│   └── math.proto
│
├── src/
│   └── nmath/
│       ├── cli/
│       │   └── main.py
│       │
│       ├── parser/
│       │   ├── lexer.py
│       │   └── parser.py
│       │
│       ├── ir/
│       │   ├── nodes.py
│       │   └── types.py
│       │
│       ├── compiler/
│       │   └── planner.py
│       │
│       ├── bridge/
│       │   └── grpc_client.py
│       │
│       └── server/
│           ├── service.py
│           └── numpy_runtime.py
│
└── tests/
    ├── unit/
    │   ├── test_parser.py
    │   ├── test_ir.py
    │   ├── test_compiler.py
    │   └── test_numpy_runtime.py
    │
    ├── contract/
    │   └── test_grpc_api.py
    │
    └── integration/
        └── test_end_to_end.py
```

The exact package names are flexible; the important part is keeping the boundaries visible.

---

# 22. TDD Development Loop

Each feature should follow the same process:

```text
1. Define mathematical behavior
2. Write failing parser tests
3. Write failing IR tests
4. Write failing bridge tests
5. Write failing runtime tests
6. Implement the smallest change
7. Add an end-to-end integration test
8. Refactor
```

The TDD emphasis should be on **behavioral contracts**, not implementation details.

For example, this is a good acceptance test:

```python
def test_add_two_scalars():
    result = execute(r"2 + 3")
    assert result == 5
```

And a remote integration test:

```python
def test_add_two_scalars_over_grpc():
    result = execute_remote(r"2 + 3")
    assert result == 5
```

These answer different questions:

```text
execute()
    ↓
Does the mathematical system work?

execute_remote()
    ↓
Does the mathematical system work across the network?
```

---

# 23. Testing Layers

The project should contain several test classes.

## Unit Tests

Test one component at a time:

```text
lexer
parser
AST / IR
type system
planner
runtime
```

These should be fast and deterministic.

## Contract Tests

Verify that:

```text
IR ↔ protobuf
```

remains compatible.

These tests help detect accidental protocol changes.

## Integration Tests

Run:

```text
CLI
→ parser
→ IR
→ planner
→ gRPC
→ server
→ NumPy
```

against a real test server.

## End-to-End Tests

Treat the complete CLI command as the public interface:

```bash
nmath "2 + 3"
```

and verify:

```text
stdout
exit code
stderr
```

This gives confidence that refactoring internal components does not break the user-facing behavior.

---

# 24. Suggested Initial Test Matrix

## Scalar arithmetic

| Input | Expected |
|---|---:|
| `2 + 3` | `5` |
| `5 - 2` | `3` |
| `4 * 7` | `28` |
| `8 / 2` | `4` |

## Precedence

| Input | Expected |
|---|---:|
| `2 + 3 * 4` | `14` |
| `(2 + 3) * 4` | `20` |

## Nested functions

| Input | Expected |
|---|---:|
| `\frac{2+3}{5}` | `1` |
| `3^2` | `9` |
| `\sqrt{16}` | `4` |

## Invalid input

| Input | Expected |
|---|---|
| `2 +` | syntax error |
| `foo` | syntax error |
| `2 ++ 3` | syntax error |
| `1 / 0` | defined numerical error |

## Vectors

| Input | Expected |
|---|---|
| `[1,2,3] + [4,5,6]` | `[5,7,9]` |
| `[1,2,3] + [4,5]` | shape error |

The final expected representation should be defined precisely in tests rather than assumed from Python's string formatting.

---

# 25. Proposed Milestone Roadmap

```text
M0  Connectivity
    └── CLI → gRPC → Ping

M1  Basic scalar binary operations
    └── + - * /

M2  Recursive scalar expressions
    └── parentheses, precedence, nested expressions

M3  Rich scalar mathematics
    └── powers, sqrt, sin, cos, exp, log

M4  Complex numbers
    └── scalar + complex + complex operations

M5  Vectors / tensors
    └── NumPy arrays, dtype, shape

M6  Matrices
    └── matrix-specific and tensor operations

M7  Complete execution graphs
    └── one gRPC request per expression

M8  Graph optimization
    └── folding, CSE, fusion, batching, caching
```

Milestones can overlap, but each should have a clear acceptance boundary.

---

# 26. Architectural Evolution

The system should eventually support multiple frontends.

```text
                ┌── LaTeX frontend
                │
                ├── Python API
                │
                ├── CLI
                │
                └── JSON / other frontend
                         │
                         ▼
                      Math IR
                         │
                   ┌─────┴─────┐
                   ▼           ▼
             gRPC runtime   Local runtime
                   │
                   ▼
                 NumPy
```

This is an important long-term goal.

The project should not become tightly coupled to the first CLI syntax.

---

# 27. Why the IR Matters So Much

Consider:

```latex
(2 + 3) * 4
```

Without an IR, the bridge might directly manipulate strings or generate RPC calls from parser tokens.

That quickly becomes hard to maintain.

With an IR:

```text
Multiply(
    Add(
        Scalar(2),
        Scalar(3)
    ),
    Scalar(4)
)
```

the same semantic structure can later be:

- evaluated locally;
- serialized over gRPC;
- visualized;
- optimized;
- cached;
- compiled into a graph;
- logged for debugging;
- translated to another backend.

The IR therefore becomes the central contract of the project.

---

# 28. Future Optimization Direction

A mature pipeline could look like:

```text
LaTeX
  ↓
Lexer
  ↓
Parser
  ↓
AST
  ↓
Type / shape checking
  ↓
Typed IR
  ↓
Optimization passes
  ↓
Execution graph
  ↓
Serialization
  ↓
gRPC
  ↓
Remote runtime
  ↓
NumPy
```

Potential optimization passes include:

### Constant folding

```text
2 + 3
```

becomes:

```text
5
```

before transmission.

### Common-subexpression elimination

```text
(2+3)^2 + (2+3)^3
```

becomes:

```text
t0 = 2 + 3
t1 = t0^2
t2 = t0^3
t3 = t1 + t2
```

### Operation fusion

Combine compatible operations to reduce intermediate allocations.

### Batching

Send multiple independent expressions in one request.

### Caching

Reuse previously evaluated expressions or intermediate nodes where appropriate.

---

# 29. Design Questions to Decide Early

These are worth writing down as architectural decisions.

## Language

- Which LaTeX subset is supported?
- Is whitespace significant?
- What is the operator precedence?
- How are unary minus and negative numbers represented?
- What syntax represents vectors and matrices?

## Numerical semantics

- Which dtypes are supported?
- What is the default dtype?
- What happens on division by zero?
- Are NaN and infinity allowed?
- How are complex numbers represented?

## Shape semantics

- Is broadcasting supported?
- Which shape combinations are legal?
- Are scalar/tensor operations allowed?
- When are shape errors detected: compile time or runtime?

## Protocol

- Does one RPC represent one operation or one complete graph?
- How are tensors serialized?
- How are large arrays transferred?
- How are errors represented?
- How is protocol compatibility maintained?

## Execution

- Should the server be stateless?
- Should intermediate values be cached?
- Can independent graph nodes execute in parallel?
- How should resource limits be enforced?

These decisions do not all need final answers at M0, but they should be made intentionally.

---

# 30. First Vertical Slice

The first implementation should be intentionally tiny.

The complete path should be:

```text
Input:
    nmath "2 + 3"

        ↓

Lexer:
    2
    +
    3

        ↓

Parser:
    Add(2, 3)

        ↓

IR:
    BinaryOp(
        ADD,
        Scalar(2),
        Scalar(3)
    )

        ↓

Bridge:
    BinaryRequest(
        ADD,
        2,
        3
    )

        ↓

gRPC

        ↓

NumPy server:
    2 + 3

        ↓

Result:
    5
```

The first end-to-end acceptance test is therefore:

```text
nmath "2 + 3"
```

must return:

```text
5
```

Once that slice works, expand the system one capability at a time.

---

# 31. Recommended First Commit Sequence

A practical implementation history could look like this:

```text
1. project skeleton + pytest
2. protobuf definition
3. Ping RPC
4. CLI + ping command
5. scalar IR
6. parser for numbers
7. parser for +
8. scalar ADD runtime
9. ADD gRPC integration
10. end-to-end `2 + 3`
11. add -, *, /
12. operator precedence
13. parentheses
14. \frac{}
15. power and unary functions
16. type model
17. complex numbers
18. tensor model
19. vector parser
20. vector runtime
21. shape checking
22. complete expression graphs
23. graph serialization
24. execution optimizations
```

Each commit should ideally leave the system in a working state.

---

# 32. Final Project Concept

The project can ultimately be understood as:

> **A small distributed mathematical execution engine with a LaTeX frontend, a typed intermediate representation, a gRPC protocol, and a NumPy backend.**

The progression is:

```text
LaTeX scalar expression
        ↓
typed mathematical expression
        ↓
remote numerical execution
        ↓
tensor computation graph
        ↓
optimized distributed execution
```

The first milestone is intentionally small:

```text
nmath "2 + 3"
        ↓
      gRPC
        ↓
     NumPy
        ↓
        5
```

Everything after that should extend the same architectural contracts rather than replace them.

---

# 33. Definition of Done for the Initial Prototype

The first prototype is complete when all of the following are true:

- `nmath "2 + 3"` works end-to-end.
- The parser produces a structured AST/IR.
- The bridge converts IR to protobuf/gRPC messages.
- The server executes the operation through the NumPy runtime.
- Parser, IR, bridge, runtime, and integration tests exist.
- Invalid expressions generate deterministic errors.
- The CLI can report server connection failures cleanly.
- LaTeX parsing remains isolated from the server.
- The architecture leaves room for recursive expressions and tensors.
- The project can be expanded without changing the fundamental CLI → IR → gRPC → NumPy flow.

---

# 34. Guiding Principle

Keep the first implementation small enough to understand completely.

The goal is not to build a full symbolic math system immediately.

The goal is to prove this architecture:

```text
LaTeX
   ↓
Math IR
   ↓
gRPC
   ↓
NumPy
```

Once that vertical slice is stable and well-tested, the language, type system, execution graph, and performance features can grow around it.
