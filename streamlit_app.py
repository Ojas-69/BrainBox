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
st.markdown('<div class="tagline">Smarter AI Notes Generator — Reads Every Page. Writes Real Notes. 🚀</div>', unsafe_allow_html=True)

# 📂 Upload PDF
uploaded_file = st.file_uploader("📄 Upload your PDF", type=["pdf"])

# 🧠 Load HuggingFace summarizer
@st.cache_resource
def load_model():
    return pipeline("text2text-generation", model="google/flan-t5-large")

note_maker = load_model()

# 📖 Extract text using PyMuPDF (fitz)
def extract_text_fitz(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text("text") + "\n"
    return text

# 🧹 Clean text
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  # remove excessive whitespace
    text = text.replace("•", "-")      # unify bullet points
    return text.strip()

# ✂️ Split into readable chunks (by sentence count)
def chunk_text_by_sentences(text, max_sentences=5):
    sentences = re.split(r'(?<=[.!?]) +', text)
    for i in range(0, len(sentences), max_sentences):
        yield " ".join(sentences[i:i + max_sentences])

# 📝 Generate study notes
def generate_notes(text):
    clean = clean_text(text)
    chunks = chunk_text_by_sentences(clean)
    notes = []
    for chunk in chunks:
        prompt = f"Convert this text into clear, bullet-point study notes:\n\n{chunk}"
        summary = note_maker(prompt, max_length=300, min_length=80, do_sample=False)
        notes.append(summary[0]['generated_text'])
    return "\n\n".join(notes)

# 🔥 Main logic
if uploaded_file:
    st.success("✅ PDF uploaded successfully!")
    if st.button("✨ Generate Notes"):
        with st.spinner("🧠 BrainBox is processing your document..."):
            raw_text = extract_text_fitz(uploaded_file)
            if len(raw_text.strip()) < 100:
                st.error("😕 Couldn't read enough text from this PDF. Try another one or check if it's scanned.")
            else:
                notes = generate_notes(raw_text)
                st.markdown('<div class="notes">' + notes.replace("\n", "<br>") + "</div>", unsafe_allow_html=True)
                st.download_button("📥 Download Notes", notes, file_name="AI_Notes.txt")
