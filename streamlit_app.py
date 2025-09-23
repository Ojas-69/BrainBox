import streamlit as st
import pdfplumber
import os

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600&family=Chakra+Petch&display=swap');

    /* Background - brighter sci-fi vibe */
    .stApp {
        background: linear-gradient(135deg, #dbeafe, #f0f9ff, #f5f3ff);
        font-family: 'Chakra Petch', sans-serif;
        color: #111827;
    }

    /* Title + headings */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: #1e1b4b;
        text-shadow: 0px 0px 6px #a78bfa;
    }

    /* File uploader */
    .stFileUploader {
        background: #ffffff;
        border: 2px dashed #6366f1;
        border-radius: 16px;
        padding: 18px;
        transition: 0.3s ease-in-out;
    }
    .stFileUploader:hover {
        border-color: #a855f7;
        box-shadow: 0 0 10px #a78bfa;
    }

    /* Notes output boxes */
    .stMarkdown {
        background: #fdf4ff;
        padding: 14px;
        border-radius: 12px;
        margin-bottom: 12px;
        border: 1px solid #e9d5ff;
        box-shadow: 0 0 8px #f0abfc55;
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
