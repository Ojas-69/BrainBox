import streamlit as st
import PyPDF2
from transformers import pipeline
from pathlib import Path

# Load custom CSS
css_path = Path("assets/style.css")
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# Cache summarizer
@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="facebook/bart-large-cnn")

summarizer = load_summarizer()

# Hero section
st.markdown("<h1>BrainBox</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>Smart notes from your PDFs — quick, clean & distraction-free.</p>", unsafe_allow_html=True)

# Upload box
st.markdown("<h2 class='section-title'>Upload Your PDF</h2>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])

if uploaded_file:
    st.markdown("<h2 class='section-title'>Your Notes</h2>", unsafe_allow_html=True)
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        summary = summarizer(text, max_length=200, min_length=50, do_sample=False)[0]["summary_text"]
        st.markdown(f"<div class='notes-area'><p>{summary}</p></div>", unsafe_allow_html=True)

        st.download_button("Download Notes", summary, file_name="BrainBox_Notes.txt")

    except Exception as e:
        st.error("Couldn’t process this file. Try another one 🙃")
