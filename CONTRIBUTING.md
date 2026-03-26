# Contributing to Constella Platform

## Collaboration loop

Constella Platform uses three linked loops:

- AgentHive cards for structured execution
- Plaza / llm-collab for runtime evidence and handoff
- GitHub issues / PRs for public collaboration

## Public feedback path

1. Open an issue for a bug, gap, UX problem, or feature idea.
2. Reference the relevant capability, task, or operator scenario when possible.
3. If code changes are needed, open a PR and link the issue.
4. The issue/PR should be reflected back into AgentHive tasks or governance records.

For second-machine verification of `TASK-024`, start with [`docs/second-machine-quickstart.md`](docs/second-machine-quickstart.md).

## What to include

- expected behavior
- actual behavior
- capability or surface involved (`CLI`, `TUI`, `GUI`, `API`)
- environment or machine context if relevant
- logs/screenshots/artifacts when available

## Review expectations

- preview-first and auditability matter
- destructive behavior must be explicit
- parity gaps between surfaces should be called out directly
