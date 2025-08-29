# app.py
from flask import Flask, render_template, request, jsonify, send_file
import json
import os
from utils import extract_keywords_from_job, generate_pdf_cv, generate_suggestions
from weasyprint import HTML
app = Flask(__name__)
USER_DATA_FILE = "data/user_data.json"

# Charger les données utilisateur
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Sauvegarder les données
def save_user_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

# app.py – dans la route /api/start
@app.route("/api/start", methods=["POST"])
def start():
    data = request.json
    job_ad = data.get("job_ad", "")

    keywords = extract_keywords_from_job(job_ad)
    suggestions = generate_suggestions(job_ad)  # ✅ Appel ici

    user_data = {
        "job_ad": job_ad,
        "keywords": keywords,
        "suggestions": suggestions,
        "step": 0
    }
    save_user_data(user_data)

    return jsonify({
        "message": "Bonjour ! Je suis votre assistant CV. Pour commencer, quel est votre nom complet ?",
        "step": "name",
        "suggestion": None
    })

# app.py – dans /api/next
@app.route("/api/next", methods=["POST"])
def next_step():
    user_data = load_user_data()
    step = user_data.get("step", 0)

    steps = ["name", "email", "phone", "experience", "skills", "education", "hobbies"]
    questions = {
        "name": "Quel est votre nom complet ?",
        "email": "Quel est votre email ?",
        "phone": "Quel est votre numéro de téléphone ?",
        "experience": "Décrivez une expérience professionnelle clé liée à cette annonce.",
        "skills": "Quelles sont vos compétences techniques principales ?",
        "education": "Quel est votre niveau d'étude et formations ?",
        "hobbies": "Souhaitez-vous ajouter des centres d’intérêt ? (facultatif)"
    }

    if step >= len(steps):
        return jsonify({"message": "Terminé !", "step": "done", "suggestion": None})

    current_step = steps[step]
    next_step = steps[step + 1] if step + 1 < len(steps) else "done"

    # ✅ Récupérer la suggestion pour la prochaine question
    suggestion = user_data["suggestions"].get(next_step) if next_step != "done" else None

    return jsonify({
        "message": questions[current_step],
        "step": current_step,
        "suggestion": suggestion  # ✅ Envoyée au frontend
    })

@app.route("/api/generate_cv", methods=["GET"])
def generate_cv():
    user_data = load_user_data()
    pdf_path = generate_pdf_cv(user_data)
    return send_file(pdf_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)