# Glavred

Glavred is an AI-native editorial service for expert authors who want to run a personal
media system instead of writing isolated posts by hand.

The current repository is a project foundation. It contains a minimal React/Vite
application, a small domain baseline for the editorial workflow, test infrastructure,
documentation, demo notes, and the design handoff supplied in `ui-design-systems/`.

## Source Requirements

Primary source requirements file: `glavred.md`.

Current status: `glavred.md` exists but is empty. Until it is filled in, product
requirements are treated as blocked. The existing design handoff is used only as a
secondary concept/design source.

## Product Direction

The available design handoff describes Glavred as an AI newsroom for personal media.
The durable editorial loop is:

`Sources -> Insights -> Plan -> Brief -> Draft -> Editing -> Release -> Analytics`

Human approval gates are expected at plan approval, brief approval, and final editing.

## Quick Start

```bash
npm install
npm run dev
```

Run tests:

```bash
npm test
```

Run the smoke build:

```bash
npm run smoke
```

## Documentation

- [Roadmap](ROADMAP.md)
- [System architecture overview](docs/architecture/SYSTEM_ARCHITECTURE_OVERVIEW.md)
- [Architecture decision records](docs/adr/README.md)
- [Contributor guide](docs/contributor/CONTRIBUTING.md)
- [Developer guide](docs/developer/DEVELOPER_GUIDE.md)
- [User guide](docs/user/USER_GUIDE.md)
- [Demo](demo/README.md)

## Development Model

This project is developed iteratively through small slices. Each slice should leave the
product runnable, tested, documented, and demonstrable.

GitHub repository creation is intentionally deferred until the user confirms it.
