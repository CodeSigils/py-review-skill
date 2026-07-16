---
name: py-type-safety
description: Review Python code for type-safety issues including Any leaks, missing public annotations, unsafe Optional handling, unparameterized collections, imprecise generics, and type-checker configuration drift. Use when reviewing typed Python code, public APIs, dataclasses, protocols, generics, casts, or mypy/pyright configuration.
---

# Python Type-Safety Review

Use these rules only after reading the changed code. Prefer findings that would
be caught by a type checker or prevent a realistic runtime bug.

## Review Rules

### Rule: type-public-signatures
**Impact:** MEDIUM-HIGH
**Applies when:** Public functions, methods, classes, or exported helpers are added or changed.
**Skip when:** The code is private test scaffolding or a throwaway script with no typed boundary.
**Python:** any
**Tools:** mypy | pyright | project-configured
**Review signal:** Public parameters or return values are unannotated, especially at package/API boundaries.

**Incorrect:**
```python
def find_user(user_id):
    return repository.get(user_id)
```

**Correct:**
```python
def find_user(user_id: str) -> User | None:
    return repository.get(user_id)
```

**Reason:** Public annotations make absence and data shape explicit. Without them, callers and type checkers lose the contract at the boundary.

### Rule: type-any-leak
**Impact:** HIGH
**Applies when:** `Any`, `dict[str, Any]`, raw JSON, or untyped third-party results cross into domain code.
**Skip when:** The value remains at a narrow dynamic boundary and is immediately validated or converted.
**Python:** any
**Tools:** mypy | pyright | project-configured
**Review signal:** `Any` appears in return types, domain objects, or widely reused helper signatures.

**Incorrect:**
```python
def load_user(payload: dict[str, Any]) -> Any:
    return payload["user"]
```

**Correct:**
```python
def load_user(payload: Mapping[str, object]) -> User:
    return User.model_validate(payload["user"])
```

**Reason:** `Any` disables checking wherever it flows. Convert dynamic data to domain types at boundaries so mistakes stay local.

### Rule: type-none-narrowing
**Impact:** HIGH
**Applies when:** A value typed as optional is dereferenced, passed onward, or returned as non-optional.
**Skip when:** The code has an explicit guard, assertion, exception, or early return proving the value is present.
**Python:** >=3.10
**Tools:** mypy | pyright | project-configured
**Review signal:** A `T | None` value is used without an `is None` check or equivalent narrowing.

**Incorrect:**
```python
user = find_user(user_id)
return user.email
```

**Correct:**
```python
user = find_user(user_id)
if user is None:
    raise UserNotFoundError(user_id)
return user.email
```

**Reason:** Optional return types encode a real missing-value path. Narrow before use so both runtime behavior and static analysis agree.

### Rule: type-collection-parameters
**Impact:** MEDIUM
**Applies when:** Functions return or accept collections.
**Skip when:** The collection is intentionally heterogeneous and documented as such.
**Python:** >=3.9
**Tools:** mypy | pyright | project-configured
**Review signal:** Bare `list`, `dict`, `set`, `tuple`, or overly broad `Iterable[Any]` appears in changed signatures.

**Incorrect:**
```python
def get_users() -> list:
    ...
```

**Correct:**
```python
def get_users() -> list[User]:
    ...
```

**Reason:** Unparameterized collections hide element types and push errors to consumers.

### Rule: type-preserve-generics
**Impact:** MEDIUM-HIGH
**Applies when:** A helper, container, decorator, or wrapper should preserve input/output types.
**Skip when:** The wrapper intentionally erases type information at a narrow dynamic boundary.
**Python:** any
**Tools:** mypy | pyright | project-configured
**Review signal:** A generic helper returns `object`, `Any`, or a base class when it can preserve `T`.

**Incorrect:**
```python
def first(items: list[object]) -> object:
    return items[0]
```

**Correct:**
```python
def first[T](items: Sequence[T]) -> T:
    return items[0]
```

**Reason:** Generic helpers should not throw away information callers already have. Preserving `T` keeps downstream code type-safe.
**References:** https://docs.python.org/3/library/typing.html
**Checked:** 2026-07-07
**Expires:** 2026-10-01

## Sensitive Evidence Safety

If changed code or tool output reveals a suspected credential, token, private
key, secret-bearing URL, or other sensitive value, do not quote or reproduce the
value. Report only its existence and location. Treat filename and pattern checks
as heuristic evidence, not proof that a repository is secret-free.

If the exposure appears credible, make it the first finding, stop lower-priority
review, and recommend revocation or rotation. Never place sensitive values in
reports, generated examples, or commit subjects or bodies.
