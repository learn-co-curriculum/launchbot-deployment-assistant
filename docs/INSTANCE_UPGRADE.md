# Optional Upgrade: Change from t3.micro to t3.medium

Start with `t3.micro` to test the lowest-cost path. If the React app loads but chatbot responses time out or return a `503` / gateway error, upgrade the same EC2 instance to `t3.medium`.

## Why this helps

The app runs all of these on one instance:

```text
Nginx
Gunicorn
Flask
SQLite
Chroma
LangChain
Ollama
llama3.2
nomic-embed-text
```

A `t3.micro` has very limited memory for this stack. A `t3.medium` gives the same deployment more room to run the model and backend services.

## Upgrade steps

1. In the EC2 console, select your instance.
2. Choose **Instance state → Stop instance**.
3. Wait until the instance is stopped.
4. Choose **Actions → Instance settings → Change instance type**.
5. Select `t3.medium`.
6. Save the change.
7. Start the instance again.
8. Copy the new public DNS if it changed.
9. Reconnect and verify the services:

```bash
sudo systemctl status ollama --no-pager
sudo systemctl status launchbot --no-pager
sudo systemctl status nginx --no-pager
curl -i http://127.0.0.1/api/health
curl -i http://127.0.0.1/api/rag/health
```

## What stays the same

The app files, `.env`, SQLite database, Chroma files, systemd service, Nginx config, and pulled Ollama models should remain on the EBS volume.

## What may change

The public DNS and public IPv4 address may change after the instance stops and starts.
