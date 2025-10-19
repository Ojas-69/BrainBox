import streamlit as st
import fitz  # PyMuPDF
from transformers import pipeline
import re

# 🎨 Styling
st.markdown("""
    <style>
    body {
        background-color: #0d1117;
        color: #e6edf3;
        font-family: 'Trebuchet MS', sans-serif;
    }
    .title {
        font-size: 36px;
        font-weight: bold;
        color: #00ffcc;
        text-align: center;
    }
    .tagline {
        font-size: 18px;
        color: #58a6ff;
        text-align: center;
        margin-bottom: 30px;
    }
    .notes {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        font-size: 16px;
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

# 🚀 Title
st.markdown('<div class="title">🧠 BrainBox</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">From Notes to Questions — Powered by AI & ML ⚙️</div>', unsafe_allow_html=True)

# 🧩 Tabs
tab1, tab2 = st.tabs(["📝 Notes Generator", "❓ Question Generator"])

# 🧠 Load models
@st.cache_resource
def load_summary_model():
    return pipeline("text2text-generation", model="google/flan-t5-large")

@st.cache_resource
def load_question_model():
    return pipeline("text2text-generation", model="valhalla/t5-small-qg-hl")

summarizer = load_summary_model()
question_maker = load_question_model()

# 📖 Extract text using PyMuPDF
def extract_text_fitz(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text("text") + "\n"
    return text

# 🧹 Clean text
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = text.replace("•", "-")
    return text.strip()

# ✂️ Split into chunks
def chunk_text_by_sentences(text, max_sentences=5):
    sentences = re.split(r'(?<=[.!?]) +', text)
    for i in range(0, len(sentences), max_sentences):
        yield " ".join(sentences[i:i + max_sentences])

# 📝 Generate Notes
def generate_notes(text):
    clean = clean_text(text)
    chunks = chunk_text_by_sentences(clean)
    notes = []
    for chunk in chunks:
        prompt = f"Convert this text into clear, bullet-point study notes:\n\n{chunk}"
        summary = summarizer(prompt, max_length=300, min_length=80, do_sample=False)
        notes.append(summary[0]['generated_text'])
    return "\n\n".join(notes)

# 🎯 Generate Questions
def generate_questions(text, q_type):
    if q_type == "MCQs":
        prompt = f"Generate 10 multiple-choice questions with options and answers from this content:\n\n{text}"
    elif q_type == "Short Answer":
        prompt = f"Generate 10 short-answer type questions based on this material:\n\n{text}"
    else:
        prompt = f"Generate 10 conceptual or analytical questions based on this study content:\n\n{text}"

    result = question_maker(prompt, max_length=512, do_sample=False)
    return result[0]['generated_text']


# ---------------- TAB 1: Notes Generator ---------------- #
with tab1:
    st.subheader("📄 Upload your PDF for AI Notes")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"], key="notes")

    if uploaded_file:
        st.success("✅ PDF uploaded successfully!")
        if st.button("✨ Generate Notes"):
            with st.spinner("🧠 BrainBox is analyzing your document..."):
                raw_text = extract_text_fitz(uploaded_file)
                if len(raw_text.strip()) < 100:
                    st.error("😕 Couldn't read enough text from this PDF. Try another one or check if it's scanned.")
                else:
                    notes = generate_notes(raw_text)
                    st.markdown('<div class="notes">' + notes.replace("\n", "<br>") + "</div>", unsafe_allow_html=True)
                    st.download_button("📥 Download Notes", notes, file_name="AI_Notes.txt")

# ---------------- TAB 2: Question Generator ---------------- #
with tab2:
    st.subheader("🎯 Generate Questions using AI")
    input_text = st.text_area("Paste your notes or text here:", height=200)
    q_type = st.selectbox("Select Question Type:", ["MCQs", "Short Answer", "Conceptual / Analytical"])

    if st.button("🤖 Generate Questions"):
        if len(input_text.strip()) < 50:
            st.warning("⚠️ Please enter some text or paste your notes first.")
        else:
            with st.spinner("Generating smart questions... 🧩"):
                questions = generate_questions(input_text, q_type)
                st.markdown("### 🧩 AI-Generated Questions")
                st.markdown('<div class="notes">' + questions.replace("\n", "<br>") + "</div>", unsafe_allow_html=True)
                st.download_button("📘 Download Questions", questions, file_name="AI_Questions.txt")
