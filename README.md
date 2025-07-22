# 🌟 AI Resume Analyzer

Welcome to the **AI Resume Analyzer** – your personal AI-powered career assistant!  
This Streamlit web app helps you improve your resume and increase your chances of landing your dream job by comparing your resume to real job descriptions using powerful AI models like **LLAMA-3** and **BERT**.

---

## 🚀 What Can It Do?

Whether you're a fresh graduate or a seasoned professional, this app will help you:

### 📄 1. Extract Resume Text
Upload your resume in PDF format. We'll automatically extract and clean the content using `pdfminer.six`.

### 🧾 2. Analyze Against Job Descriptions
Paste any job description or use our default Software Engineer JD.  
The app compares your resume with the job role using **BERT embeddings** and gives you an **ATS score**.

### 🧠 3. AI-Powered Resume Review
Using **Groq’s LLAMA-3 70B**, you'll receive:
- Section-wise evaluation (skills, projects, education, etc.)
- Emoji indicators (✅ Good, ❌ Missing, ⚠️ Needs work)
- Actionable improvement tips tailored to your resume

### 📊 4. Skill Radar Visualization
See how your skills match the job description in a radar chart.  
Spot missing or underrepresented skills instantly.

### 🎤 5. Voice-based Q&A (Optional)
Ask questions about your resume using your voice!  
We use **faster-whisper** for speech-to-text and LLAMA-3 for intelligent answers.

### 📥 6. Download a Detailed Report
Get a clean text report summarizing your resume’s strengths, weaknesses, and improvement tips.

---

## 💡 Why Use This?

- ✅ **Improve ATS Compatibility** – Make sure your resume gets past bots.
- 🤖 **AI Insights** – Get detailed feedback without hiring a resume consultant.
- 🎯 **Skill Gap Analysis** – Identify and close gaps between you and your target job.
- 🔄 **Reanalyze Anytime** – Upload newer versions of your resume as you improve.

---

## ⚙️ How to Set It Up Locally

Make sure you have the following installed:
- Python 3.9 or newer
- `pip` (Python package manager)
- Git

### 🛠️ Steps to Install

```bash
# 1. Clone this repository
git clone https://github.com/yourusername/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py


---
