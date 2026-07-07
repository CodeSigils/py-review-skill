---
name: py-anti-patterns
description: Review Python code for common correctness and maintainability anti-patterns including hard-coded configuration, mixed I/O and business logic, leaked internal models, scattered retries, mutable defaults, and resource misuse. Use as a focused checklist during Python review.
---

# Python Anti-Pattern Review

Use these rules as a correctness-first checklist. Do not flag broad architecture
preferences unless the changed code creates a concrete maintenance or behavior risk.

## Review Rules

### Rule: anti-hard-coded-config
**Impact:** HIGH
**Applies when:** Code adds endpoints, credentials, filesystem paths, timeouts, feature flags, or environment-specific values.
**Skip when:** The value is a harmless local constant or test fixture.
**Python:** any
**Tools:** none
**Review signal:** Production configuration or secrets are hard-coded in module globals or functions.

**Incorrect:**
```python
API_KEY = "sk-live-example"
DB_HOST = "prod-db.example.com"
```

**Correct:**
```python
class Settings(BaseSettings):
    api_key: str = Field(alias="API_KEY")
    db_host: str = Field(alias="DB_HOST")
```

**Reason:** Hard-coded environment values make deployments brittle and can leak secrets.

### Rule: anti-mixed-io-business-logic
**Impact:** MEDIUM-HIGH
**Applies when:** Business decisions are added near SQL, HTTP calls, filesystem reads, or ORM queries.
**Skip when:** The function is a thin adapter whose only job is I/O orchestration.
**Python:** any
**Tools:** none
**Review signal:** A function both fetches raw data and implements domain decisions that should be testable independently.

**Incorrect:**
```python
def calculate_discount(user_id: str) -> float:
    orders = db.query("SELECT * FROM orders WHERE user_id = ?", user_id)
    return 0.15 if len(orders) > 10 else 0.0
```

**Correct:**
```python
def calculate_discount(orders: Sequence[Order]) -> float:
    return 0.15 if len(orders) > 10 else 0.0
```

**Reason:** Separating I/O from business logic makes behavior easier to test and reduces hidden coupling.

### Rule: anti-expose-internal-model
**Impact:** MEDIUM-HIGH
**Applies when:** API, serialization, or package boundaries return ORM models, protobuf internals, or persistence objects.
**Skip when:** The boundary is internal and consumers are explicitly coupled to that model.
**Python:** any
**Tools:** none
**Review signal:** Handler or public method returns a database model directly.

**Incorrect:**
```python
@app.get("/users/{user_id}")
def get_user(user_id: str) -> UserModel:
    return session.get(UserModel, user_id)
```

**Correct:**
```python
@app.get("/users/{user_id}")
def get_user(user_id: str) -> UserResponse:
    user = session.get(UserModel, user_id)
    return UserResponse.model_validate(user)
```

**Reason:** Exposing internal models couples clients to storage details and can leak fields unintentionally.

### Rule: anti-scattered-retry-timeout
**Impact:** MEDIUM-HIGH
**Applies when:** Network/database calls add custom retries, timeouts, or backoff behavior.
**Skip when:** The code is the single shared client wrapper for that service.
**Python:** any
**Tools:** none
**Review signal:** Similar timeout/retry logic appears in multiple call sites, or retries exist at multiple layers.

**Incorrect:**
```python
def fetch_user(user_id: str) -> Response:
    for _ in range(3):
        try:
            return requests.get(url, timeout=30)
        except Timeout:
            continue
```

**Correct:**
```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def http_get(url: str) -> Response:
    return requests.get(url, timeout=30)
```

**Reason:** Scattered retry behavior creates inconsistent failure semantics and can accidentally multiply retries.

### Rule: anti-mutable-default
**Impact:** HIGH
**Applies when:** A function or method default value is a mutable object.
**Skip when:** The object is intentionally immutable despite its type, which should be rare and documented.
**Python:** any
**Tools:** ruff | project-configured
**Review signal:** Defaults such as `[]`, `{}`, `set()`, or model instances appear in function signatures.

**Incorrect:**
```python
def add_tag(tag: str, tags: list[str] = []) -> list[str]:
    tags.append(tag)
    return tags
```

**Correct:**
```python
def add_tag(tag: str, tags: list[str] | None = None) -> list[str]:
    result = [] if tags is None else list(tags)
    result.append(tag)
    return result
```

**Reason:** Mutable defaults are shared across calls and can leak state between independent invocations.
