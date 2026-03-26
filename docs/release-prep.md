# Release Preparation

## Current public baseline

- Repository: `songblaq/constella-platform`
- Default branch: `main`
- Public collaboration:
  - issues
  - pull requests
  - public CONTRIBUTING flow

## Release prep checklist

### Code
- clean git status
- local tests green
- public docs present
- contribution templates present

### Distribution
- `constella install`
- `constella doctor`
- `constella verify bootstrap`
- `constella backup run`
- `constella restore run`

### Artifacts
- install bundle manifest
- profile set
- packaging note
- bootstrap verification runbook

## First release shape

The first release shape is documentation + install/bundle metadata, not a binary release.

Recommended public sequence:

1. stabilize `constella-platform`
2. verify bootstrap on a second machine
3. package release artifacts
4. publish tagged release notes
