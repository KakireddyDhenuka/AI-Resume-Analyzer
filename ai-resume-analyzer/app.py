import streamlit as st
import PyPDF2
import docx2txt
import re
import matplotlib.pyplot as plt

# --- Custom CSS for Old Money theme ---
st.markdown("""
<style>
/* Background and fonts */
body {
    background-color: #f5f5dc; /* beige */
    color: #1a1a1a;
    font-family: 'Times New Roman', serif;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #e9e4d4; /* Light cream */
}

/* Titles */
h1, h2, h3, h4 {
    color: #2f4f4f; /* Dark greenish-brown */
    font-family: 'Playfair Display', serif;
}

/* Button */
div.stButton > button:first-child {
    background-color: #2E4E3F;  /* deep muted green */
    color: white;
    font-size: 16px;
    font-weight: bold;
    border-radius: 10px;
    padding: 10px 24px;
    border: none;
}
div.stButton > button:first-child:hover {
    background-color: #3B5F4A; /* slightly lighter green on hover */
    color: #f1f1f1;
}

/* Text input and textarea */
div.stFileUploader, div.stTextArea, div.stTextInput {
    border-radius: 10px;
    background-color: #ffffff;
    padding: 5px;
}

/* Graph container */
div[data-testid="stVerticalBlock"] {
    background-color: #fdfaf0;
    border-radius: 12px;
    padding: 15px;
}
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file):
    return docx2txt.process(file)

def analyze_resume(resume_text, job_desc_text):
    job_words = set(re.findall(r'\b\w+\b', job_desc_text.lower()))
    resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
    match_count = len(job_words.intersection(resume_words))
    score = int((match_count / len(job_words)) * 100) if job_words else 0
    
    if score > 70:
        feedback = "Excellent match! Your resume aligns well with this job description."
    elif score > 40:
        feedback = "Good match. Consider adding more relevant skills or experience."
    else:
        feedback = "Low match. Review the job description and update your resume accordingly."
    
    return score, feedback, match_count, len(job_words)

# --- Streamlit App ---
st.title("📑 AI Resume Analyzer")
st.write("Upload your resume and paste the job description to get a professional match score.")

# Upload Resume
resume_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
resume_text = ""

if resume_file:
    try:
        if resume_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(resume_file)
        else:
            resume_text = extract_text_from_docx(resume_file)
        st.success("✅ Resume uploaded successfully!")
    except Exception as e:
        st.error(f"Error reading file: {e}")

# Job Description Box
job_desc_text = st.text_area("Paste Job Description Here:")

# Analyze Button
if st.button("Analyze Resume"):
    if resume_text and job_desc_text.strip():
        score, feedback, match_count, total_words = analyze_resume(resume_text, job_desc_text)
        st.success(f"Resume Score: {score}%")
        st.write("### Feedback")
        st.write(feedback)

        # --- Display Graph ---
        st.write("### Job Description Match")
        labels = ['Matched', 'Unmatched']
        values = [match_count, total_words - match_count]

        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90,
               colors=['#2E4E3F', '#d3c6a1'], textprops={'color':'#1a1a1a','fontsize':12})
        ax.axis('equal')  # Equal aspect ratio ensures pie chart is circular
        st.pyplot(fig)

    else:
        st.error("Please upload a resume and paste a job description first!")
