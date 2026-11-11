# ============================================================
# MediPredict - AI Symptom / Department Recommender
# ============================================================

import re


# ------------------------------------------------------------
# Symptom knowledge base
# ------------------------------------------------------------

DEPARTMENT_KEYWORDS = {

    "General Medicine": [
        "fever",
        "cold",
        "cough",
        "weakness",
        "fatigue",
        "body pain",
        "headache",
        "vomiting",
        "nausea",
        "infection",
        "flu",
        "dizziness",
    ],

    "Cardiology": [
        "chest pain",
        "heart pain",
        "palpitation",
        "palpitations",
        "heart beating fast",
        "irregular heartbeat",
        "shortness of breath",
        "breathlessness",
        "high blood pressure",
        "hypertension",
    ],

    "Neurology": [
        "migraine",
        "severe headache",
        "seizure",
        "fits",
        "memory loss",
        "numbness",
        "tingling",
        "tremor",
        "paralysis",
        "vertigo",
    ],

    "Dermatology": [
        "skin rash",
        "rash",
        "itching",
        "acne",
        "eczema",
        "psoriasis",
        "skin infection",
        "hair loss",
        "red skin",
    ],

    "Orthopedics": [
        "bone pain",
        "joint pain",
        "back pain",
        "knee pain",
        "shoulder pain",
        "fracture",
        "swelling in joint",
        "arthritis",
        "muscle pain",
    ],

    "Gastroenterology": [
        "stomach pain",
        "abdominal pain",
        "gastric",
        "acidity",
        "indigestion",
        "diarrhea",
        "constipation",
        "heartburn",
        "ulcer",
        "bloating",
    ],

    "Pulmonology": [
        "breathing problem",
        "breathing difficulty",
        "persistent cough",
        "lung pain",
        "wheezing",
        "asthma",
        "phlegm",
        "respiratory",
    ],

    "ENT": [
        "ear pain",
        "ear infection",
        "hearing problem",
        "sore throat",
        "throat pain",
        "sinus",
        "sinusitis",
        "runny nose",
        "blocked nose",
        "nose bleeding",
    ],

    "Ophthalmology": [
        "eye pain",
        "eye infection",
        "blurred vision",
        "vision problem",
        "red eyes",
        "watery eyes",
        "eye swelling",
    ],

    "Pediatrics": [
        "child fever",
        "baby fever",
        "child cough",
        "child vomiting",
        "child diarrhea",
        "infant",
        "baby",
        "child",
    ],

    "Gynecology": [
        "period pain",
        "menstrual pain",
        "irregular periods",
        "pregnancy",
        "pregnancy pain",
        "pelvic pain",
        "vaginal pain",
        "pregnancy bleeding",
    ],

    "Psychiatry": [
        "anxiety",
        "panic attack",
        "stress",
        "depression",
        "insomnia",
        "sleep problem",
        "mood swings",
        "mental stress",
    ],
}


# ------------------------------------------------------------
# Text normalization
# ------------------------------------------------------------

def normalize_text(text):
    """
    Normalize user symptom text for matching.
    """

    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ------------------------------------------------------------
# Recommendation
# ------------------------------------------------------------

def recommend_department(symptoms):
    """
    Recommend a hospital department from the symptoms.

    Returns a dictionary containing:
        department
        confidence
        matched_symptoms
        message
    """

    text = normalize_text(symptoms)

    if not text:

        return {
            "department": "General Medicine",
            "confidence": 0,
            "matched_symptoms": [],
            "message": (
                "Please describe your symptoms "
                "for a better recommendation."
            ),
        }


    scores = {}

    matches = {}


    # --------------------------------------------------------
    # Match symptoms against department knowledge base
    # --------------------------------------------------------

    for department, keywords in DEPARTMENT_KEYWORDS.items():

        score = 0
        department_matches = []

        for keyword in keywords:

            keyword_normalized = normalize_text(
                keyword
            )

            if keyword_normalized in text:

                score += 1

                department_matches.append(
                    keyword
                )

        scores[department] = score

        matches[department] = (
            department_matches
        )


    # --------------------------------------------------------
    # No match
    # --------------------------------------------------------

    max_score = max(
        scores.values()
    )

    if max_score == 0:

        return {
            "department": "General Medicine",
            "confidence": 35,
            "matched_symptoms": [],
            "message": (
                "The symptoms do not strongly match "
                "a specific department. General Medicine "
                "is a reasonable starting point."
            ),
        }


    # --------------------------------------------------------
    # Best department
    # --------------------------------------------------------

    best_departments = [
        department
        for department, score in scores.items()
        if score == max_score
    ]

    best_department = (
        best_departments[0]
    )

    matched_symptoms = (
        matches[best_department]
    )


    # --------------------------------------------------------
    # Confidence calculation
    # --------------------------------------------------------

    confidence = min(
        95,
        50 + (max_score * 12)
    )


    # --------------------------------------------------------
    # Result message
    # --------------------------------------------------------

    message = (
        f"Based on the symptoms provided, "
        f"{best_department} may be the most relevant "
        f"department."
    )

    return {
        "department": best_department,
        "confidence": confidence,
        "matched_symptoms": matched_symptoms,
        "message": message,
    }