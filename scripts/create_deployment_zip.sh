#!/usr/bin/env bash
set -euo pipefail

ZIP_NAME="launchbot-deployment-assistant.zip"
PROJECT_DIR="../launchbot-deployment-assistant"

rm -f "$ZIP_NAME"

zip -r "$ZIP_NAME" "$PROJECT_DIR" \
  -x "*/.venv/*" \
  -x "*/node_modules/*" \
  -x "*/dist/*" \
  -x "*/__pycache__/*" \
  -x "*.pyc" \
  -x "*/.env" \
  -x "*/instance/*" \
  -x "*/.DS_Store" \
  -x "*/.pytest_cache/*"

echo "Created $ZIP_NAME"