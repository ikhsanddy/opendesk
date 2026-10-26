# Contributing to Opendesk

Thank you for improving Opendesk. This guide covers local setup, style, tests, and review expectations. Read `AGENTS.md` for deeper architectural and frontend conventions.

## Local setup

Follow the [README](README.md) bench installation first. For frontend work, keep the site running and install the SPA dependencies:

```sh
cd apps/opendesk
yarn install
yarn dev
```

The dev server reads `desk/vite.config.js`, which proxies Frappe requests and writes production assets to `opendesk/public/desk`. The backend must remain running for API, authentication, and realtime behavior.

Install the repository's Git hooks once per clone:

```sh
pre-commit install
pre-commit run --all-files
```

## Commit conventions

Commits use [Conventional Commits](https://www.conventionalcommits.org/) as enforced by `commitlint.config.mjs`. Allowed types are `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, and `test`; types are lower-case and a subject is required. Example:

```text
docs(readme): document the local bench setup
```

Keep pull requests focused. Branches in this repository target `main`, `main-hotfix`, or `develop`.

## Code style

- **Python:** Black and isort (Black profile) format code; Flake8 checks it. Configuration lives in `.pre-commit-config.yaml` and `.flake8`. The pre-commit Flake8 hook runs with `.github/helpers/.flake8_strict`.
- **Frontend:** ESLint with Vue 3, TypeScript, Tailwind, and Prettier integrations via `.eslintrc.js`. Formatting preferences are in `.prettierrc.json`, and `.lintstagedrc` configures staged-file ESLint fixes.
- **Vue:** Prefer the Composition API and `<script setup lang="ts">`, Tailwind utility classes with semantic tokens, and Lucide icons for new components. See `AGENTS.md`.

Run the configured hooks before pushing:

```sh
pre-commit run --all-files
```

## Tests

Backend behavior changes require tests. Run the full app suite from the bench directory:

```sh
bench --site opendesk.localhost run-tests --app opendesk
```

Place test helpers in `opendesk/test_utils.py` rather than defining factories inline, and add tests under the existing app test layout.

Browser tests use Playwright against a disposable bench site:

```sh
cd apps/opendesk
npx playwright install chromium
BASE_URL=http://localhost:8000 SITE_NAME=opendesk.localhost yarn test:e2e
```

Every record created by a spec must use a unique name, and site-wide settings changed by a spec must be restored. See `e2e/README.md` for the persona and fixture model.

## Documentation

When a feature has a specification document, the spec is its living source of truth. Update it in the same change that alters behavior: add new APIs, components, and decisions, and remove sections for removed behavior. Do not defer spec updates.

## Pull request checklist

- [ ] The change is scoped to one problem and its description explains the behavior change.
- [ ] Commit titles follow Conventional Commits.
- [ ] Pre-commit hooks and the relevant linters pass locally.
- [ ] Backend changes include tests, and the app test suite passes for affected areas.
- [ ] UI changes include or update Playwright coverage where a user journey is affected.
- [ ] Affected specifications and user-facing documentation are updated.
- [ ] No unrelated files, generated assets, or reformatting are included.
