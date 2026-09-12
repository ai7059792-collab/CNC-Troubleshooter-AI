import os
import re
import streamlit as st
from groq import Groq
from pypdf import PdfReader

from workflow_prompts import (
    PLANNING_PROMPT,
    DIAGNOSIS_PROMPT,
    ERROR_HANDLING_PROMPT,
)

st.set_page_config(
    page_title="CNC Troubleshooter AI",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ CNC Troubleshooter AI")
st.caption("Manual-grounded AI assistance for CNC alarm and troubleshooting analysis.")

# -----------------------------
# Configuration
# -----------------------------
MODEL = "llama-3.3-70b-versatile"

api_key = st.sidebar.text_input(
    "Groq API Key",
    type="password",
    help="For deployment, use Streamlit Secrets instead of entering it manually.",
)

# Prefer Streamlit Secrets when available.
if not api_key:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

if not api_key:
    st.info("Add your Groq API key in the sidebar, or configure GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)


# -----------------------------
# PDF extraction
# -----------------------------
@st.cache_data(show_spinner=False)
def extract_pdf_text(pdf_bytes):
    import io

    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""

        if text.strip():
            pages.append(f"--- PAGE {page_number} ---\n{text}")

    return "\n\n".join(pages)


def find_relevant_content(manual_text, error_message, max_pages=10):
    """Simple prototype retrieval based on keyword overlap."""
    if not manual_text:
        return ""

    error_words = set(
        word.lower()
        for word in re.findall(r"[A-Za-z0-9_-]+", error_message)
        if len(word) > 2
    )

    pages = re.split(r"(?=--- PAGE \d+ ---)", manual_text)
    scored = []

    for page in pages:
        page_lower = page.lower()
        score = sum(1 for word in error_words if word in page_lower)

        # Give a small preference to pages containing alarm/error terminology.
        if "alarm" in page_lower:
            score += 1
        if "troubleshoot" in page_lower:
            score += 1

        if score > 0:
            scored.append((score, page))

    scored.sort(key=lambda item: item[0], reverse=True)

    selected = [page for _, page in scored[:max_pages]]

    if selected:
        return "\n\n".join(selected)

    # Fallback for a prototype when no keywords match.
    return manual_text[:30000]


def ask_ai(system_prompt, user_prompt):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("📘 CNC Manual")

manual_file = st.sidebar.file_uploader(
    "Upload CNC manual",
    type=["pdf"],
    help="Upload the manufacturer's CNC operation, maintenance, alarm, or troubleshooting manual.",
)

if manual_file:
    with st.spinner("Reading CNC manual..."):
        manual_text = extract_pdf_text(manual_file.getvalue())

    if manual_text.strip():
        st.sidebar.success(f"Manual loaded: {len(manual_text):,} characters")
    else:
        st.sidebar.error("No readable text was found in this PDF. A scanned PDF may need OCR.")
else:
    manual_text = ""


# -----------------------------
# Machine information
# -----------------------------
st.header("1. CNC Machine Information")

col1, col2 = st.columns(2)

with col1:
    manufacturer = st.text_input(
        "CNC Manufacturer",
        placeholder="e.g. FANUC, Siemens, Haas, Mitsubishi",
    )

with col2:
    machine_model = st.text_input(
        "Machine / CNC Model",
        placeholder="e.g. FANUC 0i-MF",
    )


# -----------------------------
# Problem
# -----------------------------
st.header("2. CNC Problem")

error_message = st.text_area(
    "Alarm / Error Message",
    placeholder=(
        "Enter the complete CNC alarm or error message.\n\n"
        "Example: Alarm 401 Servo Alarm\n"
        "Example: X-axis overtravel"
    ),
    height=150,
)

additional_info = st.text_area(
    "Additional Symptoms / Context (optional)",
    placeholder=(
        "What was the machine doing when the alarm occurred?\n"
        "Example: The alarm appeared while the X axis was moving rapidly."
    ),
    height=110,
)


# -----------------------------
# Diagnosis
# -----------------------------
if st.button("🔧 Diagnose CNC Problem", type="primary", use_container_width=True):

    if not manual_file:
        st.error("Please upload the relevant CNC manual first.")
        st.stop()

    if not manual_text.strip():
        st.error("The uploaded PDF does not contain readable text.")
        st.stop()

    if not error_message.strip():
        st.error("Please enter the CNC alarm/error message.")
        st.stop()

    relevant_content = find_relevant_content(
        manual_text,
        error_message,
    )

    # Stage 1
    with st.status("Stage 1 — Planning diagnosis...", expanded=False):
        planning_user_prompt = f"""
CNC manufacturer:
{manufacturer or "Not provided"}

CNC machine/model:
{machine_model or "Not provided"}

Reported alarm/error:
{error_message}

Additional information:
{additional_info or "Not provided"}

Relevant manual content:
{relevant_content}
"""
        planning_result = ask_ai(
            PLANNING_PROMPT,
            planning_user_prompt,
        )

    # Stage 2
    with st.status("Stage 2 — Diagnosing and developing solution...", expanded=False):
        diagnosis_user_prompt = f"""
CNC manufacturer:
{manufacturer or "Not provided"}

CNC machine/model:
{machine_model or "Not provided"}

Reported alarm/error:
{error_message}

Additional information:
{additional_info or "Not provided"}

Planning result:
{planning_result}

Relevant manual content:
{relevant_content}
"""
        diagnosis_result = ask_ai(
            DIAGNOSIS_PROMPT,
            diagnosis_user_prompt,
        )

    # Stage 3
    with st.status("Stage 3 — Validating result and safety...", expanded=False):
        validation_user_prompt = f"""
CNC manufacturer:
{manufacturer or "Not provided"}

CNC machine/model:
{machine_model or "Not provided"}

Reported alarm/error:
{error_message}

Planning result:
{planning_result}

Proposed diagnosis:
{diagnosis_result}

Relevant manual content:
{relevant_content}
"""
        final_result = ask_ai(
            ERROR_HANDLING_PROMPT,
            validation_user_prompt,
        )

    st.divider()
    st.header("🛠️ CNC Troubleshooting Report")
    st.markdown(final_result)

    with st.expander("🔎 Manual evidence used"):
        st.text(relevant_content)

    st.warning(
        "Safety: This tool provides AI-assisted technical guidance. "
        "Follow the manufacturer's procedures and qualified maintenance practices. "
        "Never bypass guards, emergency stops, interlocks, limit switches, or other safety systems."
    )
