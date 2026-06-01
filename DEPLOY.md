# Deploying Sage to a GCP VM

This runs the full app — Ollama (your own LLM), Chroma, and the Streamlit
UI — on a single Google Cloud VM, giving you a shareable link your friends
and family can open in a browser.

**The honest trade-offs**

- **Not free.** Your 8B model needs real RAM, which the GCP free tier can't
  provide. A CPU VM (`e2-standard-4`, 16 GB) is the cheap option — answers
  take ~30–90s each on CPU, but that's fine for occasional family use.
- **Stop the VM when you're not sharing.** You're billed while it runs.
  `gcloud compute instances stop sage` halts the charges; start it again
  when you want the link live. The app auto-starts on boot via systemd.
- **No book text is in this repo.** The PDFs and the vector store stay out
  of git. You copy the PDFs to the VM once and build the vectors there.

Everything below assumes the repo name is **Sage** and the VM is named
**sage** — adjust if you use different names. Replace the zone if you like.

---

## 1. Create the VM

```bash
gcloud compute instances create sage \
  --zone=us-central1-a \
  --machine-type=e2-standard-4 \
  --image-family=debian-12 --image-project=debian-cloud \
  --boot-disk-size=30GB \
  --tags=sage-http
```

## 2. Open the firewall for the app's port (8501)

```bash
gcloud compute firewall-rules create allow-sage-8501 \
  --allow=tcp:8501 \
  --target-tags=sage-http \
  --source-ranges=0.0.0.0/0
```

> `0.0.0.0/0` makes it reachable by anyone with the link. To lock it down to
> specific people, replace it with their IPs (comma-separated).

## 3. SSH in and clone the repo

```bash
gcloud compute ssh sage --zone=us-central1-a
```

Then, on the VM:

```bash
git clone https://github.com/JoshuaP10/Sage.git
cd Sage
bash deploy/setup_vm.sh      # installs Ollama, pulls models, sets up the service
```

`setup_vm.sh` is the slow step — it downloads ~5.5 GB of model weights.

## 4. Copy your PDFs up (run on your laptop, in a second terminal)

The source books are gitignored, so they aren't on the VM yet. Send them:

```bash
gcloud compute scp --recurse \
  data/warren_buffett data/ray_dalio data/sam_walton \
  sage:~/Sage/data/ \
  --zone=us-central1-a
```

## 5. Build the vector store (back on the VM)

```bash
cd ~/Sage
bash deploy/ingest.sh        # embeds the books with nomic-embed-text via Ollama
```

## 6. Start the app

```bash
sudo systemctl enable --now sage
sudo systemctl status sage   # confirm it's "active (running)"
```

## 7. Get your link

```bash
gcloud compute instances describe sage \
  --zone=us-central1-a \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

Share **`http://<that-IP>:8501`**. Done.

---

## Day-to-day

| Goal | Command |
|------|---------|
| Stop billing (pause the link) | `gcloud compute instances stop sage --zone=us-central1-a` |
| Bring the link back | `gcloud compute instances start sage --zone=us-central1-a` (app auto-starts) |
| View app logs | `sudo journalctl -u sage -f` |
| Restart after a code change | `git pull && sudo systemctl restart sage` |
| Re-ingest after adding books | `bash deploy/ingest.sh && sudo systemctl restart sage` |

> The external IP can change when you stop/start the VM. To keep a fixed
> address, reserve a static IP in the GCP console and attach it to `sage`.

## Optional: a real domain + HTTPS

The steps above serve plain `http://IP:8501`. For a nicer, encrypted
`https://sage.yourdomain.com`, point a domain at the VM's static IP and put
[Caddy](https://caddyserver.com) in front of port 8501 — it gets a TLS
certificate automatically. Ask and I can add that config.
