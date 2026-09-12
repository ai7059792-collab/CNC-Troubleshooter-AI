# ⚙️ CNC Troubleshooter AI

An AI-assisted CNC troubleshooting application built with **Streamlit + Groq**.

The user uploads a CNC manufacturer's manual, enters a CNC alarm/error, and the application analyzes relevant manual content through a three-stage AI workflow:

1. **Planning** — identifies the problem and creates a diagnostic plan.
2. **Diagnosis** — develops a troubleshooting procedure using the manual.
3. **Validation & Error Handling** — checks the answer for unsupported claims and unsafe instructions.

## Features

- Upload CNC PDF manuals
- Enter CNC manufacturer and machine model
- Enter alarm/error messages
- Provide additional symptoms
- Manual-grounded troubleshooting
- Three-stage AI workflow
- Safety-focused validation
- Streamlit web interface
- Groq LLM integration

## Project Structure

```text
cnc-troubleshooter-ai/
├── app.py
├── workflow_prompts.py
├── requirements.txt
└── README.md
```

## 1. Get a Groq API Key

Create an API key through the Groq developer platform.

For local testing, you can enter the key in the Streamlit sidebar.

For Streamlit deployment, use **Streamlit Secrets** instead of committing the API key to GitHub.

## 2. Run Locally

Install Python 3.10+.

```bash
pip install -r requirements.txt
```

Run:

```bash
streamlit run app.py
```

The application will open in your browser.

## 3. Streamlit Secrets

For deployment, create a secret named:

```toml
GROQ_API_KEY = "your_api_key_here"
```

Do **not** put the real API key inside `app.py` or commit it to GitHub.

## 4. Deploy from GitHub

1. Create a new GitHub repository.
2. Upload:
   - `app.py`
   - `workflow_prompts.py`
   - `requirements.txt`
   - `README.md`
3. Open Streamlit Community Cloud.
4. Connect your GitHub account.
5. Select this repository.
6. Select `app.py` as the main file.
7. Add `GROQ_API_KEY` under Streamlit Secrets.
8. Deploy.

## 5. How to Use

### Step 1 — Upload Manual

Upload the relevant CNC manufacturer's PDF manual.

Examples:

- CNC operation manual
- Maintenance manual
- Alarm manual
- Troubleshooting manual

### Step 2 — Enter Machine Information

Enter the manufacturer and CNC/machine model when known.

### Step 3 — Enter the Error

Paste the complete alarm/error message.

For example:

```text
Alarm 401 Servo Alarm
```

or:

```text
X-axis overtravel
```

### Step 4 — Add Symptoms

If available, describe what happened immediately before the alarm.

### Step 5 — Diagnose

Click:

**Diagnose CNC Problem**

The application runs the three-stage AI workflow and generates a troubleshooting report.

## Important Safety Notice

This is an AI-assisted troubleshooting tool, not a replacement for the manufacturer's official procedures or a qualified CNC technician.

Never:

- bypass safety interlocks
- defeat guards
- bypass emergency stops
- bypass limit switches
- perform hazardous electrical work without proper qualification
- rely on an AI answer when the manufacturer's documentation is unavailable or unclear

Always verify critical procedures against the original manufacturer's documentation.

## Current Version

This version uses simple PDF text extraction and keyword-based retrieval.

For larger production-grade manuals, the next upgrade should use **RAG (Retrieval-Augmented Generation)** with:

```text
PDF
 ↓
Document parsing
 ↓
Chunking
 ↓
Embeddings
 ↓
Vector database
 ↓
Relevant manual sections
 ↓
Groq AI
 ↓
Validation
 ↓
Troubleshooting report
```

This will improve accuracy for large CNC manuals and make it easier to support multiple manufacturers and machine models.
