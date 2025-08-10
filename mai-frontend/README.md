# AI-Assisted Technical Requirement Generator

![Demo](demo.gif)

A web app that generates **professional technical requirements** for engineering and software projects using AI.  
Simply enter project details, choose tone and detail level, and export results as **PDF, DOCX, or Markdown**.

---

## 🚀 Features
- AI-powered **requirement generation**.
- **Customizable inputs**: project name, type, description, tone, detail.
- **Instant export** to PDF, DOCX, Markdown.
- Clean, **responsive Bootstrap UI**.
- Categorized outputs (Functional, Performance, Compliance, etc.).

---

## 🛠 Tech Stack
**Frontend:** React + TypeScript + Bootstrap  
**Backend:** Python (FastAPI)  
**Exports:** ReportLab, python-docx, Markdown  
**Build Tools:** Vite, Uvicorn  

---

## 📂 Workflow
1. User fills in **project details**.
2. Frontend sends request to backend AI generator.
3. AI processes and returns categorized requirements.
4. User previews results and **exports** in chosen format.

---

## ▶️ How to Run
```bash
# Backend
cd mai-backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd ../mai-frontend
npm install
npm run dev
