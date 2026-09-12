# CNC Troubleshooter AI

AI-assisted CNC alarm troubleshooting using Streamlit, Groq, and uploaded CNC manuals.

## Files

```text
cnc-troubleshooter-ai/
├── app.py
├── workflow_prompts.py
├── requirements.txt
└── README.md
```

## Important

`app.py` imports `workflow_prompts.py`. Both files MUST be in the same GitHub repository.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Groq API key

For Streamlit Cloud, add this secret:

```toml
GROQ_API_KEY = "your_groq_api_key"
```

Do not commit your real API key to GitHub.

## Streamlit deployment

1. Push all four files to GitHub.
2. Open Streamlit Community Cloud.
3. Select the GitHub repository.
4. Select `app.py` as the main file.
5. Add `GROQ_API_KEY` in Secrets.
6. Deploy.

## Workflow

```text
CNC Error
   ↓
Manual PDF
   ↓
Planning
   ↓
Diagnosis
   ↓
Validation / Error Handling
   ↓
Troubleshooting Report
```

## Safety

This application is an AI-assisted technical tool. Always verify critical
procedures against the original manufacturer documentation and use qualified
CNC maintenance personnel. Never bypass safety guards, emergency stops,
interlocks, or limit switches.
