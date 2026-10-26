# Opendesk

Opendesk is open-source customer-service and ticketing software built on Frappe Framework.

Manage support conversations, team assignments, service commitments, and self-service content in one application. Agents work in a Vue 3 desk at `/opendesk`; customers use the Studio-based ticket portal and knowledge base at `/help`.

[![License: AGPL-3.0](https://img.shields.io/badge/license-AGPL--3.0-blue)](LICENSE)
[![Frappe](https://img.shields.io/badge/stack-Frappe-0089FF)](https://frappeframework.com/)
[![Vue 3](https://img.shields.io/badge/frontend-Vue%203-42b883)](https://vuejs.org/)

Workflows: [Build](https://github.com/ikhsanddy/opendesk/actions/workflows/build.yml) · [Lint](https://github.com/ikhsanddy/opendesk/actions/workflows/lint.yml) · [Server tests](https://github.com/ikhsanddy/opendesk/actions/workflows/server-tests.yml) · [UI tests](https://github.com/ikhsanddy/opendesk/actions/workflows/ui-tests.yml)

## Features

- **Ticket workspace:** saved views, filters, tags, bulk replies, bulk edits, bulk assignment, and ticket export.
- **Service-level agreements:** priority-based response and resolution targets, service days, and holiday lists.
- **Team operations:** assignment rules, agent teams, and agent availability statuses.
- **Reusable workflows:** saved replies, ticket templates, and custom ticket fields.
- **Knowledge base:** categories, articles, reader feedback, and full-text article search.
- **Customer portal:** ticket creation, ticket conversations, and knowledge-base access at `/help`.
- **Email and realtime:** Email Account integration for incoming conversations, live ticket/comment updates, and typing indicators.
- **Integrations:** optional ERPNext customer synchronization and telephony call logs through the required `telephony` app.

## Architecture

The backend uses Python and Frappe Framework with MariaDB, Redis, and Socket.IO. The agent SPA uses Vue 3, Vite, frappe-ui, and Tailwind CSS.

| Path | Responsibility |
| --- | --- |
| `opendesk/` | Frappe app: `api/`, `opendesk/doctype/`, `patches/`, `setup/`, and `integrations/` |
| `desk/` | Vue agent SPA and Vite configuration |
| `studio/opendesk/` | Studio customer portal and knowledge base |
| `shared/` | Shared frontend code, published locally as `@opendesk/shared` |
| `e2e/` | Playwright browser tests and fixtures |
| `docker/` | Container configuration and initialization scripts |
| `realtime/` | Socket.IO ticket-room handlers |

## Getting started

Prepare a [Frappe development environment](https://frappeframework.com/docs/user/en/installation) with Bench, Python, Node.js, Yarn, MariaDB, and Redis. Run the following in a shell supported by Bench; these commands create a local development site, not a production deployment. `pyproject.toml` pins `frappe >=17.0.0-dev,<18` and `telephony >=0.0.1,<1.0.0`; use a bench with a Frappe `develop` checkout that satisfies the pinned range.

```sh
bench init opendesk-bench --frappe-branch develop
cd opendesk-bench
bench get-app https://github.com/frappe/telephony
bench get-app https://github.com/ikhsanddy/opendesk
bench new-site opendesk.localhost
bench --site opendesk.localhost install-app telephony
bench --site opendesk.localhost install-app opendesk
bench build --app opendesk
bench start
```

Open the agent desk at **http://opendesk.localhost:8000/opendesk** and the customer portal/knowledge base at **http://opendesk.localhost:8000/help**. Ensure `opendesk.localhost` resolves to your local machine. Sign in with the Administrator credentials chosen during site creation.

### Frontend development

Keep `bench start` running. From another terminal in the bench directory:

```sh
cd apps/opendesk
yarn install
yarn dev
```

The root `dev` script runs `desk/`'s Vite server; open the URL it prints. `desk/vite.config.js` enables the frappe-ui Frappe proxy, so keep the bench site running for API, authentication, and realtime behavior. The desk also links `@framework/ui` from the sibling Frappe checkout at `apps/frappe/ui`.

## Configuration

Open **Settings** from the agent sidebar. Most options require an Administrator or Manager role.

| Setting | What to configure |
| --- | --- |
| **App Settings → General** | Branding, default ticket type, ticket restrictions, auto-close rules, and team assignment restrictions |
| **Email Settings → Email Accounts** | Incoming and outgoing accounts; incoming support mail uses the app's Email Account override. Notification templates live under **Email Notifications**. |
| **App Settings → SLA Policies** | Priority-based targets, service days, and default SLA selection; **Business Holidays** supplies the holiday list |
| **Customer Portal → Portal Settings** | Customer and visitor access policies for the portal |
| **Customer Portal → Knowledge Base** | Public knowledge base, guest home behavior, and article voting; **Integrations** holds ERPNext and Telephony setup |

## Development

Read [CONTRIBUTING.md](CONTRIBUTING.md) and the repository's `AGENTS.md` before changing behavior.

- Python hooks use **Black**, **isort**, and **Flake8** in `.pre-commit-config.yaml`. Flake8 also has `.flake8`; the hook explicitly uses `.github/helpers/.flake8_strict`.
- Frontend style is configured in `.eslintrc.js` and `.prettierrc.json`; Prettier is included in the pre-commit hooks.
- Run backend tests from the bench directory on a development/test site:

  ```sh
  bench --site opendesk.localhost run-tests --app opendesk
  ```

- Browser tests use Playwright against a running bench site. From `apps/opendesk`, after installing Chromium with `npx playwright install chromium`, run:

  ```sh
  BASE_URL=http://localhost:8000 SITE_NAME=opendesk.localhost yarn test:e2e
  ```

  This invokes `playwright test`. Set `ADMIN_PASSWORD` to the site's Administrator password; the test setup creates test personas and data, so use a disposable site. See `e2e/README.md` and `playwright.config.ts` for details.

Report vulnerabilities privately as described in [SECURITY.md](SECURITY.md).

## License

Licensed under [GNU AGPL-3.0](LICENSE).

Copyright (c) Frappe Technologies Pvt. Ltd. and Opendesk contributors.
