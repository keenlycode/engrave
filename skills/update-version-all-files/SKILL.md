---
name: update-version-all-files
description: Update project version consistently across all related files in this repository. Use when asked to bump or set a release version, synchronize pyproject.toml and CHANGELOG.md, add a dated changelog section, and verify there is no version mismatch.
---

# Update Version Workflow

Execute version updates with a strict, minimal edit set.

## Inputs

Collect these values before editing:

- Target version in `MAJOR.MINOR.PATCH` format.
- Release date in `YYYY-MM-DD` format.
- Release note bullets for the changelog section.

Use the current date when no release date is provided.

## Files to Edit

Primary files for this task:

- `pyproject.toml`
- `CHANGELOG.md`

Conditional documentation files:

- `docs-src/**/*.md` when a page contains an explicit old version string or
  version-pinned install command that must match the release.

Do not edit lockfiles or generated docs output for this workflow.

## Step 1: Validate Current State

1. Read `pyproject.toml` and identify `[project].version`.
2. Read `CHANGELOG.md` and detect whether the target version heading already exists.
3. Scan `docs-src/**/*.md` for explicit version strings tied to the project.
4. Stop and ask for clarification if multiple canonical version fields are discovered.

## Step 2: Update `pyproject.toml`

1. Update only `[project].version`.
2. Preserve all other metadata and formatting.
3. Verify exactly one project version value changed.

## Step 3: Update `CHANGELOG.md`

Maintain this heading pattern:

`## [X.Y.Z] - YYYY-MM-DD`

1. Add a new release section directly below the intro block if the target version is new.
2. Update the existing section date and bullet content if the target version already exists.
3. Keep newest release sections at the top.
4. Keep concise subsections such as `### Added`, `### Changed`, `### Fixed` only when relevant.

## Step 4: Update `docs-src` (When Needed)

1. Update only explicit project version mentions in docs pages.
2. Leave generic wording such as "installed version" unchanged when no number is pinned.
3. Keep prose and examples unchanged except for the version token itself.

## Step 5: Verify Consistency

1. Re-read both files.
2. Confirm `pyproject.toml` version equals the changelog release heading version.
3. Confirm any explicit docs version mentions match `pyproject.toml`.
4. Confirm changelog date matches the requested date or current date fallback.
5. Report final updated values and touched files.

## Guardrails

- Avoid broad search-and-replace across the repo.
- Restrict edits to explicit version lines and the intended changelog section.
- Do not rewrite unrelated changelog entries.
- If the repository format differs from this workflow, pause and ask for direction.
