import streamlit as st
import PyPDF2
import re
from transformers import pipeline

# --- Load Hugging Face Pipelines ---
@st.cache_resource
def load_pipelines():
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    qg = pipeline("text2text-generation", model="iarfmoose/t5-base-question-generator")
    return summarizer, qg

summarizer, qg = load_pipelines()

# --- Helper Functions ---
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def chunk_text(text, chunk_size=800):
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size])

def summarize_text(text):
    try:
        return summarizer(text, max_length=120, min_length=30, do_sample=False)[0]['summary_text']
    except:
        return "⚠️ Could not summarize this chunk."

def generate_questions(text, num_qs=3):
    try:
        raw_qs = qg("generate questions: " + text, max_length=64, num_return_sequences=num_qs)
        return [q['generated_text'] for q in raw_qs]
    except:
        return ["⚠️ Could not generate questions."]

# --- Streamlit UI ---
st.title("🤖 BrainBox Turbo AI — Handles 1000+ Page PDFs 🧠")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    st.success("✅ PDF uploaded successfully!")

    # Extract text
    text = extract_text_from_pdf(uploaded_file)
    st.write(f"📖 Extracted {len(text.split())} words.")

    # Process chunks
    st.header("🔎 Chunk Summaries & Questions")
    final_summary = []
    for i, chunk in enumerate(chunk_text(text, chunk_size=800)):
        st.subheader(f"📌 Chunk {i+1}")
        
        summary = summarize_text(chunk)
        questions = generate_questions(chunk)

        st.write("**AI Summary:**", summary)
        st.write("**AI Questions:**")
        for q in questions:
            st.write("-", q)

        final_summary.append(summary)

    # Final mega-summary
    st.header("✨ Final Combined AI Summary")
    st.write(" ".join(final_summary[:8]))
