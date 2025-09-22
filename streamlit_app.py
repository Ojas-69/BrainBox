import streamlit as st
import PyPDF2
import random

# ------------------ APP SETUP ------------------ #
st.set_page_config(page_title="BrainBox", page_icon="🧠", layout="wide")

st.title("🧠 BrainBox: Your AI-Powered Study Buddy")
st.markdown("Upload PDFs, get summaries, and auto-generate questions. No stress, just flex.")

# ------------------ PDF UPLOAD ------------------ #
uploaded_file = st.file_uploader("📂 Upload your study material (PDF)", type="pdf")

text = ""

if uploaded_file is not None:
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    for page in pdf_reader.pages:
        text += page.extract_text() or ""

    st.success("✅ PDF uploaded and processed successfully!")
    st.subheader("📑 Extracted Text Preview")
    st.text_area("Here’s a sneak peek of your PDF:", text[:1000] + "...", height=200)

# ------------------ SUMMARY FUNCTION ------------------ #
def summarize_text(content, max_sentences=5):
    sentences = content.split(".")
    if len(sentences) <= max_sentences:
        return content
    return ". ".join(sentences[:max_sentences]) + "."

# ------------------ QUESTION GENERATOR ------------------ #
def generate_questions(content, num_questions=5):
    sentences = [s.strip() for s in content.split(".") if len(s.strip()) > 10]
    random.shuffle(sentences)
    questions = []
    for i, sent in enumerate(sentences[:num_questions]):
        q = sent.replace(" is ", " ______ is ").replace(" are ", " ______ are ")
        q = q.replace(" was ", " ______ was ").replace(" were ", " ______ were ")
        if q == sent:  
            q = "What is the significance of: " + sent[:50] + "..."
        questions.append(f"Q{i+1}: {q}?")
    return questions

# ------------------ MAIN FEATURES ------------------ #
if text:
    st.subheader("📝 Notes / Summary")
    summary = summarize_text(text)
    st.write(summary)

    st.subheader("❓ Practice Questions")
    qs = generate_questions(text, num_questions=5)
    for q in qs:
        st.write(q)

    st.download_button("⬇️ Download Notes", summary, file_name="BrainBox_Notes.txt")

else:
    st.info("👆 Upload a PDF to get started!")

# ------------------ FOOTER ------------------ #
st.markdown("---")
st.caption("Built with ❤️ by Ojas (and a suspiciously helpful AI)")
