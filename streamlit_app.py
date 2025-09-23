import streamlit as st
from transformers import pipeline

# Load summarizer model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Function to split text into safe chunks (so model doesn't explode)
def split_text(text, max_chunk_size=900):
    words = text.split()
    chunks, current = [], []

    for word in words:
        if sum(len(w) for w in current) + len(word) + len(current) <= max_chunk_size:
            current.append(word)
        else:
            chunks.append(" ".join(current))
            current = [word]
    if current:
        chunks.append(" ".join(current))
    return chunks

# Function to summarize safely
def summarize_text(text):
    chunks = split_text(text)
    summaries = []
    for chunk in chunks:
        summary = summarizer(
            chunk,
            max_length=200,
            min_length=80,
            do_sample=False
        )
        summaries.append(summary[0]['summary_text'])
    return " ".join(summaries)

# Streamlit UI
st.title("BrainBox – PDF Summarizer 🧠📄")
uploaded_file = st.file_uploader("Upload your PDF", type="pdf")

if uploaded_file is not None:
    from PyPDF2 import PdfReader

    pdf_reader = PdfReader(uploaded_file)
    raw_text = ""
    for page in pdf_reader.pages:
        raw_text += page.extract_text() + " "

    if st.button("Summarize"):
        with st.spinner("Cooking up that summary... 🍳"):
            summary = summarize_text(raw_text)
        st.subheader("Summary:")
        st.write(summary)
