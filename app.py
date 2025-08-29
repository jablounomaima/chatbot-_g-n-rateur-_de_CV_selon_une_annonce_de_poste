from flask import Flask, render_template, request, jsonify, send_file
import json
import os
from utils import extract_keywords_from_job, generate_suggestions, generate_pdf_cv

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

@app.route("/api/start", methods=["POST"])
def start():
    data = request.json
    job_ad = data.get("job_ad", "").strip()
    
    if not job_ad:
        return jsonify({"error": "L'annonce est vide"}), 400

    keywords = extract_keywords_from_job(job_ad)
    suggestions = generate_suggestions(job_ad)  # ✅ Fonction définie dans utils.py

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
        "suggestions": []  # Pas de suggestion pour le nom
    })

@app.route("/api/next", methods=["POST"])
def next_step():
    user_data = load_user_data()
    step = user_data.get("step", 0)
    message = request.json.get("message", "").strip()

    steps = ["name", "email", "phone", "experience", "skills", "education", "hobbies"]
    questions = {
        "name": "Quel est votre email ?",
        "email": "Quel est votre téléphone ?",
        "phone": "Décrivez une expérience pertinente.",
        "experience": "Vos compétences techniques ?",
        "skills": "Vos formations ?",
        "education": "Centres d’intérêt ?",
        "hobbies": "✅ CV prêt !"
    }

    if step < len(steps):
        user_data[steps[step]] = message
        user_data["step"] += 1
        save_user_data(user_data)

    if step >= len(steps):
        return jsonify({"message": "Terminé !", "step": "done", "suggestions": []})

    next_step_key = steps[step]
    return jsonify({
        "message": questions[next_step_key],
        "step": next_step_key,
        "suggestions": user_data["suggestions"].get(next_step_key, [])  # ✅ Envoie la liste
    })

@app.route("/api/generate_cv", methods=["GET"])
def generate_cv():
    user_data = load_user_data()
    pdf_path = generate_pdf_cv(user_data)
    return send_file(pdf_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)