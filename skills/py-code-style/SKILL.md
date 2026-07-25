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

### Rule: style-string-regex-hygiene
**Impact:** MEDIUM
**Applies when:** Code contains regex patterns, string interpolation, or string construction that could be simplified.
**Skip when:** The regex is inherently complex (e.g., parsing nested structures) and the escaping is unavoidable.
**Python:** any
**Tools:** ruff | project-configured
**Review signal:** Manual escape sequences in character classes, verbose string building, or regex patterns that could use Python convenience features.

**Incorrect:**
```python
# Unnecessary backslash before double-quote in raw string character class
re.search(r'python-version:\s*[\\"\\']{ver}[\\"\\']', text)

# Verbose string construction
expected = "[" + ", ".join(f'"{v}"' for v in VERSIONS) + "]"

# Hardcoded string used in multiple places
if filepath == ".agents/skills/skill-discovery":  # also defined in another file
```

**Correct:**
```python
# Switch quote delimiter to avoid escaping inside character class
re.search(rf"python-version:\s*[\"']{ver}[\"']", text)

# Use a magic string constant — readable at a glance
EXPECTED_YAML = '["3.10", "3.14"]'

# Extract to a named constant — single source of truth
SYMLINK_ENTRY = ".agents/skills/skill-discovery"
if filepath == SYMLINK_ENTRY:
```

**Reason:** Python provides quote-delimiter switching, f-strings, `re.escape()`, and named constants to avoid manual escaping. Complex escape sequences are error-prone for both humans and AI agents, and often indicate a simpler approach exists.

### Rule: style-regex-escape-strategy
**Impact:** MEDIUM
**Applies when:** Code builds regex patterns by concatenating user input, configuration values, or dynamic strings.
**Skip when:** The pattern is a static literal with no interpolated values.
**Python:** any
**Tools:** ruff | project-configured
**Review signal:** Manual escaping of regex metacharacters in interpolated values, or missing `re.escape()` on user-controlled input.

**Incorrect:**
```python
# Manual escaping — error-prone, misses edge cases
domain = "example.com"
pattern = r"https?://" + domain.replace(".", "\\.") + r"/.*"

# User input not escaped — ReDoS or wrong match
def find_users(query: str) -> list[str]:
    return re.findall(rf"User: {query}", log_text)
```

**Correct:**
```python
# re.escape() handles all metacharacters correctly
domain = "example.com"
pattern = rf"https?://{re.escape(domain)}/.*"

# Escape user input before embedding in regex
def find_users(query: str) -> list[str]:
    return re.findall(rf"User: {re.escape(query)}", log_text)
```

**Reason:** `re.escape()` is the canonical way to sanitize strings for regex interpolation. Manual escaping misses characters (e.g., `{`, `}`, `(`) and creates maintenance burden when regex syntax evolves.

### Rule: style-quote-delimiter-strategy
**Impact:** LOW
**Applies when:** Raw strings contain quotes that require escaping inside the string delimiter.
**Skip when:** The regex or string is simple enough that escaping is minimal and clear.
**Python:** any
**Tools:** ruff | project-configured
**Review signal:** Unnecessary backslash-escaping of quotes inside raw strings, or mixed delimiter styles within the same module.

**Incorrect:**
```python
# Double-quoted raw string — " needs escaping, ' doesn't
re.search(r"version:\s*[\"']?[\"']", text)  # confusing

# Single-quoted raw string — ' needs escaping, " doesn't  
re.search(r'version:\s*[\"\\']?[\"\\']', text)  # worse
```

**Correct:**
```python
# Choose delimiter so the character class needs no escaping
re.search(r"version:\s*[\"']?[\"']", text)   # " is in class, use " delimiter → ' doesn't escape
re.search(r'version:\s*[\"\'']?[\"\'']', text)  # ' is in class, use ' delimiter → " doesn't escape

# Or use a character class with the delimiter's quote first
re.search(r"[\"']+", text)   # Either quote — no escaping needed
```

**Reason:** Consistent delimiter choice eliminates escape noise. If the character class contains `"`, use `'` as the string delimiter (or vice versa). Pick one convention per project and follow it.

### Rule: style-constant-placement
**Impact:** LOW-MEDIUM
**Applies when:** Named values are defined as module-level constants or hardcoded in multiple locations.
**Skip when:** The value is truly local to a single function and used nowhere else.
**Python:** any
**Tools:** ruff | project-configured
**Review signal:** Magic strings/numbers repeated across files, or module-level constants that are only used in one function.

**Incorrect:**
```python
# Hardcoded in multiple places — no single source of truth
if status == "completed":  # also in validator.py and test_validators.py
    ...

# Module-level constant used only in one function
MAX_RETRIES = 3  # defined at top, used only in fetch_with_retry()

def fetch_with_retry(url: str) -> Response:
    for _ in range(MAX_RETRIES):  # could be local
        ...
```

**Correct:**
```python
# Extracted to a shared constant — single source of truth
# In constants.py or at module top
COMPLETED_STATUS = "completed"

if status == COMPLETED_STATUS:
    ...

# Function-local when only used there
def fetch_with_retry(url: str) -> Response:
    max_retries = 3  # local — doesn't need module scope
    for _ in range(max_retries):
        ...
```

**Reason:** Constants belong at the narrowest scope that covers all their uses. Module-level is for values shared across functions or files; function-local is for values used in one place. Repeated magic strings should be extracted to a single definition.

## Sensitive Evidence Safety

If changed code or tool output reveals a suspected credential, token, private
key, secret-bearing URL, or other sensitive value, do not quote or reproduce the
value. Report only its existence and location. Treat filename and pattern checks
as heuristic evidence, not proof that a repository is secret-free.

If the exposure appears credible, make it the first finding, stop lower-priority
review, and recommend revocation or rotation. Never place sensitive values in
reports, generated examples, or commit subjects or bodies.
