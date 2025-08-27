import io
import re
import json
import tempfile
import os
import docx2txt
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

# ---------- text extraction ----------
def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes using PyPDF2."""
    reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    texts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            texts.append(page_text)
    return "\n".join(texts)

def extract_text_from_docx_bytes(docx_bytes: bytes) -> str:
    """Write bytes to a temp file and use docx2txt to extract text."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(docx_bytes)
        tmp_path = tmp.name
    try:
        text = docx2txt.process(tmp_path) or ""
    finally:
        try:
            os.remove(tmp_path)
        except:
            pass
    return text

# ---------- skills loading & keyword matching ----------
def load_skill_list(path="skills.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            skills = json.load(f)
            return [s.strip() for s in skills]
    except Exception:
        # fallback default list
        return [
            "python", "java", "c++", "javascript", "flask", "django",
            "sql", "mysql", "postgresql", "mongodb", "aws", "azure",
            "gcp", "docker", "kubernetes", "git", "linux", "html", "css",
            "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
            "nlp", "opencv", "rest api", "api", "automation", "data analysis",
            "data visualization", "matplotlib", "plotly", "streamlit"
        ]

def extract_skills_by_keywords(text: str, skill_set) -> list:
    text_low = text.lower()
    found = set()
    for skill in skill_set:
        # word boundary match
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_low):
            found.add(skill)
    return sorted(found)

# ---------- spaCy candidate phrases ----------
@st.cache_resource
def load_spacy_model():
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        return nlp
    except Exception:
        # If model not installed, return None and show a friendly message later
        return None

def extract_candidate_phrases_spacy(text: str, nlp, top_n=40) -> list:
    if nlp is None:
        return []
    doc = nlp(text)
    candidates = []
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.strip().lower()
        if 2 <= len(chunk_text) <= 60:
            candidates.append(chunk_text)
    for ent in doc.ents:
        ent_text = ent.text.strip().lower()
        if 2 <= len(ent_text) <= 60:
            candidates.append(ent_text)
    # frequency
    freq = {}
    for c in candidates:
        freq[c] = freq.get(c, 0) + 1
    sorted_candidates = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [c for c, _ in sorted_candidates[:top_n]]

# ---------- similarity ----------
def compute_similarity_resume_job(resume_text: str, job_text: str):
    # If no job text, return 0
    if not job_text or not job_text.strip():
        return 0.0, []
    vect = TfidfVectorizer(stop_words="english", max_features=2000)
    docs = [resume_text, job_text]
    try:
        tfidf = vect.fit_transform(docs)
        sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    except Exception:
        sim = 0.0

    resume_terms = set(re.findall(r"\w+", resume_text.lower()))
    job_terms = set(re.findall(r"\w+", job_text.lower()))
    common = sorted(list(resume_terms.intersection(job_terms)))
    # surface only skill-like common terms
    return sim, common[:200]
