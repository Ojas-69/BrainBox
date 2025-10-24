import os
import streamlit as st
import fitz  # PyMuPDF
from huggingface_hub import InferenceClient
import re

st.set_page_config(page_title="BrainBox 2.0", page_icon="🧠", layout="centered")

# 🎨 Styling
st.markdown("""
    <style>
    body {background-color: #0d1117; color: #e6edf3; font-family: 'Trebuchet MS', sans-serif;}
    .title {font-size: 40px; font-weight: bold; color: #00ffcc; text-align: center;}
    .tagline {font-size: 18px; color: #58a6ff; text-align: center; margin-bottom: 40px;}
    .notes {background-color: #161b22; padding: 15px; border-radius: 10px; margin: 10px 0; font-size: 16px; line-height: 1.6;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🧠 BrainBox 2.0</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">AI-Powered Notes & Question Generator 🚀</div>', unsafe_allow_html=True)

# Tabs
tab1, tab2 = st.tabs(["📝 Notes Generator", "❓ Question Generator"])

# Hugging Face Inference API token (set in Streamlit secrets or environment)
HF_TOKEN = st.secrets["HF_TOKEN"] if "HF_TOKEN" in st.secrets else os.environ.get("HF_TOKEN")

@st.cache_resource
def get_hf_client():
    if not HF_TOKEN:
        return None
    return InferenceClient(token=HF_TOKEN)

# create client (allow temporary input when missing)
client = get_hf_client()
if client is None:
    token_input = st.text_input(
        "Hugging Face token (temporary)",
        type="password",
        help="Paste HF token to run model calls now. For deployments, set HF_TOKEN in Streamlit secrets or env vars."
    )
    if token_input:
        client = InferenceClient(token=token_input)

# remote model ids
SUMMARY_MODEL = "facebook/bart-large-cnn"
QUESTION_MODEL = "valhalla/t5-small-qa-qg-hl"

def call_model(model_id, prompt, max_new_tokens=256):
    if client is None:
        raise RuntimeError("No Hugging Face token configured. Set HF_TOKEN in Streamlit secrets or environment.")
    try:
        # Make the API call (new syntax)
        resp = client.text_generation(
            model=model_id,
            prompt=prompt,
            max_new_tokens=max_new_tokens
        )

        # Debug: if response is a dict or list, print it
        if isinstance(resp, dict):
            return resp.get("generated_text", str(resp))
        elif isinstance(resp, list) and len(resp) > 0:
            return resp[0].get("generated_text", "") or str(resp[0])
        else:
            return str(resp)

    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        raise RuntimeError(f"Model call failed: {e}\n\n{err_msg}")


# PDF extraction
def extract_text_fitz(pdf_file):
    text = ""
    try:
        pdf_file.seek(0)
        data = pdf_file.read()
        with fitz.open(stream=data, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
    except Exception:
        return ""
    return text

# Cleaning
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# Chunking
def chunk_text_by_sentences(text, max_sentences=3):
    sentences = re.split(r'(?<=[.!?]) +', text)
    for i in range(0, len(sentences), max_sentences):
        yield " ".join(sentences[i:i + max_sentences])

# Notes generation (remote)
def generate_notes(text):
    clean = clean_text(text)
    chunks = list(chunk_text_by_sentences(clean))
    notes = []
    for chunk in chunks:
        prompt = f"Convert this into clear, structured study notes:\n\n{chunk}"
        try:
            gen = call_model(SUMMARY_MODEL, prompt, max_new_tokens=256)
            notes.append(gen.strip())
        except Exception as e:
            notes.append(f"[Error generating notes for this chunk: {e}]")
    return "\n\n".join(n for n in notes if n)

# Question generation (remote)
def generate_questions(text, q_type):
    clean = clean_text(text)
    chunks = list(chunk_text_by_sentences(clean))
    questions = []
    for chunk in chunks:
        if q_type == "MCQs":
            prompt = f"Generate 3 multiple choice questions with answers from:\n\n{chunk}"
        elif q_type == "Short Answer":
            prompt = f"Generate 3 short-answer questions from:\n\n{chunk}"
        else:
            prompt = f"Generate 3 conceptual or analytical questions from:\n\n{chunk}"
        try:
            gen = call_model(QUESTION_MODEL, prompt, max_new_tokens=256)
            questions.append(gen.strip())
        except Exception as e:
            questions.append(f"[Error generating questions for this chunk: {e}]")
    return "\n\n".join(q for q in questions if q)

# 🧾 Notes Tab
with tab1:
    st.subheader("📄 Upload your PDF for AI Notes")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded_file:
        if st.button("✨ Generate Notes", key="generate_notes_button"):
            if client is None:
                st.error("HF_TOKEN not configured. Add it to Streamlit secrets or set HF_TOKEN env var.")
            else:
                with st.spinner("Processing PDF..."):
                    text = extract_text_fitz(uploaded_file)
                    if len(text.strip()) < 50:
                        st.error("This PDF seems empty or scanned. Try another one.")
                    else:
                        notes = generate_notes(text)
                        st.markdown('<div class="notes">' + notes.replace("\n", "<br>") + "</div>", unsafe_allow_html=True)
                        st.download_button("📥 Download Notes", notes, file_name="AI_Notes.txt")

# ❓ Questions Tab
with tab2:
    st.subheader("🎯 Generate Questions")
    user_text = st.text_area("Paste your notes or text:", height=200)
    q_type = st.selectbox("Select Question Type:", ["MCQs", "Short Answer", "Conceptual"])
    if st.button("🤖 Generate Questions", key="generate_questions_button"):
        if len(user_text.strip()) < 30:
            st.warning("Please add some text first.")
        else:
            if client is None:
                st.error("HF_TOKEN not configured. Add it to Streamlit secrets or set HF_TOKEN env var.")
            else:
                with st.spinner("AI is crafting your questions..."):
                    qs = generate_questions(user_text, q_type)
                    st.markdown('<div class="notes">' + qs.replace("\n", "<br>") + "</div>", unsafe_allow_html=True)
                    st.download_button("📘 Download Questions", qs, file_name="AI_Questions.txt")
