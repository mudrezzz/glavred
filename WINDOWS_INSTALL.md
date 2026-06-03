# Windows install notes

## Unzip into a project folder

Unzip the archive directly into your project root.

Expected result:

```text
AGENTS.md
ROADMAP.md
README.md
.agents/
docs/
demo/
```

## PowerShell check

From the project root:

```powershell
Get-ChildItem -Force
Get-ChildItem -Force .agents\skills
```

## Codex usage examples

```text
$project-bootstrap initialize this project
$architecture-design design the architecture from the requirements file
$project-onboarding take the next task from ROADMAP.md
$slice-implementation implement the next ready slice
$docs-sync update docs for the latest changes
$regression-and-test-strategy decide what tests to run
$demo-maintenance update the demo
```

## GitHub account

The template instructs Codex to create repositories under:

```text
mudrezzz
```

when GitHub CLI is installed and authenticated.
