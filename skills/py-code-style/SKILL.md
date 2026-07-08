---
name: py-code-style
description: Review Python code style with emphasis on configured tooling, import organization, naming clarity, public API documentation, and formatting consistency. Use when reviewing style/lint changes, pyproject lint configuration, docstrings, imports, naming, or readability issues after correctness findings.
---

# Python Code-Style Review

Use style findings after correctness findings. Defer to the project's configured
formatter and linter when they exist.

**Freshness:** stable (no external references) — review rules based on core Python conventions, not volatile APIs.

## Review Rules

### Rule: style-defer-to-tooling
**Impact:** LOW-MEDIUM
**Applies when:** The project has `ruff`, `black`, `isort`, `mypy`, or `pyright` configuration.
**Skip when:** No tooling exists and the issue is purely subjective.
**Python:** any
**Tools:** ruff | mypy | pyright | project-configured
**Review signal:** Review feedback contradicts or duplicates configured automated tooling.

**Incorrect:**
```python
# Reviewer asks for single quotes while pyproject config uses double quotes.
name = 'Ada'
```

**Correct:**
```python
# Follow configured formatter output.
name = "Ada"
```

**Reason:** Style review should reinforce automated tools, not create a parallel subjective standard.

### Rule: style-import-organization
**Impact:** LOW-MEDIUM
**Applies when:** Imports are added or moved.
**Skip when:** The project formatter/linter will auto-fix the issue and CI already enforces it.
**Python:** any
**Tools:** ruff | project-configured
**Review signal:** Standard library, third-party, and local imports are mixed, or relative imports are added without need.

**Incorrect:**
```python
from myapp.models import User
import os
import httpx
```

**Correct:**
```python
import os

import httpx

from myapp.models import User
```

**Reason:** Predictable import grouping reduces merge churn and makes dependencies easier to scan.

### Rule: style-naming-clarity
**Impact:** LOW-MEDIUM
**Applies when:** New public names, modules, classes, functions, or constants are introduced.
**Skip when:** The name follows a domain convention or matches an external API.
**Python:** any
**Tools:** ruff | project-configured
**Review signal:** Abbreviated or misleading names obscure the domain concept.

**Incorrect:**
```python
def proc_usr(u: User) -> Result:
    ...
```

**Correct:**
```python
def process_user(user: User) -> Result:
    ...
```

**Reason:** Clear names reduce the need for comments and make reviewable intent visible.

### Rule: style-public-docstring
**Impact:** LOW-MEDIUM
**Applies when:** A public class, function, or method has non-obvious behavior, side effects, or failure modes.
**Skip when:** The public API is self-evident and fully described by its name and type signature.
**Python:** any
**Tools:** ruff | project-configured
**Review signal:** Public APIs with important arguments, return values, raised exceptions, or examples lack docstrings.

**Incorrect:**
```python
def process_batch(items: list[Item], max_workers: int = 4) -> BatchResult:
    ...
```

**Correct:**
```python
def process_batch(items: list[Item], max_workers: int = 4) -> BatchResult:
    """Process items concurrently and return successes plus per-item failures."""
    ...
```

**Reason:** Docstrings are most valuable where types alone do not communicate side effects or failure semantics.

### Rule: style-line-length-readability
**Impact:** LOW
**Applies when:** A changed line is hard to review because it combines multiple calls, conditions, or string fragments.
**Skip when:** The configured formatter keeps the line and readability is acceptable.
**Python:** any
**Tools:** ruff | project-configured
**Review signal:** Long expressions are technically valid but obscure intermediate meaning.

**Incorrect:**
```python
return client.fetch(user.id, include_orders=True, include_invoices=True, timeout=timeout, retry_policy=retry_policy)
```

**Correct:**
```python
return client.fetch(
    user.id,
    include_orders=True,
    include_invoices=True,
    timeout=timeout,
    retry_policy=retry_policy,
)
```

**Reason:** Review style should improve scanability where automated formatting alone is not enough.
