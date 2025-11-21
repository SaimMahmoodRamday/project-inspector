# Project Inspector
A full-stack application that analyzes a project folder, generates dependency graphs, and produces AI-based summaries using FastAPI (backend) and React + Vite (frontend).

## 🚀 Features
- Upload a project folder via frontend
- Parse and analyze source files
- Generate dependency graphs using NetworkX + Graphviz
- Summarize code using LangChain + Google GenAI
- Export or view structured reports
- Dockerized setup for easy deployment

## 🔑 Environment Variables
Create a .env file inside backend/:
GOOGLE_API_KEY=your_key_here
MODEL_NAME=your_model_here

## 🏗 To Run Project
- docker-compose up (from the root of repo)

