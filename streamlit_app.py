import streamlit as st
import pdfplumber
import os

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    /* Background - soft minimalist */
    .stApp {
        background: #f9fafb;
        font-family: 'Inter', sans-serif;
        color: #1f2937;
    }

    /* Headings with pastel highlight */
    h1, h2, h3 {
        font-weight: 600;
        color: #111827;
        letter-spacing: -0.5px;
        padding-bottom: 4px;
        border-bottom: 3px solid #a5b4fc; /* soft indigo highlight */
        display: inline-block;
    }

    /* File uploader - flat, no chunky box */
    .stFileUploader {
        background: transparent;
        border: 2px dashed #d1d5db;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        transition: 0.2s ease-in-out;
    }
    .stFileUploader:hover {
        border-color: #818cf8; /* indigo highlight */
        background: #eef2ff; /* very soft indigo */
    }

    /* Notes output - clean text only */
    .stMarkdown {
        background: transparent !important;
        padding: 10px 0;
        border: none !important;
        box-shadow: none !important;
        margin-bottom: 14px;
        font-size: 1rem;
        line-height: 1.6;
    }

    /* Accent on bullet points / lists */
    .stMarkdown ul li::marker {
        color: #10b981; /* soft green */
        font-weight: bold;
    }

    /* Buttons */
    .stDownloadButton > button {
        background: #6366f1; /* indigo */
        color: #ffffff;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
        transition: 0.2s ease-in-out;
    }
    .stDownloadButton > button:hover {
        background: #4f46e5;
    }
    </style>
""", unsafe_allow_html=True)




# ---------------- Title ----------------
st.markdown("<h1 style='text-align:center;'>🧠 BrainBox</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:20px;'>Turning 1000-page pain into snack-sized notes 🚀</p>", unsafe_allow_html=True)
st.markdown("---")

# ---------------- File Upload ----------------
st.markdown("<div class='upload-msg'>📂 Step 1: Drop your PDF here 👇</div>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Choose your PDF", type=["pdf"], label_visibility="visible")

# ---------------- Notes Generator ----------------
if uploaded_file is not None:
    st.markdown("### ⚡ Step 2: Summoning notes...")
    with pdfplumber.open(uploaded_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
    
    if text.strip() == "":
        st.error("🚨 No extractable text found in this PDF. Maybe it’s all images?")
    else:
        # Simple "notes" → just paragraph breakup
        notes = "\n\n".join([chunk.strip() for chunk in text.split("\n") if chunk.strip()])
        
        st.success("✅ Done! Your notes are ready below ⬇️")
        st.text_area("📑 Notes:", notes[:5000], height=300)

        # Save + download option
        notes_file = "notes.txt"
        with open(notes_file, "w", encoding="utf-8") as f:
            f.write(notes)

        with open(notes_file, "rb") as f:
            st.download_button("⬇️ Download Notes", f, file_name="BrainBox_Notes.txt")
