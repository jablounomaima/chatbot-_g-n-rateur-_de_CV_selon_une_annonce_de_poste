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

def generate_suggestions(job_text):
    """
    Génère des suggestions de réponses basées sur le contenu de l'annonce.
    """
    doc = nlp(job_text.lower())

    # Extraire compétences
    skills = [ent.text.capitalize() for ent in doc.ents if ent.label_ in ["SKILL", "WORK_OF_ART", "PRODUCT"]]
    if not skills:
        skills = [token.lemma_.capitalize() for token in doc if token.pos_ == "NOUN" and len(token.lemma_) > 4][:3]

    # Détecter le type de poste
    job_titles = {
        "développeur": ["développeur", "dev", "engineer", "programmeur"],
        "chef de projet": ["chef de projet", "project manager", "gestionnaire"],
        "data analyst": ["analyste", "data", "scientifique"],
        "commercial": ["commercial", "vendeur", "account manager"]
    }
    detected_job = "professionnel"
    for job, keywords in job_titles.items():
        if any(k in job_text.lower() for k in keywords):
            detected_job = job
            break

    # Générer les suggestions
    return {
        "experience": (
            f"En tant que {detected_job}, j'ai piloté des projets centrés sur {skills[0] if skills else 'l\'innovation'}, "
            f"dans un environnement Agile, en utilisant {skills[1] if len(skills) > 1 else 'des outils modernes'} "
            "pour améliorer l'efficacité opérationnelle."
        ),
        "skills": (
            f"Compétences clés : {', '.join(skills[:4])}, travail en équipe, communication, résolution de problèmes."
        ),
        "education": (
            f"Master en {skills[0] if skills else 'Informatique ou Gestion'} – Université de Lyon, 2020–2022. "
            f"Projet sur l'optimisation des processus liés à {skills[0] if skills else 'la performance'}."
        ),
        "hobbies": (
            f"Passionné(e) par la veille technologique, les meetups {skills[0] if skills else 'IT'}, "
            "et le bénévolat dans des projets éducatifs."
        ),
        "objective": (
            f"À la recherche d’un poste de {detected_job} dans une entreprise innovante, "
            f"où je pourrai appliquer mes compétences en {skills[0] if skills else 'gestion de projet'}."
        )
    }
    

import pdfkit

def generate_pdf_cv(user_data):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('cv_template.html')
    html_out = template.render(
        name=user_data.get("name", "John Doe"),
        email=user_data.get("email", ""),
        phone=user_data.get("phone", ""),
        objective=user_data.get("objective", ""),
        experience=user_data.get("experience", ""),
        skills=user_data.get("skills", ""),
        education=user_data.get("education", ""),
        hobbies=user_data.get("hobbies", ""),
        keywords=user_data.get("keywords", [])
    )

    # Chemin vers wkhtmltopdf
    path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"  # Vérifie ce chemin !
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    
    pdf_path = "static/cv_genere.pdf"
    pdfkit.from_string(html_out, pdf_path, configuration=config)
    return pdf_path