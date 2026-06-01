#!/usr/bin/env bash
#
# Provision a fresh Debian/Ubuntu GCP VM to run Sage.
#
# Run ONCE, from the repo root, right after `git clone`:
#
#     bash deploy/setup_vm.sh
#
# It installs Ollama, pulls the models, creates a Python venv with the
# project deps, and installs a systemd service so the app starts on boot.
# It does NOT start the app yet — you still need to copy your PDFs up and
# build the vector store (see deploy/ingest.sh and DEPLOY.md).
#
set -euo pipefail

GEN_MODEL="${SAGE_GEN_MODEL:-qwen3:8b}"
EMBED_MODEL="${SAGE_EMBED_MODEL:-nomic-embed-text}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_USER="$(whoami)"

echo "==> Installing system packages"
sudo apt-get update -y
sudo apt-get install -y python3 python3-venv python3-pip curl git

echo "==> Installing Ollama"
if ! command -v ollama >/dev/null 2>&1; then
  curl -fsSL https://ollama.com/install.sh | sh
fi

echo "==> Pulling models (slow — ~5.5GB for ${GEN_MODEL})"
ollama pull "$GEN_MODEL"
ollama pull "$EMBED_MODEL"

echo "==> Creating Python venv + installing deps"
cd "$REPO_DIR"
python3 -m venv .venv
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

echo "==> Installing systemd service (sage.service)"
sudo tee /etc/systemd/system/sage.service >/dev/null <<EOF
[Unit]
Description=Sage RAG (Streamlit)
After=network-online.target ollama.service
Wants=network-online.target

[Service]
User=${RUN_USER}
WorkingDirectory=${REPO_DIR}
Environment=SAGE_GEN_MODEL=${GEN_MODEL}
Environment=SAGE_EMBED_MODEL=${EMBED_MODEL}
ExecStart=${REPO_DIR}/.venv/bin/streamlit run app.py \
  --server.address 0.0.0.0 --server.port 8501 \
  --server.headless true \
  --server.enableCORS false --server.enableXsrfProtection false
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload

cat <<'DONE'

==========================================================
 Setup complete.

 Next steps (see DEPLOY.md for the copy-paste commands):
   1. From your laptop, scp your PDFs into data/<author>/ on this VM.
   2. On this VM, build the vector store:   bash deploy/ingest.sh
   3. Start the app:                        sudo systemctl enable --now sage
   4. Share:  http://<THIS_VM_EXTERNAL_IP>:8501
==========================================================
DONE
