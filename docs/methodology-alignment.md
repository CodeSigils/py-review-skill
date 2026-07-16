# Methodology Alignment

`py-review-skill` follows the `skill-discovery` and `skill-creator` findings:

- Keep runtime skills portable: only `name` and `description` YAML frontmatter.
- Keep review rules inline in each focused `SKILL.md`; do not create per-rule files.
- Use scripts for deterministic validation and generated test cases.
- Track source provenance and freshness in docs and markdown body markers.
- Avoid platform adapter directories in v1.
- Keep the sensitive-evidence safety contract inline in every standalone skill;
  focused skills may load without the router.
- Treat repository policy and runtime behavior as separate layers:
  `SECURITY.md` owns disclosure and trust scope, while each `SKILL.md` owns
  secret-safe review behavior.

The repo is intentionally richer than the runtime skill surface. Agents load
only the relevant `SKILL.md` files; maintainers use `docs/`, `scripts/`, CI,
fixtures, and generated test cases to keep the skill set stable. Deterministic
validation checks structure, security guards, portability, routing, freshness,
and common live-credential patterns; it does not prove reviewed repositories
are vulnerability-free.
