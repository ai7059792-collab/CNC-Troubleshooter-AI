import os
import re
import tempfile

import streamlit as st
from groq import Groq
from pypdf import PdfReader

from workflow_prompts import (
    PLANNING_PROMPT,
    DIAGNOSIS_PROMPT,
    ERROR_HANDLING_PROMPT,
)


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="CNC Troubleshooter AI",
    page_icon="⚙️",
    layout="wide",
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("⚙️ CNC Troubleshooter AI")
st.subheader("AI-assisted CNC alarm and troubleshooting system")

st.write(
    """
    Upload a CNC machine manual, enter the machine error/alarm,
    and the AI will analyze the problem using the uploaded manual.
    """
)


# ---------------------------------------------------------
# API CONFIGURATION
# ---------------------------------------------------------

api_key = st.sidebar.text_input(
    "Groq API Key",
    type="password",
    help="Enter your Groq API key."
)

if not api_key:
    st.info("Enter your Groq API key in the sidebar to continue.")
    st.stop()

client = Groq(api_key=api_key)


# ---------------------------------------------------------
# MODEL
# ---------------------------------------------------------

MODEL = "llama-3.3-70b-versatile"


# ---------------------------------------------------------
# PDF TEXT EXTRACTION
# ---------------------------------------------------------

def extract_pdf_text(uploaded_file):

    pdf_reader = PdfReader(uploaded_file)

    pages = []

    for page_number, page in enumerate(pdf_reader.pages, start=1):

        try:
            text = page.extract_text()

            if text:
                pages.append(
                    f"\n--- PAGE {page_number} ---\n{text}"
                )

        except Exception:
            continue

    return "\n".join(pages)


# ---------------------------------------------------------
# TEXT CLEANING
# ---------------------------------------------------------

def clean_text(text):

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ---------------------------------------------------------
# FIND RELEVANT MANUAL CONTENT
# ---------------------------------------------------------

def find_relevant_content(manual_text, error_message):

    error_words = re.findall(
        r"[A-Za-z0-9_-]+",
        error_message.lower()
    )

    pages = manual_text.split("--- PAGE ")

    scored_pages = []

    for page in pages:

        page_lower = page.lower()

        score = 0

        for word in error_words:

            if len(word) > 2 and word in page_lower:
                score += 1

        if score > 0:
            scored_pages.append(
                (score, page)
            )

    scored_pages.sort(
        key=lambda x: x[0],
        reverse=True
    )

    selected = scored_pages[:8]

    if not selected:
        return manual_text[:20000]

    return "\n--- PAGE ".join(
        page for _, page in selected
    )


# ---------------------------------------------------------
# GROQ CALL
# ---------------------------------------------------------

def ask_ai(system_prompt, user_prompt):

    response = client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],

        temperature=0.1,
    )

    return response.choices[0].message.content


# ---------------------------------------------------------
# MANUAL UPLOAD
# ---------------------------------------------------------

st.sidebar.header("📘 CNC Manual")

manual_file = st.sidebar.file_uploader(
    "Upload CNC Manual PDF",
    type=["pdf"]
)


if manual_file:

    with st.spinner("Reading CNC manual..."):

        manual_text = extract_pdf_text(
            manual_file
        )

    st.sidebar.success(
        f"Manual loaded: {len(manual_text):,} characters"
    )

else:

    manual_text = ""


# ---------------------------------------------------------
# MACHINE INFORMATION
# ---------------------------------------------------------

st.header("1. CNC Machine Information")

col1, col2 = st.columns(2)

with col1:

    manufacturer = st.text_input(
        "CNC Manufacturer",
        placeholder="e.g. FANUC, Siemens, Haas"
    )

with col2:

    machine_model = st.text_input(
        "Machine / CNC Model",
        placeholder="e.g. FANUC 0i-MF"
    )


# ---------------------------------------------------------
# ERROR INPUT
# ---------------------------------------------------------

st.header("2. Enter CNC Problem")

error_message = st.text_area(
    "CNC Alarm / Error Message",
    placeholder=(
        "Example:\n"
        "Alarm 401 Servo Alarm\n"
        "Axis X overtravel\n"
        "Spindle alarm\n"
        "Paste the complete alarm message here."
    ),
    height=150,
)


# ---------------------------------------------------------
# OPTIONAL ADDITIONAL INFORMATION
# ---------------------------------------------------------

additional_info = st.text_area(
    "Additional Information (optional)",
    placeholder=(
        "Describe what happened before the alarm.\n"
        "Example: Alarm appeared during rapid movement "
        "of X axis."
    ),
    height=100,
)


# ---------------------------------------------------------
# DIAGNOSE BUTTON
# ---------------------------------------------------------

if st.button(
    "🔧 Diagnose CNC Problem",
    type="primary",
    use_container_width=True,
):

    if not manual_file:

        st.error(
            "Please upload the CNC manual first."
        )

        st.stop()

    if not error_message.strip():

        st.error(
            "Please enter the CNC alarm/error."
        )

        st.stop()


    # -----------------------------------------------------
    # RELEVANT MANUAL CONTENT
    # -----------------------------------------------------

    relevant_content = find_relevant_content(
        manual_text,
        error_message
    )


    # -----------------------------------------------------
    # STAGE 1 — PLANNING
    # -----------------------------------------------------

    with st.status(
        "Stage 1: Planning diagnosis...",
        expanded=True
    ):

        planning_prompt = PLANNING_PROMPT.format(
            manufacturer=manufacturer,
            machine_model=machine_model,
            error_message=error_message,
            additional_info=additional_info,
            manual_content=relevant_content,
        )

        planning_result = ask_ai(
            PLANNING_PROMPT,
            planning_prompt
        )

        st.write(planning_result)


    # -----------------------------------------------------
    # STAGE 2 — DIAGNOSIS
    # -----------------------------------------------------

    with st.status(
        "Stage 2: Analyzing manual and developing solution...",
        expanded=True
    ):

        diagnosis_user_prompt = DIAGNOSIS_PROMPT.format(
            manufacturer=manufacturer,
            machine_model=machine_model,
            error_message=error_message,
            additional_info=additional_info,
            planning_result=planning_result,
            manual_content=relevant_content,
        )

        diagnosis_result = ask_ai(
            DIAGNOSIS_PROMPT,
            diagnosis_user_prompt
        )


    # -----------------------------------------------------
    # STAGE 3 — ERROR HANDLING / VALIDATION
    # -----------------------------------------------------

    with st.status(
        "Stage 3: Validating troubleshooting response...",
        expanded=True
    ):

        validation_prompt = ERROR_HANDLING_PROMPT.format(
            manufacturer=manufacturer,
            machine_model=machine_model,
            error_message=error_message,
            planning_result=planning_result,
            diagnosis_result=diagnosis_result,
            manual_content=relevant_content,
        )

        final_result = ask_ai(
            ERROR_HANDLING_PROMPT,
            validation_prompt
        )


    # -----------------------------------------------------
    # FINAL RESULT
    # -----------------------------------------------------

    st.divider()

    st.header("🛠️ CNC Troubleshooting Report")

    st.markdown(final_result)

    st.success(
        "Diagnosis completed using the uploaded manual."
    )

    st.warning(
        """
        ⚠️ Safety notice: This AI tool is an assistance system.
        Follow the machine manufacturer's safety procedures and
        qualified maintenance practices. Do not bypass safety
        interlocks or perform hazardous work based solely on AI output.
        """
    )
