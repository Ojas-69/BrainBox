st.markdown("""
    <style>
    /* Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Poppins:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    /* Sci-fi animated background */
    .stApp {
        background: radial-gradient(circle at 20% 20%, #0f2027, #203a43, #2c5364);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        color: white;
    }

    @keyframes gradientShift {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    /* Title styling (sci-fi font) */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #00ffea;
        text-shadow: 0 0 10px #00ffeab3, 0 0 20px #00ffeab3;
    }

    /* Sidebar = dark neon */
    .css-1d391kg, .css-1l02zno {
        background: #111 !important;
        color: #0ff !important;
    }
    .css-1d391kg a, .css-1l02zno a {
        color: #ff00ff !important;
        font-weight: bold;
    }

    /* Buttons = meme neon */
    div.stButton > button {
        background: linear-gradient(90deg, #ff00cc, #3333ff);
        color: white;
        border-radius: 12px;
        padding: 0.7em 1.5em;
        font-weight: 700;
        font-family: 'Orbitron', sans-serif;
        border: none;
        box-shadow: 0 0 20px rgba(255, 0, 204, 0.6);
        transition: 0.3s ease-in-out;
    }
    div.stButton > button:hover {
        transform: scale(1.1) rotate(-1deg);
        box-shadow: 0 0 30px rgba(0, 255, 234, 0.9);
    }

    /* Download button glow */
    .stDownloadButton > button {
        background: #0ff;
        color: #111;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 0.7em 1.5em;
        box-shadow: 0 0 15px #0ff;
        transition: 0.3s ease-in-out;
    }
    .stDownloadButton > button:hover {
        background: #ff00cc;
        color: white;
        box-shadow: 0 0 30px #ff00cc;
    }

    /* Expander as holo-panels */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 234, 0.4);
        border-radius: 15px;
        padding: 10px;
        color: #0ff;
        font-weight: bold;
        text-shadow: 0 0 5px #0ff;
    }
    </style>
""", unsafe_allow_html=True)


import streamlit as st
import PyPDF2
import re
from transformers import pipeline

import streamlit as st

# --- TITLE + MEME TAGLINE ---
st.title("🧠 BrainBox")
st.markdown(
    "<h3 style='text-align: center; color: #ff00cc; font-family: Orbitron, sans-serif; text-shadow: 0 0 10px #ff00cc;'>⚡ Upload your PDF, awaken the braincells ⚡</h3>",
    unsafe_allow_html=True
)

# --- PDF UPLOAD SECTION ---
st.markdown(
    "<h4 style='color: #00ffea; font-family: Orbitron, sans-serif; text-shadow: 0 0 10px #00ffea;'>🚀 Beam up your PDF</h4>",
    unsafe_allow_html=True
)
uploaded_file = st.file_uploader("", type=["pdf"])


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
