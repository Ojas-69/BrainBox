import streamlit as st
import pdfplumber
import os

# ---------------- CSS (lighter theme, sci-fi + meme-ish) ----------------
st.markdown("""
    <style>
    /* Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500&family=Chakra+Petch&display=swap');

    body {
        background-color: #f5f7fa; /* soft daylight grey */
        color: #1c1c1c;
    }
    .stApp {
        background: linear-gradient(120deg, #f5f7fa, #e6ecf5);
        font-family: 'Chakra Petch', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: #1e293b; /* dark slate */
        text-shadow: 1px 1px 0px #e0e7ff;
    }
    .upload-msg {
        text-align: center;
        font-size: 18px;
        color: #334155;
        margin-bottom: 12px;
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
