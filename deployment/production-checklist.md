# LaunchBot Production-Style Verification Checklist

Use this checklist before you submit deployment evidence.

## AWS instance

- [ ] Amazon Linux 2023 instance is running.
- [ ] Security group allows SSH from My IP.
- [ ] Security group allows HTTP from Anywhere IPv4.
- [ ] Ports `5000`, `8000`, and `11434` are not publicly open.
- [ ] Swap is active.

## Ollama

- [ ] Ollama service is active.
- [ ] `llama3.2` is pulled.
- [ ] `nomic-embed-text` is pulled.
- [ ] `curl http://127.0.0.1:11434/api/tags` returns model information.

## Flask and data

- [ ] Python virtual environment uses Python 3.11.
- [ ] `server/.env` exists and has a unique `SECRET_KEY`.
- [ ] `GENERATION_MODEL=llama3.2`.
- [ ] `EMBEDDING_MODEL=nomic-embed-text`.
- [ ] SQLite database exists.
- [ ] Chroma folder exists.
- [ ] `python seed_chroma.py` has completed successfully.

## React build

- [ ] `npm run build:flask` completed successfully.
- [ ] `server/app/templates/index.html` exists.
- [ ] `server/app/static/assets` contains built assets.

## Services

- [ ] `launchbot` service is active.
- [ ] `nginx` service is active.
- [ ] `curl http://127.0.0.1:8000/api/health` returns `200 OK`.
- [ ] `curl http://127.0.0.1/api/health` returns `200 OK`.

## Public app

- [ ] Public URL loads the React app.
- [ ] Public `/api/health` route returns JSON.
- [ ] Public `/api/rag/health` route returns JSON.
- [ ] A chat thread can be created.
- [ ] The chatbot returns a source-backed answer.
- [ ] Source cards appear in the UI.

## Cost and cleanup

- [ ] Instance is stopped or terminated when finished.
- [ ] Unused volumes are deleted when appropriate.
- [ ] Unused Elastic IPs are released if created.
- [ ] AWS billing dashboard or Free Tier usage box has been checked.
