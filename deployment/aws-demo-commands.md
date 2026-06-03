# LaunchBot Amazon Linux Deployment Command Reference

This file is a copy-paste reference for the deployment walkthrough in `README.md`.

Use this with:

```text
Amazon Linux 2023
x86_64 instance
t3.micro first
t3.medium if chatbot responses time out
```

## 1. Verify the server

```bash
whoami
uname -m
cat /etc/os-release
```

Expected user:

```text
ec2-user
```

Expected architecture:

```text
x86_64
```

## 2. Install server tools

```bash
sudo dnf update -y

sudo dnf install -y \
  git \
  nginx \
  unzip \
  rsync \
  sqlite \
  python3.11 \
  python3.11-pip \
  python3.11-devel \
  gcc \
  gcc-c++ \
  make \
  cmake \
  openssl-devel \
  libffi-devel \
  sqlite-devel \
  nodejs \
  npm

python3.11 --version
node --version
npm --version
nginx -v
curl --version
```

## 3. Add swap

```bash
sudo fallocate -l 6G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h
```

## 4. Install Ollama and pull models

```bash
curl -fsSL https://ollama.com/install.sh | sh

sudo systemctl enable ollama
sudo systemctl start ollama
sudo systemctl status ollama --no-pager
```

Configure Ollama:

```bash
sudo systemctl edit ollama.service
```

Paste:

```ini
[Service]
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_CONTEXT_LENGTH=2048"
Environment="OLLAMA_KEEP_ALIVE=0"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
```

Reload:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

Pull models:

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
ollama list
curl http://127.0.0.1:11434/api/tags
```

## 5. Upload the app zip

Run this from your local computer:

```bash
scp -i ~/Downloads/launchbot-demo-key.pem \
  ~/Downloads/launchbot-deployment-assistant-student.zip \
  ec2-user@YOUR_EC2_PUBLIC_DNS:~
```

## 6. Place the app on the server

Run this on EC2:

```bash
cd ~
unzip -o launchbot-deployment-assistant-student.zip

sudo mkdir -p /var/www/launchbot
sudo rsync -av --delete launchbot-deployment-assistant/ /var/www/launchbot/
sudo chown -R ec2-user:nginx /var/www/launchbot

ls /var/www/launchbot
```

## 7. Configure Flask

```bash
cd /var/www/launchbot/server

python3.11 -m venv --copies .venv
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

cp ../deployment/sample-prod.env .env
```

Generate a secret:

```bash
python - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
```

Edit `.env`:

```bash
nano .env
```

Expected production settings:

```bash
FLASK_ENV=production
SECRET_KEY=paste-your-generated-secret-key-here

DATABASE_PATH=/var/www/launchbot/server/instance/launchbot.sqlite
CHROMA_PATH=/var/www/launchbot/server/instance/chroma
COLLECTION_NAME=deployment_runbook

OLLAMA_BASE_URL=http://127.0.0.1:11434
GENERATION_MODEL=llama3.2
EMBEDDING_MODEL=nomic-embed-text

TOP_K=2
TEMPERATURE=0
```

Permissions:

```bash
chmod 640 .env
sudo chown ec2-user:nginx .env
```

## 8. Initialize data

```bash
cd /var/www/launchbot/server
source .venv/bin/activate

mkdir -p instance
python init_db.py
python seed_chroma.py
ls -lah instance
```

## 9. Build React into Flask

```bash
cd /var/www/launchbot/client

npm install
npm run build:flask

ls /var/www/launchbot/server/app/templates
ls /var/www/launchbot/server/app/static/assets
```

## 10. Test Gunicorn manually

```bash
cd /var/www/launchbot/server
source .venv/bin/activate

gunicorn --workers 1 --threads 2 --timeout 300 --bind 127.0.0.1:8000 wsgi:app
```

In a second SSH session:

```bash
curl -i http://127.0.0.1:8000/api/health
curl -i http://127.0.0.1:8000/api/rag/health

curl -i -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Why can my friend not open my localhost app?"}'
```

Stop manual Gunicorn with `Ctrl + C`.

## 11. Install systemd service

```bash
sudo cp /var/www/launchbot/deployment/launchbot.service /etc/systemd/system/launchbot.service

sudo systemctl daemon-reload
sudo systemctl enable launchbot
sudo systemctl start launchbot
sudo systemctl status launchbot --no-pager

curl -i http://127.0.0.1:8000/api/health
```

## 12. Configure Nginx

```bash
sudo cp /var/www/launchbot/deployment/nginx-launchbot.conf /etc/nginx/conf.d/launchbot.conf

sudo systemctl enable nginx
sudo systemctl start nginx
sudo nginx -t
sudo systemctl reload nginx

curl -i http://127.0.0.1/api/health
```

## 13. Public verification

Open:

```text
http://YOUR_EC2_PUBLIC_DNS/
```

Test:

```text
http://YOUR_EC2_PUBLIC_DNS/api/health
http://YOUR_EC2_PUBLIC_DNS/api/rag/health
```

Ask:

```text
Why can my friend not open my localhost app?
```

## 14. Useful troubleshooting commands

```bash
free -h
df -h
sudo systemctl status ollama --no-pager
sudo systemctl status launchbot --no-pager
sudo systemctl status nginx --no-pager
sudo journalctl -u ollama -n 100 --no-pager
sudo journalctl -u launchbot -n 100 --no-pager
sudo nginx -t
```
