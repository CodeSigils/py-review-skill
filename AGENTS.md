# py-review-skill

This repo ships a Python code-review router and five focused review skills.
All skills use only agentskills.io base frontmatter (`name` + `description`)
and reference only generic CLI tools — no agent-specific commands or paths.

## How to use

1. Load `py-review` first when asked to review Python code.
2. It inspects the project's Python version, maturity, and toolchain, then
   dispatches to the relevant focused sub-skills based on what changed.
3. Focused skills: `py-type-safety`, `py-error-handling`, `py-anti-patterns`,
   `py-async-patterns`, `py-code-style`.

Each skill is self-contained. No external setup needed beyond making the
`skills/` directory discoverable by your agent runtime.
