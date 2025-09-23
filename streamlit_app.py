import streamlit as st
from transformers import pipeline
from PyPDF2 import PdfReader

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
st.markdown('<div class="tagline">Turn boring PDFs into clean study notes ✨</div>', unsafe_allow_html=True)

# 📂 Upload PDF
uploaded_file = st.file_uploader("📄 Upload your PDF", type=["pdf"])

# 🧠 Load HuggingFace summarizer
@st.cache_resource
def load_model():
    return pipeline("summarization", model="google/flan-t5-base")

summarizer = load_model()

# 📑 Extract text
def extract_text(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# ✨ Chunking function
def chunk_text(text, max_chunk=700):
    words = text.split()
    for i in range(0, len(words), max_chunk):
        yield " ".join(words[i:i+max_chunk])

# 📝 Formatter for clean notes
def format_notes(raw_text: str) -> str:
    lines = [line.strip("-• ").strip() for line in raw_text.splitlines() if line.strip()]
    notes = []
    current_section = None

    for line in lines:
        # If it's a "Summary:" line → make it a heading
        if line.lower().startswith("summary:") or line.lower().startswith("summary"):
            current_section = line.replace("summary:", "").strip().title()
            notes.append(f"\n### {current_section}\n")
        else:
            notes.append(f"- {line}")
    return "\n".join(notes)

# 📝 Notes Generator
def generate_notes(text):
    chunks = chunk_text(text)
    notes = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=120, min_length=40, do_sample=False)[0]['summary_text']
        notes.append(summary)
    return "\n\n".join(notes)

# 🔥 Main logic
if uploaded_file:
    st.success("✅ PDF uploaded! Click below to generate notes.")
    if st.button("✨ Generate Notes"):
        with st.spinner("BrainBox is thinking... 🧠"):
            raw_text = extract_text(uploaded_file)
            notes = generate_notes(raw_text)
            clean_notes = format_notes(notes)
        st.markdown('<div class="notes">' + clean_notes.replace("\n", "<br>") + "</div>", unsafe_allow_html=True)
