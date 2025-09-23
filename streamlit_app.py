import streamlit as st
import pdfplumber
import os

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600&family=Chakra+Petch&display=swap');

    /* Background - clean gradient */
    .stApp {
        background: linear-gradient(135deg, #e0f7fa, #f1f5f9, #e0e7ff);
        font-family: 'Chakra Petch', sans-serif;
        color: #111827;
    }

    /* Headings */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: #0f172a;
        text-shadow: 1px 1px 2px #94a3b8;
    }

    /* Upload box */
    .stFileUploader {
        background: #f8fafc;
        border: 2px dashed #6366f1;
        border-radius: 15px;
        padding: 20px;
    }

    /* Notes section */
    .stMarkdown {
        background: #ffffffaa;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 12px;
        border: 1px solid #cbd5e1;
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
