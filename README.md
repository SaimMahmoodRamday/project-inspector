# 🕵️ Project Inspector

**Project Inspector** is a full-stack, cloud-native AI developer tool. Upload any codebase as a `.zip` and get back a full static analysis — a visual cross-file function call graph, per-file AI-generated summaries, and a structured dependency report — all rendered instantly in the browser.

<!-- Built to run at scale on Azure Container Apps with zero-downtime CI/CD via GitHub Actions. -->

<!-- [![Live Demo](https://img.shields.io/badge/Live%20Demo-Azure%20Container%20Apps-0078D4?logo=microsoftazure)](https://project-inspector-frontend.proudfield-b0f3558f.eastus.azurecontainerapps.io) -->

---

## ✨ Features

- **Cross-file call graph** — statically parses Python AST to extract function definitions, call sites, and cross-module dependencies, then renders an interactive SVG graph using NetworkX and Graphviz
- **AI code summaries** — sends each file through Google Gemini (`gemini-2.5-flash-lite`) with automatic fallback to Groq (`llama-3.1-8b-instant`) if the primary model is unavailable
- **Structured analysis report** — generates a Markdown report with function inventory, import graph, and dependency highlights, rendered live in the browser
- **Resilient by design** — dual-LLM fallback, per-file error isolation (one broken file never aborts the full analysis), and a response cache to avoid redundant LLM calls
- **Stateless & cloud-native** — SVGs are embedded as base64 data URIs in the API response, so the app works correctly across any number of replicas with no shared storage
- **Production-deployed** — containerized with Docker, hosted on Azure Container Apps, with CI/CD via GitHub Actions on every push to `main`

---

## 🏗️ Architecture & Tech Stack

### Backend

| Component | Technology | Role |
|---|---|---|
| API Framework | **FastAPI** | Async REST API, automatic OpenAPI docs at `/docs` |
| Static Analysis | **Python AST + NetworkX** | Parses source files, builds directed call graph |
| Graph Rendering | **Graphviz (fdp engine)** | Force-directed SVG layout, returned as inline data URI |
| AI Summarization | **LangChain + Google Gemini** | Per-file code summaries, 50-word max, structured output |
| LLM Fallback | **Groq (LLaMA 3.1 8B)** | Automatic failover if Gemini rate-limits or errors |
| Response Cache | **MD5-keyed JSON file** | Avoids re-summarizing unchanged files across uploads |

### Frontend

| Component | Technology | Role |
|---|---|---|
| Framework | **React 18 + Vite** | SPA with fast HMR in dev, optimized production bundle |
| Styling | **Tailwind CSS** | Utility-first responsive layout |
| HTTP Client | **Fetch API** | Streams ZIP upload with loading state and error handling |
| Server | **Nginx (Alpine)** | Serves static assets, reverse-proxies `/upload` to backend |

### Infrastructure

| Component | Technology | Role |
|---|---|---|
| Containerization | **Docker** (multi-stage builds) | Separate optimized images for backend and frontend |
| Container Registry | **Azure Container Registry** | Private image hosting with versioned SHA tags |
| Hosting | **Azure Container Apps** | Serverless containers, scale-to-zero on Consumption plan |
| CI/CD | **GitHub Actions** | Auto-build and deploy on push to `main` |

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

<!-- **Live URLs:**
- Frontend: https://project-inspector-frontend.proudfield-b0f3558f.eastus.azurecontainerapps.io
- Backend: https://project-inspector-backend.proudfield-b0f3558f.eastus.azurecontainerapps.io -->

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

---
