---
name: py-error-handling
description: Review Python code for error-handling issues including missing boundary validation, generic exceptions, swallowed failures, missing exception chaining, partial batch failure handling, and cleanup behavior. Use when reviewing validation logic, exception paths, retries, file/network operations, or batch processing.
---

# Python Error-Handling Review

Use these rules when changed code creates, catches, transforms, logs, retries, or
suppresses failures.

**Freshness:** stable (no external references) — review rules based on core Python conventions, not volatile APIs.

## Review Rules

### Rule: error-validate-boundary
**Impact:** HIGH
**Applies when:** External input enters the system through API handlers, CLI args, config, files, queues, or network payloads.
**Skip when:** The caller already validated the exact invariant and the contract is local and obvious.
**Python:** any
**Tools:** none
**Review signal:** Code trusts raw strings, dicts, or numeric ranges until deep inside business logic.

**Incorrect:**
```python
def fetch_page(url: str, page_size: int) -> Page:
    return client.get(url, params={"page_size": page_size})
```

**Correct:**
```python
def fetch_page(url: str, page_size: int) -> Page:
    if not url:
        raise ValueError("'url' is required")
    if not 1 <= page_size <= 100:
        raise ValueError(f"'page_size' must be 1-100, got {page_size}")
    return client.get(url, params={"page_size": page_size})
```

**Reason:** Boundary validation fails early with useful context instead of allowing vague downstream failures.

### Rule: error-specific-exceptions
**Impact:** HIGH
**Applies when:** Code raises or catches exceptions.
**Skip when:** A truly unknown exception is caught only to add context and then re-raised.
**Python:** any
**Tools:** ruff | project-configured
**Review signal:** `raise Exception(...)`, bare `except:`, or `except Exception: pass` appears in changed code.

**Incorrect:**
```python
try:
    process()
except Exception:
    pass
```

**Correct:**
```python
try:
    process()
except ConnectionError as exc:
    logger.warning("Connection failed; retrying", exc_info=exc)
    raise
```

**Reason:** Generic or swallowed exceptions hide bugs and make production failures hard to diagnose.

### Rule: error-chain-context
**Impact:** MEDIUM-HIGH
**Applies when:** Code catches an exception and raises a domain-specific exception.
**Skip when:** The original exception intentionally must be hidden from users and is still logged with trace context.
**Python:** any
**Tools:** ruff | project-configured
**Review signal:** `except SomeError as e:` followed by `raise OtherError(...)` without `from e`.

**Incorrect:**
```python
try:
    return Config.from_file(path)
except OSError as exc:
    raise ConfigError(f"Could not load {path}")
```

**Correct:**
```python
try:
    return Config.from_file(path)
except OSError as exc:
    raise ConfigError(f"Could not load {path}") from exc
```

**Reason:** Chaining preserves the original traceback while still exposing a domain-level error.

### Rule: error-batch-partial-failures
**Impact:** MEDIUM-HIGH
**Applies when:** A loop processes independent items from a batch, queue, import, or migration.
**Skip when:** The operation must be atomic and rollback is explicit.
**Python:** any
**Tools:** none
**Review signal:** One item failure aborts a batch where other items could safely continue.

**Incorrect:**
```python
def process_batch(items: list[Item]) -> list[Result]:
    return [process(item) for item in items]
```

**Correct:**
```python
def process_batch(items: list[Item]) -> BatchResult:
    succeeded: dict[int, Result] = {}
    failed: dict[int, Exception] = {}
    for index, item in enumerate(items):
        try:
            succeeded[index] = process(item)
        except ProcessingError as exc:
            failed[index] = exc
    return BatchResult(succeeded=succeeded, failed=failed)
```

**Reason:** Independent batch work should report successes and failures separately unless atomicity is required.

### Rule: error-cleanup-context-manager
**Impact:** HIGH
**Applies when:** Code opens files, sockets, locks, database sessions, temporary directories, or other closeable resources.
**Skip when:** Ownership is intentionally transferred and documented.
**Python:** any
**Tools:** ruff | project-configured
**Review signal:** `open()`, locks, sessions, or clients are acquired without `with`, `async with`, `try/finally`, or an explicit close path.

**Incorrect:**
```python
def read_config(path: str) -> str:
    handle = open(path)
    return handle.read()
```

**Correct:**
```python
def read_config(path: str) -> str:
    with open(path) as handle:
        return handle.read()
```

**Reason:** Cleanup must run when reads, writes, or downstream processing raise.

## Sensitive Evidence Safety

If changed code or tool output reveals a suspected credential, token, private
key, secret-bearing URL, or other sensitive value, do not quote or reproduce the
value. Report only its existence and location. Treat filename and pattern checks
as heuristic evidence, not proof that a repository is secret-free.

If the exposure appears credible, make it the first finding, stop lower-priority
review, and recommend revocation or rotation. Never place sensitive values in
reports, generated examples, or commit subjects or bodies.
