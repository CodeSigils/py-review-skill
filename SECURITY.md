# Security Policy

## Reporting a Vulnerability

Report security issues privately through the
[GitHub Security Advisory](https://github.com/CodeSigils/py-review-skill/security/advisories/new)
rather than opening a public issue. Do not include exploit details, credentials,
or other sensitive values in public reports.

Use private reporting for any credible security vulnerability, including:

- review rules that could expose secrets, encourage insecure code, or cause
  destructive changes;
- compromised or misleading shipped skill payloads;
- credentials or unsafe sensitive examples in fixtures or compatibility
  evidence; and
- supply-chain or privilege risks in repository scripts, dependencies, or CI
  workflows.

Ordinary documentation defects, feature requests, and behavior bugs without a
credible security impact may be opened as public GitHub issues. When uncertain,
report privately.

## Repository Security Scope

Repository security covers CI workflows, validation scripts, generated test
cases, review fixtures, compatibility evidence, and release metadata. These
components must preserve the declared payload boundary, keep synthetic examples
clearly non-live, and prevent unreviewed or secret-bearing material from entering
the six shipped skills.

CI validates skill structure, portability, routing and fixture contracts,
freshness markers, sensitive-evidence directives, and common live-token or
private-key patterns. Passing those checks is limited evidence, not a claim that
the repository or reviewed projects are vulnerability-free.

## Shipped Skill Trust Guarantees

The shipped payload is 6 standalone `SKILL.md` files with no runtime scripts,
no config files, and no dependencies. Review rules are inline and checked for
agent-specific references by CI. Eval fixtures and recorded compatibility
evidence use synthetic placeholders rather than credentials.

Each standalone skill requires secret-safe reporting because focused skills may
load without the router. Suspected sensitive values are reported by existence
and location only. Credible exposure is prioritized ahead of lower-value review,
and the reviewer recommends revocation or rotation without reproducing the
value.

## Skill Trust Checklist

- [x] All six skills redact sensitive values and report existence or location only.
- [x] Credible credential exposure stops lower-priority review and prompts rotation guidance.
- [x] Filename and pattern checks are described as heuristic, not proof of a clean repository.
- [x] Reports, generated examples, and commit subjects and bodies exclude sensitive values.
- [x] CI checks the payload and fixtures for common live-token and private-key patterns.
- [x] The shipped payload contains no destructive reset, forced-push, or secret-dumping commands.

Last reviewed: 2026-08-23.
