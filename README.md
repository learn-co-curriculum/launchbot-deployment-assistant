# Technical Lesson: Deploy a Full-Stack AI Application to AWS

## Introduction

In local development, your app runs on your computer. That is useful while building, but other users cannot open your `localhost` URL from their own browser.

In this lesson, you will deploy a full-stack AI application to AWS so the React interface, Flask API, Chroma vector database, SQLite thread storage, LangChain RAG workflow, and Ollama model service run on an EC2 instance. You will follow the process **Identify → Assemble → Execute → Verify** so each deployment step has a clear purpose and a clear success check.

**Learning outcome:** You will deploy a full-stack React and Flask RAG chatbot within an AWS EC2 environment by configuring server tools, environment variables, model services, persistent data paths, Gunicorn, systemd, and Nginx to a standard where the public app loads, API health checks pass, and the chatbot returns a source-backed answer.

---

## Scenario

You built a full-stack AI app locally and told a friend:

```text
Go to http://localhost:5000
```

Your friend saw:

```text
This site can’t be reached.
localhost refused to connect.
```

The app was working, but only on your machine. In this lesson, you will deploy LaunchBot to AWS so another computer can access the app through a public URL.

LaunchBot is a deployment runbook assistant. It answers questions about deployment using retrieved source context from a small Chroma knowledge base. The app is intentionally small, but it uses the same deployment pattern as larger AI-integrated full-stack apps.

---

## Tools and Resources

You will use:

- AWS account
- Amazon EC2
- Amazon Linux 2023
- SSH or EC2 Instance Connect
- Python 3.11
- Node.js and npm
- Flask
- React + Vite
- Gunicorn
- Nginx
- SQLite
- Chroma
- LangChain
- Ollama
- `llama3.2`
- `nomic-embed-text`

You will also use the project files in this zip package.

---

## Before You Start: What Has Already Been Built

You are deploying a working app, not writing the entire app from scratch.

The app already includes:

- **React routes and components** for the threaded chat interface.
- **Flask API routes** under `/api` so backend routes do not conflict with React routes.
- **A Flask root route** that serves the built React app from `/`.
- **A build helper command**:

```bash
npm run build:flask
```

This command builds the React app with Vite and copies the result into Flask:

```text
client/dist/index.html → server/app/templates/index.html
client/dist/assets/    → server/app/static/assets/
```

The app also includes environment variables so local and production paths can be different:

```text
DATABASE_PATH
CHROMA_PATH
COLLECTION_NAME
OLLAMA_BASE_URL
GENERATION_MODEL
EMBEDDING_MODEL
TOP_K
TEMPERATURE
```

In development, those paths can point to local project folders. In production, they point to files on the EC2 instance.

---

## Local development setup

Before deploying, let's test the app locally.

### 1. Start Ollama and pull models

Start by installing any Ollama models the application uses if not yet pulled on your local environment:

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
ollama run llama3.2 "Reply with one short sentence."
```

### 2. Set up the Flask backend

Configure the backend and databases:

```bash
cd server
pipenv install
pipenv shell

cp .env.example .env
python init_db.py
python seed_chroma.py
```

Run the Flask application:

```bash
flask --app wsgi run --debug
```

The backend runs at:

```text
http://127.0.0.1:5000
```

### 3. Set up the React frontend

In a second terminal:

```bash
cd client
npm install
npm run dev
```

The React dev server runs at:

```text
http://127.0.0.1:5173
```

### 4. Test Flask-served React

To test the production-style frontend locally:

```bash
cd client
npm run build:flask

cd ../server
pipenv shell
flask --app wsgi run
```

Open:

```text
http://127.0.0.1:5000
```

Once you've verified the app is up and running, feel free to close down the React and Flask applications.

---

# Deployment

## Task 1: Identify the Deployment Architecture

### Step 1. Identify what moves from local to production

**Review the production request path.**

```text
Browser
→ EC2 public URL
→ Nginx
→ Gunicorn
→ Flask
→ LangChain
→ Chroma
→ Ollama
→ response with sources
```

This helps you understand what each tool is responsible for before you start installing and configuring services.

**What this does:** You are identifying the pieces of the deployed system so you can verify them later.

**Evidence of success:** You can explain why `localhost` is not enough and why the app needs to run on a public server.

---

## Task 2: Assemble the EC2 Instance

### Step 1. Launch an EC2 instance

**Open the EC2 launch wizard.**

If you don't already have one, create an AWS account. Then navigate to EC2 to launch an instance.

```text
AWS Console
→ EC2
→ Instances
→ Launch instances
```

Use these settings:

```text
Name: launchbot-free-tier-test
AMI: Amazon Linux 2023 AMI
Architecture: 64-bit x86
Instance type: t3.micro
Key pair: create or choose a .pem key
Storage: 30 GiB gp3
Auto-assign public IP: enabled
```

Security group inbound rules:

| Type | Port | Source |
|---|---:|---|
| SSH | 22 | My IP |
| HTTP | 80 | Anywhere IPv4 |

Do **not** open these ports:

```text
5000
8000
11434
```

**What this does:** The EC2 instance becomes the public server for the application. The security group allows SSH for you and HTTP for browser users, while keeping Flask, Gunicorn, and Ollama private to the server.

**Evidence of success:** The instance state is `Running`, and status checks eventually show `2/2 checks passed`.

### Step 2. Understand the free-tier limitation

**Start with `t3.micro`, but be ready to upgrade.**

A `t3.micro` instance is useful for a low-cost smoke test. It may be able to load the public React app and pass basic health checks. However, it may be too slow for the chatbot because the same small instance is running Flask, Chroma, SQLite, Nginx, and Ollama.

If the app loads but the chatbot times out or returns a `503` response, you can upgrade the same instance to `t3.medium`.

**What this does:** You are testing the lowest-cost option first, then making an evidence-based scaling decision.

**Evidence of success:** You know that a slow or timed-out chatbot on `t3.micro` is an infrastructure limitation, not necessarily an app-code failure.

---

## Task 3: Connect to the EC2 Instance

### Step 1. Connect with the correct user

**Connect using `ec2-user`.**

From your local terminal:

```bash
chmod 400 ~/Downloads/launchbot-demo-key.pem

ssh -i ~/Downloads/launchbot-demo-key.pem ec2-user@YOUR_EC2_PUBLIC_DNS
```

Replace:

```text
YOUR_EC2_PUBLIC_DNS
```

with your instance’s public DNS value from the EC2 console.

If you use EC2 Instance Connect in the browser, use this username:

```text
ec2-user
```

**What this does:** Amazon Linux uses `ec2-user` as the default login user. The private key remains on your local computer and is used only to authenticate the connection.

**Evidence of success:** Your terminal prompt starts with something like:

```text
[ec2-user@ip-... ~]$
```

### Step 2. Confirm the operating system

**Check the OS.**

```bash
cat /etc/os-release
```

Expected output includes:

```text
NAME="Amazon Linux"
VERSION="2023"
```

**What this does:** You are verifying that the commands in this lesson match the server’s operating system.

**Evidence of success:** The server is running Amazon Linux 2023.

---

## Task 4: Assemble Server Tools

### Step 1. Update packages

**Update the server.**

```bash
sudo dnf update -y
```

Amazon Linux uses `dnf`, not `apt`.

**What this does:** The package index and installed packages are brought up to date.

**Evidence of success:** The command finishes without an error.

### Step 2. Install required packages

**Install Python, build tools, Nginx, SQLite, Git, unzip, rsync, Node, and npm.**

```bash
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
```

Verify versions:

```bash
python3.11 --version
node --version
npm --version
nginx -v
curl --version
```

You likely do not need to install `curl` manually unless your instance does not already have it. Amazon Linux commonly includes a minimal curl package. If you hit an issue running curl, you can also run `sudo dnf install -y curl`

**What this does:** These tools let the server run the Flask backend, install Python dependencies, build the React frontend, serve public traffic, and call installation scripts.

**Evidence of success:** Version numbers print for Python, Node, npm, Nginx, and curl.

### Step 3. Add swap

**Add swap for the low-memory instance.**

```bash
sudo fallocate -l 6G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h
```

**What this does:** Swap gives the server extra disk-backed memory space. It is slower than RAM, but it can help avoid crashes on a small instance.

**Evidence of success:** `free -h` shows a `Swap` row with about `6.0Gi`.

---

## Task 5: Execute the Ollama Setup

### Step 1. Install Ollama

**Install and start Ollama.**

```bash
curl -fsSL https://ollama.com/install.sh | sh

sudo systemctl enable ollama
sudo systemctl start ollama
sudo systemctl status ollama --no-pager
```

You may see:

```text
WARNING: No NVIDIA/AMD GPU detected. Ollama will run in CPU-only mode.
```

That is expected for this low-cost EC2 deployment.

**What this does:** Ollama becomes a local model service running on the EC2 instance.

**Evidence of success:** The Ollama service status is `active (running)`.

### Step 2. Configure Ollama for a small instance

**Create a systemd override for Ollama.**

```bash
sudo systemctl edit ollama.service
```

Paste this block:

```ini
[Service]
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_CONTEXT_LENGTH=2048"
Environment="OLLAMA_KEEP_ALIVE=0"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
```

Save and exit. Then reload and restart:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
sudo systemctl status ollama --no-pager
```

**What this does:** Ollama stays private on the EC2 instance and uses lower-concurrency settings that fit the teaching deployment.

**Evidence of success:** Ollama restarts successfully.

### Step 3. Pull the required models

**Pull the generation and embedding models.**

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

Verify:

```bash
ollama list
curl http://127.0.0.1:11434/api/tags
```

Test generation:

```bash
ollama run llama3.2 "Reply with one short sentence."
```

**What this does:** `llama3.2` generates chatbot answers. `nomic-embed-text` generates embeddings for Chroma retrieval.

**Evidence of success:** Both models appear in `ollama list`, and the model returns a short response.

---

## Task 6: Execute the App Upload

### Step 1. Upload the zip from your local computer

**Zip the project and upload it to the ec2 instance.**

Start by compressing the project using the included script. From the project root directory, run:

```bash
bash ./scripts/create_deployment_zip.sh
```

This script also removes anything that doesn't need to be in the zip file, such as the `.venv` created locally, `node_modules`, `__pycache__`, etc.

Then add the zip file to the ec2 instance, ensuring to enter the correct file paths and your public DNS (do not include the square brackets):

```bash
scp -i ~/[FILE PATH TO KEY]/launchbot-demo-key.pem \
  ~/[FILE PATH TO ZIP]/launchbot-deployment-assistant.zip \
  ec2-user@[YOUR_EC2_PUBLIC_DNS]:~
```

such as:
```bash
scp -i ~/sd_curriculum/backend_course/launchbot-demo-key.pem \
  ~/Downloads/launchbot-deployment-assistant.zip \
  ec2-user@ec2-some-numbers.us-east-2.compute.amazonaws.com:~
```

Note: scp command is not copying the private key to the server; the `-i` option tells `scp` which local key to use for authentication. Never upload your `.pem` private key to the EC2 instance.

**What this does:** The app is copied to the EC2 user’s home folder.

### Step 2. Move the app into `/var/www`

**Unzip and place the project.**

```bash
cd ~
unzip -o launchbot-deployment-assistant.zip

sudo mkdir -p /var/www/launchbot
sudo rsync -av --delete launchbot-deployment-assistant/ /var/www/launchbot/
sudo chown -R ec2-user:nginx /var/www/launchbot

ls /var/www/launchbot
```

Expected output includes:

```text
client
server
deployment
README.md
TECHNICAL_LESSON_AWS_DEPLOYMENT.md
```

**What this does:** The app is copied into the server folder where Gunicorn and Nginx will use it.

**Evidence of success:** The project files are visible in `/var/www/launchbot`.

---

## Task 7: Configure the Flask Backend

### Step 1. Create the virtual environment

**Create the app’s Python environment with Python 3.11.**

```bash
cd /var/www/launchbot/server

python3.11 -m venv --copies .venv
source .venv/bin/activate

python --version
```

Expected output:

```text
Python 3.11.x
```

**What this does:** The backend gets its own isolated Python environment. Do not change the system `python3` command.

**Evidence of success:** `python --version` shows Python 3.11 while the virtual environment is active.

### Step 2. Install backend dependencies

**Install Flask, LangChain, Chroma, Gunicorn, and related packages.**

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**What this does:** These packages let the Flask app run, connect to Ollama, store vectors in Chroma, and run through Gunicorn.

**Evidence of success:** The install completes without errors.

### Step 3. Create the production environment file

**Copy and edit the environment file.**

```bash
cp ../deployment/sample-prod.env .env
```

Generate a secret key:

```bash
python - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
```

Copy the key generated.

Edit `.env`:

```bash
nano .env
```

Use this configuration:

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

Then write the file and exit. You can check that it saved correctly by opening it again using:

```bash
nano .env
```

Once out of nano and back in the regular command line, set permissions:

```bash
chmod 640 .env
sudo chown ec2-user:nginx .env
```

**What this does:** The app reads production paths and model settings from `.env` instead of hard-coding them.

**Evidence of success:** `.env` contains the correct paths and model names.

---

## Task 8: Execute the Database and Vector Store Setup

### Step 1. Initialize SQLite

**Create the chat database.**

```bash
cd /var/www/launchbot/server
source .venv/bin/activate

mkdir -p instance
python init_db.py
```

**What this does:** SQLite creates the tables used for threads and messages.

**Evidence of success:** The command prints a success message, and `instance/launchbot.sqlite` exists.

### Step 2. Seed Chroma

**Create the vector database from the runbook chunks.**

```bash
python seed_chroma.py
```

**What this does:** The script embeds the approved deployment runbook chunks with `nomic-embed-text` and stores them in Chroma.

**Evidence of success:** The command reports that the Chroma collection was seeded.

Verify:

```bash
ls -lah instance
```

Expected output includes:

```text
launchbot.sqlite
chroma/
```

---

## Task 9: Execute the React Production Build

### Step 1. Build React into Flask

**Build the frontend and copy it into Flask.**

```bash
cd /var/www/launchbot/client

npm install
npm run build:flask
```

**What this does:** Vite creates the production React build, and the project script copies the output into Flask’s `templates` and `static` folders.

**Evidence of success:** You see output similar to:

```text
Copied React build into Flask:
- /var/www/launchbot/server/app/templates/index.html
- /var/www/launchbot/server/app/static/assets
```

Verify:

```bash
ls /var/www/launchbot/server/app/templates
ls /var/www/launchbot/server/app/static/assets
```

---

## Task 10: Verify Gunicorn Manually

### Step 1. Start Gunicorn directly

**Run Flask through Gunicorn on localhost.**

```bash
cd /var/www/launchbot/server
source .venv/bin/activate

gunicorn --workers 1 --threads 2 --timeout 300 --bind 127.0.0.1:8000 wsgi:app
```

Leave this running.

**What this does:** Gunicorn runs the Flask app on an internal server port.

**Evidence of success:** Gunicorn starts and waits for requests.

### Step 2. Test the app in a second SSH session

**Open another SSH connection and test the health routes.**

```bash
curl -i http://127.0.0.1:8000/api/health
curl -i http://127.0.0.1:8000/api/rag/health
```

Then test a one-off RAG answer:

```bash
curl -i -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Why can my friend not open my localhost app?"}'
```

> Note: If this takes too long or seems to hang indefinitely, it's likely due to the EC2 instance type. If you wish, you can continue on and return to these checks when you've upgraded your instance type to `t3.medium` or better.

**What this does:** You are verifying the backend, Chroma, Ollama, and RAG workflow before adding systemd and Nginx.

**Evidence of success:** The health routes return `200 OK`, and the RAG endpoint returns an answer with sources.

Stop the manual Gunicorn process in the first SSH session:

```text
Ctrl + C
```

---

## Task 11: Execute the Persistent App Service

### Step 1. Install the systemd service

**Copy the service file.**

```bash
sudo cp /var/www/launchbot/deployment/launchbot.service /etc/systemd/system/launchbot.service
```

Enable and start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable launchbot
sudo systemctl start launchbot
sudo systemctl status launchbot --no-pager
```

**What this does:** systemd runs the Flask/Gunicorn app as a background service and restarts it after reboots or failures.

**Evidence of success:** The service status shows `active (running)`.

### Step 2. Check logs if needed

**View recent app logs.**

```bash
sudo journalctl -u launchbot -n 100 --no-pager
```

**What this does:** Logs help you troubleshoot environment, dependency, or model-service problems.

**Evidence of success:** The logs do not show repeated restart failures.

---

## Task 12: Execute the Nginx Public Web Configuration

### Step 1. Add the Nginx site configuration

**Copy the Nginx config into Amazon Linux’s Nginx config folder.**

```bash
sudo cp /var/www/launchbot/deployment/nginx-launchbot.conf /etc/nginx/conf.d/launchbot.conf
```

Start and enable Nginx:

```bash
sudo systemctl enable nginx
sudo systemctl start nginx
```

Test the config:

```bash
sudo nginx -t
```

Reload Nginx:

```bash
sudo systemctl reload nginx
```

**What this does:** Nginx listens on public port `80` and forwards requests to Gunicorn on `127.0.0.1:8000`.

**Evidence of success:** `sudo nginx -t` reports that the syntax is okay and the test is successful.

### Step 2. Test through Nginx locally

**Call the app through port 80.**

```bash
curl -i http://127.0.0.1/api/health
```

**What this does:** This tests the same Nginx → Gunicorn → Flask path that public users will use.

**Evidence of success:** The response returns `200 OK`.

---

## Task 13: Verify the Public App

### Step 1. Open the public URL

**Open the EC2 public DNS in your browser.**

```text
http://YOUR_EC2_PUBLIC_DNS/
```

Then test:

```text
http://YOUR_EC2_PUBLIC_DNS/api/health
http://YOUR_EC2_PUBLIC_DNS/api/rag/health
```

**What this does:** You are checking that your browser can reach the deployed app from outside the EC2 instance.

**Evidence of success:** The React app loads, and both API URLs return JSON.

### Step 2. Test the chatbot

**Ask a deployment question.**

```text
Why can my friend not open my localhost app?
```

**What this does:** This verifies the full AI workflow.

**Evidence of success:** The assistant returns an answer and displays source cards.

---

## Task 14: Upgrade the Instance if the Chatbot Times Out

### Step 1. Recognize the scaling signal

If the app loads but the chatbot takes too long or returns a `503` / gateway error, the `t3.micro` instance may not have enough memory or CPU capacity for `llama3.2`.

This does not mean your deployment failed, but rather you proved the low-cost deployment path and found the resource limit.

### Step 2. Stop the instance

In AWS:

```text
EC2
→ Instances
→ Select launchbot-free-tier-test
→ Instance state
→ Stop instance
```

Wait until the state is:

```text
Stopped
```

### Step 3. Change the instance type

With the same instance selected:

```text
Actions
→ Instance settings
→ Change instance type
```

Choose:

```text
t3.medium
```

Then save the change and start the instance again.

### Step 4. Reconnect and verify

The public DNS may change after restarting. Copy the new public DNS from the EC2 console.

Reconnect:

```bash
ssh -i ~/Downloads/launchbot-demo-key.pem ec2-user@NEW_EC2_PUBLIC_DNS
```

Check services:

```bash
sudo systemctl status ollama --no-pager
sudo systemctl status launchbot --no-pager
sudo systemctl status nginx --no-pager
```

Test:

```bash
curl -i http://127.0.0.1/api/health
curl -i http://127.0.0.1/api/rag/health
```

Open the new public URL and ask the chatbot question again.

**Evidence of success:** The same deployed app responds faster on the upgraded instance.

---

## Task 15: Optional Custom Domain Note

The long AWS public DNS is fine for this lesson. For a capstone or portfolio project, you may want a friendlier URL.

At a high level, you would:

1. Register or use a domain.
2. Create a DNS record for a subdomain.
3. Point that record to the EC2 instance.
4. Add HTTPS before calling the app production-ready.

A stable domain usually needs a stable IP address. AWS Elastic IPs can provide a stable public IPv4 address, but public IPv4 resources may create additional cost. Use this only when you understand the billing and cleanup requirements.

---

## Task 16: Clean Up Resources

### Step 1. Stop or terminate the instance

Cloud resources can cost money while they are running or while storage remains allocated. When you finish the lesson, stop or terminate the EC2 instance and check for unused storage, public IPv4 resources, and other AWS resources.

If you want to continue later, stop the instance:

```text
EC2
→ Instances
→ Select launchbot-free-tier-test
→ Instance state
→ Stop instance
```

If you are done and do not need the server again, terminate the instance:

```text
EC2
→ Instances
→ Select launchbot-free-tier-test
→ Instance state
→ Terminate instance
```

### Step 2. Check for leftovers

Check:

```text
EC2 → Volumes
EC2 → Elastic IPs
EC2 → Security Groups
Billing and Cost Management
```

**What this does:** This helps prevent avoidable cloud costs after the lesson.

**Evidence of success:** You know which resources are still running or allocated.

---

## Reflection

Use **Notice → Interpret → Respond → Align** to reflect on the deployment.

1. **Notice:** What changed between local development and the deployed AWS environment?
2. **Interpret:** Why did those changes matter for users, cost, performance, security, or reliability?
3. **Respond:** What did you do to verify the app and troubleshoot deployment issues?
4. **Align:** What would you change before using this architecture for a production or capstone application?

Feel free to keep your notes on hand to return to when deploying your next project.
