# Roadmap Tracker

`ROADMAP.md` is now a generated human-readable report. Do not edit it manually.

The reviewable source artifact is:

- `docs/roadmap/slices.export.jsonl`

The local working cache is:

- `var/roadmap/roadmap.sqlite`

`var/` is ignored by Git. Commit the JSONL export and generated `ROADMAP.md` together.

## Commands

```bash
python -m backend.app.roadmap list --status Ready
python -m backend.app.roadmap next
python -m backend.app.roadmap show 2.17.4
python -m backend.app.roadmap add-slice 2.17.4.1 "Title" --after 2.17.4 --status Backlog --goal "..." --user-value "..." --scope "..."
python -m backend.app.roadmap update-status 2.17.4 Done
python -m backend.app.roadmap import
python -m backend.app.roadmap export
python -m backend.app.roadmap render
python -m backend.app.roadmap check
```

## Workflow

1. Use `python -m backend.app.roadmap next` to find the next slice.
2. Change roadmap state through the CLI, or edit `docs/roadmap/slices.export.jsonl`
   and then run `import/check/render`.
3. Run:

```bash
python -m backend.app.roadmap check
python -m backend.app.roadmap render
python -m backend.app.roadmap export
git diff --check
```

4. Review diffs in `docs/roadmap/slices.export.jsonl` first. Review `ROADMAP.md` as
   the generated report for humans.

## Record Model

The JSONL export contains one record per line:

- `meta`: product vision, blocked/open sections, next-task text.
- `iteration`: iteration id, title, status, goal, ordering.
- `slice`: slice id, iteration id, title, status, ordering, body markdown,
  completion date, and optional payload.

The first tracker version preserves historical slice Markdown in `body_markdown`
instead of fully normalizing every old field. New slices should still use the standard
slice fields in that Markdown body.

