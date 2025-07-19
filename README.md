# 🎬 What2Watch – Django × Gemini AI Movie Dashboard

A sleek, Netflix-style movie dashboard powered by Gemini AI (with OMDb fallback). Search movies intelligently, auto-fill details, and log them into a shared CSV file. Built with Django and deployed on Render.

---

## 🚀 Features
- 🔍 Smart movie search using Gemini AI (fallback to OMDb API)
- 📄 Add movies to a shared catalog (`movies.csv`)
- 📊 Filter dashboard by language, genre, and decade (auto-generated)
- 🔒 Authentication (login/register)
- 🖼️ Clean, responsive UI with movie cards and poster previews

---

## 🛠️ Setup
```bash
git clone https://github.com/aryandhone555/What2Watch.git
cd What2Watch
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
