# 🎬 What2Watch – Django × Gemini AI Movie Dashboard

A sleek, Netflix-style movie dashboard powered by **Gemini AI** (with OMDb fallback). Search movies intelligently, auto-fill details, and log them into a shared CSV file. Built with Django and deployed on Render.

---

## 🌟 Why this project?

We often forget **underrated masterpieces**, regional gems, or thought-provoking cinema that deeply moves us. This app helps curate a **shared, intelligent catalog** of must-watch films – be it emotional, artistic, or meaningful – with your friends.

It solves the classic "What should we watch?" dilemma and builds a **movie library that matters**.

---

## 🚀 Features

- 🤖 Smart movie search via **Gemini AI**
- 🔁 Auto fallback to **OMDb API**
- 📝 Auto-fills movie metadata (title, year, genre, cast, ratings, poster)
- 📁 Adds entries to a shared `movies.csv` file
- 🎛️ Filter dashboard by **language**, **genre**, or **decade**
- 👥 Register & login to track who added what
- 🖼️ Responsive UI with movie posters

---

## 🔐 API Key Setup

Before running, generate:

1. **Gemini API Key**  
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Generate & copy your Gemini API key.

2. **OMDb API Key**  
   - Register at [OMDb API](http://www.omdbapi.com/apikey.aspx)
   - Choose the free tier and get your key.

3. **Django Secret Key**  
   - Use any Django secret generator, e.g., [Djecrety](https://djecrety.ir/)

---

## 🛠️ Installation

```bash
git clone https://github.com/aryandhone555/What2Watch.git
cd What2Watch
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
