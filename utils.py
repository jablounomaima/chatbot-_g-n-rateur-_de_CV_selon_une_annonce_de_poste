# utils.py

import spacy
from jinja2 import Environment, FileSystemLoader

# Charger le modèle NLP
try:
    nlp = spacy.load("fr_core_news_sm")
except OSError:
    raise OSError(
        "Erreur : le modèle spaCy 'fr_core_news_sm' n'est pas installé.\n"
        "Exécute : python -m spacy download fr_core_news_sm"
    )

def extract_keywords_from_job(job_text):
    doc = nlp(job_text.lower())
    skills = []
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop:
            if any(word in token.lemma_ for word in ["compétence", "outil", "langage", "technologie", "expérience"]):
                continue
            # Mots pertinents
            if len(token.lemma_) > 3:
                skills.append(token.lemma_.capitalize())
    # Extraire aussi les entités nommées
    for ent in doc.ents:
        if ent.label_ in ["SKILL", "WORK_OF_ART", "PRODUCT", "LANGUAGE"]:
            skills.append(ent.text.capitalize())
    return list(set(skills))[:10]

### 🔥 AJOUTE CETTE FONCTION DANS utils.py 🔥
# utils.py

import spacy

# Charger spaCy
try:
    nlp = spacy.load("fr_core_news_sm")
except OSError:
    raise OSError("Installe le modèle : python -m spacy download fr_core_news_sm")

def extract_keywords_from_job(job_text):
    doc = nlp(job_text.lower())
    return [ent.text.capitalize() for ent in doc.ents if ent.label_ in ["SKILL", "WORK_OF_ART", "PRODUCT"]][:5]

def generate_suggestions(job_text):
    doc = nlp(job_text.lower())
    
    # Extraire compétences, mots-clés
    skills = [ent.text.capitalize() for ent in doc.ents if ent.label_ in ["SKILL", "WORK_OF_ART", "PRODUCT"]]
    if not skills:
        skills = ["React", "Gestion de projet", "Communication"]

    job_titles = ["développeur", "chef de projet", "data analyst", "commercial", "designer"]
    detected_job = "professionnel"
    for job in job_titles:
        if job in job_text.lower():
            detected_job = job
            break

    locations = [ent.text.title() for ent in doc.ents if ent.label_ == "GPE"]
    location = locations[0] if locations else "France"

    return {
        "experience": [
            f"En tant que {detected_job}, j'ai piloté des projets centrés sur {skills[0]}, en méthode Agile.",
            f"Expérience clé : conception et mise en œuvre de solutions autour de {skills[0]}.",
            f"Amélioration des performances de 30 % grâce à une optimisation ciblée sur {skills[0]}."
        ],
        "skills": [
            f"Compétences : {', '.join(skills[:4])}, travail en équipe, communication.",
            f"Maîtrise de {skills[0]} et des outils collaboratifs (Trello, Slack).",
            f"Expertise en {skills[0]} et en gestion de projet."
        ],
        "education": [
            f"Master en {skills[0]} – Université de Lyon, 2020–2022.",
            f"Formation en lien avec {skills[0]}, complétée par des certifications.",
            f"Diplôme en gestion de projet avec spécialisation en {skills[0]}."
        ],
        "hobbies": [
            f"Passionné(e) par la veille tech et les meetups {skills[0]}.",
            f"Jeux vidéo, lecture, et bénévolat dans l'enseignement numérique.",
            f"Voyages et participation à des hackathons {skills[0]}."
        ],
        "objective": [
            f"À la recherche d’un poste de {detected_job} à {location}, où je pourrai appliquer mes compétences en {skills[0]}.",
            f"Objectif : contribuer à des projets innovants dans un environnement dynamique et collaboratif.",
            f"Souhaite rejoindre une entreprise en croissance pour développer des solutions autour de {skills[0]}."
        ]
    }

import pdfkit

# utils.py

import pdfkit
from jinja2 import Environment, FileSystemLoader
import os

def generate_pdf_cv(user_data):
    """
    Génère un CV en PDF à partir d'un template HTML.
    """
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('cv_template.html')
    
    html_out = template.render(
        name=user_data.get("name", "John Doe"),
        email=user_data.get("email", ""),
        phone=user_data.get("phone", ""),
        objective=user_data.get("objective", "Objectif professionnel"),
        experience=user_data.get("experience", "Aucune expérience fournie."),
        skills=user_data.get("skills", "Aucune compétence fournie."),
        education=user_data.get("education", "Aucune formation fournie."),
        hobbies=user_data.get("hobbies", ""),
        keywords=user_data.get("keywords", [])
    )

    # Chemin vers wkhtmltopdf
    path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    
    # Générer le PDF
    pdf_path = "static/cv_genere.pdf"
    pdfkit.from_string(html_out, pdf_path, configuration=config)
    return pdf_path