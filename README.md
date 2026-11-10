# PPT Validator AI
## AI-Powered Presentation Evaluation, Quality Assurance & Feedback Platform

PPT Validator AI evaluates, validates, scores, and provides actionable feedback on PowerPoint (.pptx, .ppt) and PDF presentations used for:
1. **Smart India Hackathon (SIH)** Grand Finale project presentations.
2. **College Mini-Project & Major-Project** presentations and seminars.
3. **Internal & External Project Reviews** (Milestone & sprint reviews).
4. **Subject Presentations & Academic Seminars**.
5. **Research Presentations & Symposiums**.
6. **Custom User-Defined Rubrics**.

---

## Key Features

- **Multi-Stage Processing Pipeline**:
  - Stage 1: File validation & security verification (.pptx, .ppt, .pdf up to 50MB)
  - Stage 2: Content extraction (slide titles, text frames, bullet points, tables, speaker notes, shapes, hyperlinks)
  - Stage 3: Slide preview rendering (PyMuPDF high-DPI + Pillow canvas generator)
  - Stage 4: Structural flow & mandatory section verification
  - Stage 5: Technical depth, architecture, and credibility evaluation
  - Stage 6: Visual design, readability, text density, and contrast analysis
  - Stage 7: Explainable scoring & report generation
- **Explainable Weighted Scoring**:
  - Overall score out of 100 with rating system (90–100: Excellent, 80–89: Very Good, 70–79: Good, 60–69: Needs Improvement, 40–59: Weak, Below 40: Critical Improvements Required)
  - Dimension breakdown with weightages, evidence quotes, and improvement recommendations
- **Slide-by-Slide Inspector**:
  - Direct slide navigation with thumbnails
  - Content score, Technical score, Visual score
  - Severity classification (Critical, High, Medium, Low)
  - Suggested professional rewrite with one-click copy
- **SIH Jury Defense Simulator**:
  - 5 Evaluator Personas: Technical Expert, Innovation Evaluator, Problem Domain Expert, Implementation Feasibility Evaluator, Project Impact Evaluator
  - Tough questions citing relevant slide numbers, juror rationale, and suggested defense
  - Interactive defense test tool: evaluate student responses and generate juror counter-questions
- **AI Improvement Assistant**:
  - Interactive Q&A with full presentation deck context
  - Automatic slide citation badges (e.g. `Slide 3`, `Slide 5`) linking directly to slide previews
  - Preloaded recommended prompt pills
- **Custom Rubric Builder**:
  - Create, customize, and save evaluation criteria with normalized weightages (summing to 100%) and mandatory section tags
- **Formal Audit Reports**:
  - Downloadable official PDF report (generated with ReportLab)
  - Downloadable JSON report for pipeline automation

---

## Project Architecture

```
D:\AI-PPT-VALIDATOR\
├── backend/
│   ├── main.py                  # FastAPI server entry point, static files, CORS
│   ├── core/
│   │   ├── config.py            # Environment configurations & paths
│   │   └── database.py          # SQLite persistence
│   ├── schemas/                 # Pydantic data models
│   ├── processors/
│   │   ├── file_validator.py    # Type & size validation
│   │   ├── pptx_extractor.py    # python-pptx extraction
│   │   ├── pdf_extractor.py     # PyMuPDF extraction
│   │   ├── slide_renderer.py    # High-res slide rendering
│   │   └── visual_analyzer.py   # Word density & visual metrics
│   ├── rubrics/
│   │   └── definitions.py       # SIH, Academic, Review, Subject, Research rubrics
│   ├── ai/
│   │   ├── provider.py          # Unified Gemini, OpenAI, & Heuristic AI Client
│   │   └── evaluator.py         # Multi-stage evaluation & scoring engine
│   ├── reports/
│   │   └── generator.py         # ReportLab PDF & JSON report generator
│   └── api/
│       ├── routes.py            # Aggregated API router
│       └── endpoints/           # Upload, evaluate, slides, jury, assistant, rubrics, reports, analytics
└── frontend/
    ├── src/
    │   ├── api/                 # API client
    │   ├── types/               # TypeScript interfaces
    │   ├── components/          # Sidebar, ScoreBadge, StageTracker
    │   ├── views/               # Dashboard, Upload, Scorecard, SlideInspector, JurySimulator, Assistant, Rubrics, Reports, Settings
    │   ├── App.tsx              # Main application shell
    │   └── main.tsx
```

---

## Setup & Running the Application

### 1. Backend Server

```bash
# From project root
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation is available at: `http://127.0.0.1:8000/docs`

### 2. Frontend Development Server

```bash
# In another terminal
cd frontend
npm run dev
```
Open your browser at: `http://localhost:5173`

---

## Environment Variables (Optional)

You can set these in your environment or via the in-app **Platform Settings** page:
- `GEMINI_API_KEY`: Google Gemini API Key (e.g. `AIza...`) for multimodal and semantic evaluation
- `OPENAI_API_KEY`: OpenAI API Key (e.g. `sk-...`)
- `DEFAULT_AI_PROVIDER`: `gemini` | `openai` | `heuristic` (defaults to `gemini` if configured, or built-in analytical heuristics when offline).

