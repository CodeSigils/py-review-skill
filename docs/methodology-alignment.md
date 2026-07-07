# Methodology Alignment

`py-review-skill` follows the `skill-discovery` and `skill-creator` findings:

- Keep runtime skills portable: only `name` and `description` YAML frontmatter.
- Keep review rules inline in each focused `SKILL.md`; do not create per-rule files.
- Use scripts for deterministic validation and generated test cases.
- Track source provenance and freshness in docs and markdown body markers.
- Avoid platform adapter directories in v1.

The repo is intentionally richer than the runtime skill surface. Agents load
only the relevant `SKILL.md` files; maintainers use `docs/`, `scripts/`, CI,
and `test-cases.json` to keep the skill set stable.
