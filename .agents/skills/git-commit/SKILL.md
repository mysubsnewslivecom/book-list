---
name: git-commit
description: 'Execute git commit with conventional commit message analysis, intelligent staging, and message generation. Use when user asks to commit changes, create a git commit, or mentions "/commit". Supports: (1) Auto-detecting type and scope from changes, (2) Generating conventional commit messages from diff, (3) Interactive commit with optional type/scope/description overrides, (4) Intelligent file staging for logical grouping'
license: MIT
---

# Git Commit with Conventional Commits

## Overview

Create standardized, semantic git commits using the Conventional Commits specification. Analyze the actual diff to determine appropriate type, scope, and message.

## Decision Logic for the Agent

When a user requests a commit, follow this reasoning path:

1. **State Detection**: Run `git status` to see if changes are staged or unstaged.
2. **Granularity Check**: Are the changes in one logical group?
   - If `git diff --staged` contains multiple unrelated changes (e.g., a `feat` and a `fix`), **stop** and suggest staging them separately.
3. **Context Extraction**:
   - **Type**: Identify from the nature of the code change (see Commit Types).
   - **Scope**: Identify the specific module, directory, or component being modified.
   - **Message**: Summarize the _intent_ of the change, not just the action.
4. **Safety Check**: Scan the diff for sensitive patterns (API keys, `.env`, `password`) before proposing the commit.

## Conventional Commit Format

```
<type>[optional scope]: <description>
[optional body]
[optional footer(s)]
```

## Commit Types

| Type       | Purpose                        |
| ---------- | ------------------------------ |
| `feat`     | New feature                    |
| `fix`      | Bug fix                        |
| `docs`     | Documentation only             |
| `style`    | Formatting/style (no logic)    |
| `refactor` | Code refactor (no feature/fix) |
| `perf`     | Performance improvement        |
| `test`     | Add/update tests               |
| `build`    | Build system/dependencies      |
| `ci`       | CI/config changes              |
| `chore`    | Maintenance/misc               |
| `revert`   | Revert commit                  |

## Breaking Changes

```
# Exclamation mark after type/scope
feat!: remove deprecated endpoint

# BREAKING CHANGE footer
feat: allow config to even extend other configs
BREAKING CHANGE: `extends` key behavior changed
```

## Changelog Trailers

Add `Changelog: <category>` footer to categorize commits for changelog generation:

```
<Commit message subject>
<Commit message description>
Changelog: <category>
```

**Changelog Categories:**
| Category | Purpose |
| ------------- | -------------------------------- |
| `added` | New feature |
| `fixed` | Bug fix |
| `changed` | Feature change |
| `deprecated` | New deprecation |
| `removed` | Feature removal |
| `security` | Security fix |
| `performance` | Performance improvement |
| `other` | Other changes |

## Agent Execution Flow

### Step 1: Analyze Diff

Determine the scope and type by inspecting the changes.

```bash
# Check status
git status --porcelain
# Inspect staged changes
git diff --staged
# Inspect unstaged changes (if nothing is staged)
git diff
```

### Step 2: Stage Files (Intelligent Grouping)

If the diff shows unrelated changes, group them into logical commits.

```bash
# Stage specific files for a specific feature
git add path/to/feature_file.py
# Stage all files in a specific module
git add src/components/header/
```

**CRITICAL:** **Never commit secrets** (`.env`, credentials, private keys). If detected, abort and notify user.

### Step 3: Generate Commit Message

Construct the message using the following rules:

- **Imperative mood**: "add feature" instead of "added feature".
- **Present tense**: "fix bug" instead of "fixes bug".
- **Scope**: Use the directory or component name (e.g., `feat(auth): ...`).
- **Length**: Keep the subject line under 72 characters.

### Step 4: Execute Commit

```bash
# Standard commit
git commit -m "<type>[scope]: <description>" -m "Changelog: <category>"

# Multi-line commit (for complex changes)
git commit -m "$(cat <<'EOF'
<type>[scope]: <description>

<optional body explaining the 'why'>

Changelog: <category>
EOF
)"
```

## Best Practices

- **Atomic Commits**: One logical change per commit.
- **Reference Issues**: Use `Closes #123` or `Refs #456` in the body/footer.
- **No Refactor/Fix overlap**: If a refactor introduces a bug fix, split it into two commits.

## Git Safety Protocol

- **NEVER** update git config.
- **NEVER** run destructive commands (`--force`, `reset --hard`) without explicit, verified user request.
- **NEVER** skip hooks (`--no-verify`) unless specifically asked.
- **NEVER** force push to `main` or `master`.
- **Error Handling**: If a commit fails due to a pre-commit hook (e.g., linting error), do **not** use `--no-verify`. Instead, fix the error and create a new commit.
