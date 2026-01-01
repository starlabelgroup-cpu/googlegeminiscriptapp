<!-- Auto-generated guidance for AI coding agents working on this repository -->
# Copilot / AI Agent Instructions

Purpose: help an AI agent become immediately productive in this repository.

Repository snapshot
- Minimal repo: see [README.md](README.md#L1) — currently contains only a short description.
- Default branch: `main` (owner: starlabelgroup-cpu).

What to do first (fast discovery)
- Run a file manifest check for common language indicators: look for `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `Dockerfile`, and `.github/workflows/*`.
- If none exist, report back to the human owner asking for the project language, entrypoint, and intended runtime.

How to explore (recommended quick steps)
- Read [README.md](README.md#L1) and list project files in repository root.
- Search for configuration and CI: `.github/workflows/`, `Dockerfile`, `.devcontainer/`, and any `*.yml` files.
- Check for ignored or hidden files that may hold infra: `.gitignore`, `.dockerignore`.

Agent workflows (when repository is sparse)
- If there are no build/test manifests: ask the user what language/framework to scaffold. Offer to create a minimal scaffold (README expansion, `Dockerfile`, a basic `Makefile`, and a test harness).
- If manifests exist: infer build/test commands from them and list explicit run commands in your PR summary.

Project-specific conventions and hints
- This repo currently lacks conventional project files. Prefer asking clarifying questions before making large structural changes.
- Treat `main` as the canonical default branch; open PRs against `main` and use short, focused commits.

Integration and external dependencies
- No explicit integrations found in the current tree. If you add external services (APIs, cloud), document credentials and local emulation steps in `README.md`.

What to include in automated changes or PRs
- Small, self-contained PRs with one change per PR (scaffold, then features, then tests).
- Include a concise `README.md` update showing how to run the project locally and run tests.

When unsure — ask
- If you cannot find an entrypoint or language indicators within the repo, ask the repository owner for the intended runtime and any non-committed secrets or infra assumptions.

Notes for maintainers
- This file was generated from an automated scan of repository contents on creation. Update it when you add a language, CI, or key services so future agents can act without prompting.
