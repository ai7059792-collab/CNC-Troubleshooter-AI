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

## Important PDF fix

This version includes the PDF cryptography dependencies:

```text
pypdf[crypto]
cryptography
```

This is important because some CNC manufacturer manuals are protected/encrypted.
The application also handles password-protected PDFs and shows a clear message
instead of crashing.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Groq API key

For Streamlit Cloud, add:

```toml
GROQ_API_KEY = "your_groq_api_key"
```

Do not commit the real API key to GitHub.

## Streamlit deployment

1. Replace the old files in GitHub with the files from this package.
2. Confirm all four files are in the repository root.
3. Open Streamlit Community Cloud.
4. Select the repository.
5. Select `app.py`.
6. Add `GROQ_API_KEY` under Secrets.
7. Redeploy.

## PDF troubleshooting

If the manual is password-protected:

1. Upload the PDF.
2. Enter its PDF password in the sidebar.
3. Click Diagnose.

If the PDF is scanned/image-only, normal text extraction may not work.
OCR will be added in the next version.

## Workflow

```text
CNC Error
   ↓
Manual PDF
   ↓
PDF extraction
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

This is an AI-assisted technical tool. Always verify critical procedures against
the original manufacturer documentation and use qualified CNC maintenance personnel.

Never bypass guards, emergency stops, interlocks, limit switches, or other safety systems.
