import streamlit as st
import pdfplumber
import re
from transformers import pipeline

# Summarizer model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Smart chunking function
def split_into_chunks(text, max_words=600):
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks, current_chunk, words = [], [], 0

    for sent in sentences:
        word_count = len(sent.split())
        if words + word_count > max_words:
            chunks.append(" ".join(current_chunk))
            current_chunk, words = [], 0
        current_chunk.append(sent)
        words += word_count
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

# ✅ New extractor (replacing PyPDF2)
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:  
                text += page_text + "\n"
    return text

# Summarizer function
def summarize_text(full_text):
    chunks = split_into_chunks(full_text)
    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=200, min_length=80, do_sample=False)
        summaries.append(summary[0]['summary_text'])
    # Merge into one final summary
    combined = " ".join(summaries)
    final_summary = summarizer(combined, max_length=300, min_length=150, do_sample=False)
    return final_summary[0]['summary_text']

# Streamlit UI
st.title("🧠 BrainBox - Smart PDF Notes Generator")
uploaded_file = st.file_uploader("Upload your PDF here", type=["pdf"])

if uploaded_file is not None:
    st.info("Processing your PDF... ⏳ This may take a while for big files.")
    raw_text = extract_text_from_pdf(uploaded_file)
    if raw_text.strip():
        summary = summarize_text(raw_text)
        st.subheader("📝 Generated Notes")
        st.write(summary)
    else:
        st.error("Could not extract any text from this PDF. Try another file.")
