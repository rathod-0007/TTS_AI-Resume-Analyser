import streamlit as st
from pdfminer.high_level import extract_text
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq
import re
from dotenv import load_dotenv
import os
import sounddevice as sd
import numpy as np
import tempfile
import scipy.io.wavfile as wavfile
from faster_whisper import WhisperModel
import plotly.graph_objects as go

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Initialize session state
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
if "resume" not in st.session_state:
    st.session_state.resume = ""
if "job_desc" not in st.session_state:
    st.session_state.job_desc = ""
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "jd_skills" not in st.session_state:
    st.session_state.jd_skills = set()
if "resume_skills" not in st.session_state:
    st.session_state.resume_skills = set()

# UI Header
st.markdown("""
<h1 style='text-align: center; color: #4CAF50;'>🌟 AI Resume Analyzer 🔘</h1>
<p style='text-align: center; color: #aaa;'>Get Smart Feedback on your Resume and Improve Instantly!</p>
<hr style='border-top: 2px solid #4CAF50;'>
""", unsafe_allow_html=True)

# Function Definitions
def extract_pdf_text(uploaded_file):
    try:
        extracted_text = extract_text(uploaded_file)
        return extracted_text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return "Could not extract text from the PDF file."

def calculate_similarity_bert(text1, text2):
    ats_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    embeddings1 = ats_model.encode([text1])
    embeddings2 = ats_model.encode([text2])
    similarity = cosine_similarity(embeddings1, embeddings2)[0][0]
    return similarity

def extract_skills_from_text(text, is_jd=False):
    client = Groq(api_key=api_key)
    if is_jd:
        if len(text.split()) < 10:
            prompt = f"List the key skills required for a {text} role. Provide the skills as a comma-separated list."
        else:
            prompt = f"Based on the following job description, list the key skills required for the role. Provide the skills as a comma-separated list.\n\n{text}"
    else:
        prompt = f"Based on the following resume, list the skills that the candidate possesses. Provide the skills as a comma-separated list.\n\n{text}"
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-70b-8192"
    )
    skills_text = response.choices[0].message.content.strip()
    skills = [skill.strip().lower() for skill in skills_text.split(",")]
    return set(skills)

def show_skill_radar_chart(jd_skills, resume_skills):
    all_skills = sorted(jd_skills)
    match_vector = [1 if skill in resume_skills else 0 for skill in all_skills]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=match_vector + [match_vector[0]],
        theta=all_skills + [all_skills[0]],
        fill='toself',
        name='Skills Found in Resume',
        line=dict(color='green')
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        title="Skill Radar Chart"
    )
    st.plotly_chart(fig, use_container_width=True)
    missing_skills = jd_skills - resume_skills
    if missing_skills:
        st.write("**Missing Skills:**", ", ".join(missing_skills))

def get_report(resume, job_desc):
    client = Groq(api_key=api_key)
    prompt = f"""
# Context:
- You are an AI Resume Analyzer. You will be given the candidate's resume and the job description.

# Instruction:
- Analyze the resume based on the job description.
- If job description is empty, assume a generic software engineer JD.
- For each point, give a score (out of 5), with emojis (✅, ❌, ⚠) and explanations.
- Add suggestions at the end to improve the resume.

# Inputs:
Candidate Resume: {resume}
---
Job Description: {job_desc or "Software Engineer with strong fundamentals in Data Structures, Algorithms, OOPs, Git, Linux, and at least one programming language like Python or Java."}

# Output:
- Use score format like 3/5 at start of each point.
- Add emojis and detailed explanations.
"""
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-70b-8192"
    )
    return response.choices[0].message.content

def extract_scores(text):
    pattern = r'(\d+(?:\.\d+)?)/5'
    matches = re.findall(pattern, text)
    scores = [float(match) for match in matches]
    return scores

def transcribe_voice():
    duration = 5
    fs = 44100
    st.info("Recording... Speak now!")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        wavfile.write(temp_file.name, fs, recording)
        model = WhisperModel("tiny.en", device="cpu")
        segments, _ = model.transcribe(temp_file.name, beam_size=5)
        text = " ".join([segment.text for segment in segments]).strip()
    os.unlink(temp_file.name)
    return text if text else "No speech detected."

# Main Workflow
st.subheader("📤 Upload Resume & Job Description")
with st.form(key='resume_form'):
    resume_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])
    job_desc_input = st.text_area("Paste Job Description (Optional)", height=150)
    submit_button = st.form_submit_button(label="Analyze Resume 🚀")

if submit_button:
    if resume_file:
        st.session_state.resume = extract_pdf_text(resume_file)
        st.session_state.job_desc = job_desc_input
        jd_text = st.session_state.job_desc if st.session_state.job_desc else ""
        st.session_state.jd_skills = extract_skills_from_text(jd_text, is_jd=True)
        st.session_state.resume_skills = extract_skills_from_text(st.session_state.resume)
        st.session_state.form_submitted = True
        st.rerun()
    else:
        st.warning("Please Upload at least Resume to analyze")

if st.session_state.form_submitted:
    score_place = st.info("Generating Scores...")
    job_desc_for_ats = st.session_state.job_desc if st.session_state.job_desc else "Software Engineer with strong fundamentals in Data Structures, Algorithms, OOPs, Git, Linux, and at least one programming language like Python or Java."
    ats_score = calculate_similarity_bert(st.session_state.resume, job_desc_for_ats)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.metric("ATS Similarity Score", f"{ats_score * 100:.2f}")
    report = get_report(st.session_state.resume, st.session_state.job_desc)
    report_scores = extract_scores(report)
    avg_score = sum(report_scores) / (5 * len(report_scores)) if report_scores else 0.0
    with col2:
        st.metric("Average AI Review Score", f"{avg_score * 100:.2f}")
    score_place.success("Scores generated successfully!")
    
    st.subheader("🤖 AI Generated Analysis Report")
    st.markdown(f"""
    <div style='text-align: left; background-color: #f0f0f0; padding: 20px; border-radius: 12px; color: #333;'>
    {report}
    </div>
    """, unsafe_allow_html=True)
    st.download_button(label="📂 Download Report", data=report, file_name="report.txt", mime="text/plain")
    
    st.markdown("---")
    st.subheader("🌍 Skill Radar Chart")
    if st.session_state.jd_skills:
        show_skill_radar_chart(st.session_state.jd_skills, st.session_state.resume_skills)
    else:
        st.write("No skills extracted from the job description.")
    
    st.markdown("---")
    st.subheader("🤖 Ask Anything About Your Resume")
    col_text, col_mic = st.columns([4, 1])
    with col_text:
        user_input = st.text_input("Type your question", value=st.session_state.user_input, placeholder="e.g., What skills should I add?")
    with col_mic:
        if st.button("🎧 Speak"):
            voice_text = transcribe_voice()
            if voice_text:
                st.session_state.user_input = voice_text
                user_input = voice_text
    if user_input:
        with st.spinner("Thinking..."):
            chat_prompt = f"""
            You are a helpful AI assistant. The user has the following resume:
            {st.session_state.resume}
            Based on the resume, answer this question:
            "{user_input}"
            """
            response = Groq(api_key=api_key).chat.completions.create(
                messages=[{"role": "user", "content": chat_prompt}],
                model="llama3-70b-8192"
            )
            st.markdown(f"<div style='background-color:#222;padding:10px;border-radius:8px;color:#eee'><b>AI:</b> {response.choices[0].message.content.strip()}</div>", unsafe_allow_html=True)
