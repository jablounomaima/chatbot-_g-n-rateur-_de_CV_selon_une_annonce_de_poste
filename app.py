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
        "suggestion": None
    })

@app.route("/api/next", methods=["POST"])
def next_step():
    user_data = load_user_data()
    step = user_data.get("step", 0)
    message = request.json.get("message", "").strip()

    steps = ["name", "email", "phone", "experience", "skills", "education", "hobbies"]
    questions = {
        "name": "Quel est votre email ?",
        "email": "Quel est votre numéro de téléphone ?",
        "phone": "Décrivez une expérience professionnelle clé liée à cette annonce.",
        "experience": "Quelles sont vos compétences techniques principales ?",
        "skills": "Quel est votre niveau d'étude et formations ?",
        "education": "Souhaitez-vous ajouter des centres d’intérêt ? (facultatif)",
        "hobbies": "✅ CV presque prêt ! Téléchargez-le ci-dessous."
    }

    # Sauvegarder la réponse actuelle
    if step < len(steps):
        current_field = steps[step]
        user_data[current_field] = message
        user_data["step"] += 1
        save_user_data(user_data)

    # Préparer la prochaine étape
    if step >= len(steps):
        return jsonify({
            "message": "Terminé !",
            "step": "done",
            "suggestion": None
        })

    next_step_key = steps[step] if step < len(steps) else "done"
    next_message = questions.get(next_step_key, "Merci pour vos réponses !")

    # Obtenir la suggestion pour la prochaine question
    suggestion = None
    if next_step_key != "done" and "suggestions" in user_data:
        suggestion = user_data["suggestions"].get(next_step_key)

    return jsonify({
        "message": next_message,
        "step": next_step_key,
        "suggestion": suggestion
    })

@app.route("/api/generate_cv", methods=["GET"])
def generate_cv():
    user_data = load_user_data()
    pdf_path = generate_pdf_cv(user_data)
    return send_file(pdf_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)