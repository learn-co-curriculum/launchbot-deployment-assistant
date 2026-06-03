# What Has Been Preconfigured

This project is designed for deployment practice. You are not expected to build the full app during the deployment lesson.

## Frontend

The React app already includes:

- Thread sidebar
- Chat window
- Message bubbles
- Source cards
- Loading and error states
- API service functions that call relative `/api` routes in production

## React build integration

The `client/package.json` file includes:

```bash
npm run build:flask
```

That command runs:

```bash
vite build && node scripts/copy-build.js
```

The copy script moves the Vite build into Flask:

```text
client/dist/index.html → server/app/templates/index.html
client/dist/assets/    → server/app/static/assets/
```

## Backend routing

The Flask backend separates routes:

```text
/       React app
/api    Backend API routes
```

This prevents React Router and Flask API routes from competing for the same URL paths.

## Environment variables

The backend reads production settings from `server/.env`.

Important values:

```text
DATABASE_PATH
CHROMA_PATH
OLLAMA_BASE_URL
GENERATION_MODEL
EMBEDDING_MODEL
TOP_K
TEMPERATURE
```

## Data persistence

SQLite stores chat threads:

```text
server/instance/launchbot.sqlite
```

Chroma stores vectors:

```text
server/instance/chroma
```

## Deployment files

The `deployment` folder includes:

```text
launchbot.service       systemd service for Amazon Linux 2023
nginx-launchbot.conf    Nginx reverse proxy config
sample-prod.env         production environment template
aws-demo-commands.md    command reference
production-checklist.md verification checklist
```
