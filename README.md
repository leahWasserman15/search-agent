# Search Agent

Multi-agent research app that plans web searches, summarizes findings, and writes a logistics disruption report for a warehouse at **440 9th Ave, New York**.

## Stack

- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) — planner, search, and writer agents
- Gradio — web UI with live progress and report download

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
cp .env.example .env          # then add your OPENAI_API_KEY
```

## Run

```bash
python app.py
```

Open the local URL Gradio prints (usually `http://127.0.0.1:7860`), click **Run Logistics Agent**, and wait for the report.

## Project layout

| File | Role |
|------|------|
| `app.py` | Gradio app entry point |
| `planner_agent.py` | Plans search queries |
| `search_agent.py` | Runs web searches |
| `writer_agent.py` | Writes the markdown report |
| `research_manager.py` | Orchestrates the full pipeline |
| `styles.py` | UI theme |
| `testing_agents.ipynb` | Step-by-step agent experimentation |
| `prod tester.ipynb` | Notebook version of the full Gradio app |
