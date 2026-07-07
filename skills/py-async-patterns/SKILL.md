---
name: py-async-patterns
description: Review Python async code for event-loop blocking, missing await, incorrect task/gather usage, swallowed cancellation, missing timeouts, and sync/async boundary mistakes. Use when reviewing asyncio, FastAPI, aiohttp, httpx async clients, background tasks, or concurrent I/O.
---

# Python Async Review

Use these rules only for async or concurrent I/O code. Prefer concrete event-loop
or cancellation risks over general async style suggestions.

## Review Rules

### Rule: async-blocking-call
**Impact:** CRITICAL
**Applies when:** Code inside `async def` performs sleeping, HTTP, database, filesystem, subprocess, or CPU-heavy work.
**Skip when:** The operation is explicitly offloaded to a thread/process or is known non-blocking.
**Python:** any
**Tools:** ruff | project-configured
**Review signal:** `time.sleep`, `requests`, sync database clients, or CPU loops appear inside `async def`.

**Incorrect:**
```python
async def fetch_data(url: str) -> dict:
    time.sleep(1)
    return requests.get(url).json()
```

**Correct:**
```python
async def fetch_data(url: str) -> dict:
    await asyncio.sleep(1)
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    return response.json()
```

**Reason:** Blocking calls stop the event loop and degrade every concurrent request or task.

### Rule: async-missing-await
**Impact:** HIGH
**Applies when:** Changed code calls an async function.
**Skip when:** The coroutine is intentionally scheduled with `asyncio.create_task` and its lifecycle is handled.
**Python:** any
**Tools:** pyright | mypy | ruff | project-configured
**Review signal:** A coroutine-returning function is called without `await`, `create_task`, `gather`, or equivalent scheduling.

**Incorrect:**
```python
async def handler() -> dict:
    result = fetch_user()
    return {"user": result}
```

**Correct:**
```python
async def handler() -> dict:
    result = await fetch_user()
    return {"user": result}
```

**Reason:** Calling an async function without awaiting or scheduling it returns a coroutine object and does not run the operation.

### Rule: async-gather-failure-semantics
**Impact:** MEDIUM-HIGH
**Applies when:** Code runs independent async operations concurrently.
**Skip when:** Failing fast on the first exception is required and documented.
**Python:** any
**Tools:** none
**Review signal:** `asyncio.gather` is used for independent batch work without deliberate exception handling.

**Incorrect:**
```python
async def fetch_all(ids: list[str]) -> list[User]:
    return await asyncio.gather(*(fetch_user(user_id) for user_id in ids))
```

**Correct:**
```python
async def fetch_all(ids: list[str]) -> list[User | Exception]:
    return await asyncio.gather(
        *(fetch_user(user_id) for user_id in ids),
        return_exceptions=True,
    )
```

**Reason:** Concurrent batch code needs explicit failure semantics: fail fast, collect partial failures, or cancel siblings deliberately.

### Rule: async-cancellation-propagates
**Impact:** CRITICAL
**Applies when:** Code catches broad exceptions inside async tasks or request handlers.
**Skip when:** The code catches `asyncio.CancelledError` only to clean up and then re-raises.
**Python:** any
**Tools:** none
**Review signal:** Broad `except Exception`/`except BaseException` around awaited work may swallow cancellation or hide task shutdown.

**Incorrect:**
```python
async def worker() -> None:
    try:
        await run_forever()
    except BaseException:
        logger.exception("worker failed")
```

**Correct:**
```python
async def worker() -> None:
    try:
        await run_forever()
    except asyncio.CancelledError:
        await cleanup()
        raise
    except Exception:
        logger.exception("worker failed")
        raise
```

**Reason:** Cancellation is control flow for async shutdown. Swallowing it can hang deployments and leak resources.
**References:** https://docs.python.org/3/library/asyncio-task.html
**Checked:** 2026-07-07
**Expires:** 2026-10-01

### Rule: async-timeout-boundary
**Impact:** HIGH
**Applies when:** Code awaits network, database, queue, subprocess, or external service calls.
**Skip when:** The called client has a documented timeout configured at construction or service level.
**Python:** any
**Tools:** none
**Review signal:** Awaited external calls have no timeout or cancellation boundary.

**Incorrect:**
```python
async def load_profile(user_id: str) -> Profile:
    return await profile_client.fetch(user_id)
```

**Correct:**
```python
async def load_profile(user_id: str) -> Profile:
    return await asyncio.wait_for(profile_client.fetch(user_id), timeout=2.0)
```

**Reason:** Unbounded awaits can pin request handlers and background workers indefinitely.
