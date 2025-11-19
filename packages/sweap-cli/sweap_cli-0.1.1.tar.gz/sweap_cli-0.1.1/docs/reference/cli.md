# CLI Reference

The SWEAP CLI is implemented with [Typer](https://typer.tiangolo.com) and ships
the commands described below. All commands accept `--help` for additional
details. Paths default to the current working directory (`.`) unless otherwise
stated.

## `task init`

Scaffold a new task bundle.

- `--repo` (**required**) – source repository URL.
- `--commit` (**required**) – commit SHA anchoring the task.
- `--runner` – runner type to scaffold (`pytest`, `node`, or `maven`).
- `--task-id` – override the derived task ID/slug.
- `--directory` – output directory (defaults to `<task_id>`).
- `--force` – overwrite an existing directory after confirmation.

Creates the manifest (`task.json`), guardrail directories, runner-specific
dependency stubs, and placeholder files (`description.md`, `gold_patch.diff`).

## `task validate`

Validate guardrails locally or inside Modal.

- `--modal` – run inside Modal instead of locally (requires Modal credentials).
- `--full` – execute the repository’s native test command described in
  `tests.full`.

Baseline guardrails must pass (`pass2pass`) and fail (`fail2pass`) before the
golden patch is applied. After applying the patch both suites must succeed.
`--full` runs prerequisites, the command, and cleanup declared in the manifest.

## `task build`

Build a reusable Modal image or snapshot (currently available for pytest
runners).

- `--name` – friendly Modal image name (`<task_id>-image` by default).
- `--python-version` – override the Python version for the base image.

The command installs declared dependencies, prepares `/opt/sweap-venv`, and
records `environment.modal_image` or `environment.modal_image_id` inside the
manifest for later Modal runs.

## `task run`

Execute the evaluation workflow locally (Modal) or enqueue a remote run.

- `--model` (**required**) – model identifier stored in evaluation artifacts.
- `--modal/--no-modal` – toggle local Modal execution (legacy non-Modal path is
  not implemented).
- `--remote` – enqueue via the backend API and poll for results.
- `--remote-task-id` / `--remote-version` – override remote identifiers when the
  manifest lacks metadata.
- `--llm-command` – custom Codex invocation. Free-form prompts are wrapped in
  the default `codex exec …` prefix if needed.
- `--skip-baseline` – skip baseline guardrail execution (use sparingly).
- LLM credential options: `--codex-auth`, `--codex-config`, `--codex-api-key`,
  `--codex-api-key-file`, and `--skip-llm-login/--require-llm-login`.

Local Modal runs download artifacts (evaluation JSON + transcript) directly into
the bundle directory. Remote runs store artifacts with the backend and download
them at the end of polling.

## `task submit`

Register or update a task with the backend and upload the bundle archive.

- `--visibility` – `private` (default) or `public`.
- `--remote-id` – update an existing task even if the manifest lacks metadata.
- `--notes` – optional version notes stored with the bundle.

The manifest’s `metadata.remote` section is updated with the task ID, slug,
visibility, and bundle version returned by the backend.

## `task info`

Fetch remote task metadata from the backend.

- `--remote-task-id` – override the task ID stored in the manifest.

Outputs task title, repository details, visibility, status, and latest bundle
version, plus any stored description text.

## `task fetch-bundle`

Download and optionally extract a bundle from the backend.

- `--remote-task-id` – override the manifest’s task ID.
- `--version` – specific bundle version (defaults to recorded or latest).
- `--output` – destination zip path (defaults to `downloaded_bundle.zip`).
- `--extract` – unzip into the working directory after download.

## `task runs-get`

Retrieve a remote run record and (optionally) its artifacts.

- `--bundle-dir` – location to write downloaded artifacts.
- `--download-artifacts` – toggle artifact download.

The command prints the run record as formatted JSON and saves artifacts such as
evaluation reports or transcripts when requested.
