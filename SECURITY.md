# Security Policy

Report security issues privately through the
[GitHub Security Advisory](https://github.com/CodeSigils/py-review-skill/security/advisories/new)
rather than opening a public issue.

Security concerns in this repository include review rules that could encourage
insecure code patterns, supply-chain risks in CI scripts and workflows, or
credentials in test fixtures and compatibility evidence. Do not include exploit
details in public reports.

Issues that do not involve the CI pipeline or credential material can be opened
as public GitHub issues. Report CI-related vulnerabilities through the advisory
link above.

The shipped payload is six standalone `SKILL.md` files with no runtime scripts,
no config files, and no dependencies. Review rules are inline and checked for
agent-specific references by CI. Eval fixtures and recorded compatibility
evidence contain no credentials.

Last reviewed: 2026-07-14.
