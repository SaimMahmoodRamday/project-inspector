# 🕵️ Project Inspector

**Project Inspector** is a full-stack AI-powered tool that analyzes a zipped project folder and returns a visual function call graph, per-file code summaries, and a structured dependency report — helping developers quickly understand unfamiliar codebases.

[![Deploy to Azure](https://img.shields.io/badge/Deployed%20on-Azure%20Container%20Apps-0078D4?logo=microsoftazure)](https://project-inspector-frontend.proudfield-b0f3558f.eastus.azurecontainerapps.io)

---

## ✨ Features

- 📦 Upload any project as a `.zip` file via the web UI
- 🔗 Visual function call graph (NetworkX + Graphviz, rendered as inline SVG)
- 🤖 Per-file AI summaries with Gemini (Groq as fallback)
- 📄 Markdown analysis report rendered in the browser
- 🐳 Fully Dockerized — runs locally or on any cloud

---

## 🏗 Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, NetworkX, Graphviz, LangChain |
| Frontend | React + Vite, Tailwind CSS, Nginx |
| AI | Google Gemini (`gemini-2.5-flash-lite`), Groq (`llama-3.1-8b-instant`) |
| DevOps | Docker, Azure Container Apps, Azure Container Registry, GitHub Actions |

---

## 🖼️ Screenshot

![Interface](./assets/projectinspectorgit.jpg)

---

## 🚀 Run Locally

### 1. Set up environment variables

Copy the example file and fill in your API keys:

```bash
cp backend/.env.example backend/.env
```

```bash
# backend/.env
GOOGLE_API_KEY=your_google_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

### 2. Start with Docker Compose

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend docs: http://localhost:8000/docs

---

## 🔑 Updating API Keys

API keys are passed as environment variables — they are never baked into the Docker image.

### Locally

Edit `backend/.env` and restart:

```bash
docker-compose restart backend
```

### On Azure (production)

Use the Azure CLI to update the secret on the running Container App — no rebuild required:

```bash
az containerapp update \
  --name project-inspector-backend \
  --resource-group project-inspector-rg \
  --set-env-vars "GOOGLE_API_KEY=your_new_key" "GROQ_API_KEY=your_new_key"
```

The app restarts automatically and picks up the new values.

> To get new API keys:
> - **Gemini / Google:** https://aistudio.google.com/apikey
> - **Groq:** https://console.groq.com/keys

---

## ☁️ Azure Deployment

Deployed on **Azure Container Apps** with images hosted on **Azure Container Registry (ACR)**.

| Resource | Name |
|---|---|
| Resource Group | `project-inspector-rg` |
| Container Registry | `projectinspectoracr` |
| Backend App | `project-inspector-backend` |
| Frontend App | `project-inspector-frontend` |

**Live URLs:**
- Frontend: https://project-inspector-frontend.proudfield-b0f3558f.eastus.azurecontainerapps.io
- Backend: https://project-inspector-backend.proudfield-b0f3558f.eastus.azurecontainerapps.io

### Manual deployment

```bash
# 1. Authenticate
az login
az acr login --name projectinspectoracr

# 2. Build & push backend
docker build -t projectinspectoracr.azurecr.io/project-inspector-backend:latest ./backend
docker push projectinspectoracr.azurecr.io/project-inspector-backend:latest
az containerapp update \
  --name project-inspector-backend \
  --resource-group project-inspector-rg \
  --image projectinspectoracr.azurecr.io/project-inspector-backend:latest

# 3. Build & push frontend
docker build -t projectinspectoracr.azurecr.io/project-inspector-frontend:latest ./frontend
docker push projectinspectoracr.azurecr.io/project-inspector-frontend:latest
az containerapp update \
  --name project-inspector-frontend \
  --resource-group project-inspector-rg \
  --image projectinspectoracr.azurecr.io/project-inspector-frontend:latest
```

### Verify deployment

```bash
# Stream live logs
az containerapp logs show \
  --name project-inspector-backend \
  --resource-group project-inspector-rg \
  --follow

# Check running revision
az containerapp show \
  --name project-inspector-backend \
  --resource-group project-inspector-rg \
  --query properties.latestRevisionName
```

---

## ⚙️ CI/CD — GitHub Actions

Every push to `main` automatically builds and deploys both services via `.github/workflows/deploy.yml`.

### Required GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Value |
|---|---|
| `AZURE_CREDENTIALS` | Service principal JSON (see below) |
| `ACR_LOGIN_SERVER` | `projectinspectoracr.azurecr.io` |
| `ACR_USERNAME` | ACR admin username (Portal → ACR → Access keys) |
| `ACR_PASSWORD` | ACR admin password (Portal → ACR → Access keys) |

### Create the service principal (one-time setup)

```bash
# Get your subscription ID
az account show --query id -o tsv

az ad sp create-for-rbac \
  --name project-inspector-sp \
  --role contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/project-inspector-rg \
  --sdk-auth
```

Paste the full JSON output as the `AZURE_CREDENTIALS` secret.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
