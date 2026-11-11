# ============================================================
# MediPredict - AI Assistant / Chatbot
# ============================================================

import re


# ------------------------------------------------------------
# Basic response helpers
# ------------------------------------------------------------

def clean_message(message):
    """
    Clean and normalize the user's message.
    """

    if not message:
        return ""

    message = message.lower().strip()

    message = re.sub(
        r"\s+",
        " ",
        message
    )

    return message


# ------------------------------------------------------------
# Emergency keywords
# ------------------------------------------------------------

EMERGENCY_KEYWORDS = [
    "severe chest pain",
    "chest pain",
    "difficulty breathing",
    "cannot breathe",
    "breathing difficulty",
    "unconscious",
    "heavy bleeding",
    "severe bleeding",
    "stroke",
    "seizure",
    "fainted",
    "suicide",
    "self harm",
]


# ------------------------------------------------------------
# Keyword groups
# ------------------------------------------------------------

GREETING_WORDS = [
    "hello",
    "hi",
    "hey",
    "namaste",
    "good morning",
    "good evening",
    "good afternoon",
]


APPOINTMENT_WORDS = [
    "appointment",
    "book appointment",
    "doctor appointment",
    "schedule appointment",
]


DOCTOR_WORDS = [
    "doctor",
    "specialist",
    "physician",
    "find doctor",
]


FEVER_WORDS = [
    "fever",
    "temperature",
    "high temperature",
]


COUGH_WORDS = [
    "cough",
    "coughing",
]


HEADACHE_WORDS = [
    "headache",
    "migraine",
    "head pain",
]


STOMACH_WORDS = [
    "stomach pain",
    "abdominal pain",
    "acidity",
    "gas",
    "indigestion",
    "diarrhea",
    "constipation",
]


BED_WORDS = [
    "bed",
    "beds",
    "icu",
    "icu bed",
    "hospital bed",
]


# ------------------------------------------------------------
# Emergency response
# ------------------------------------------------------------

def emergency_response():
    return (
        "Your message may describe a potentially serious "
        "medical situation. Please seek urgent medical care "
        "or contact your local emergency service immediately. "
        "Do not rely on this chatbot for emergency diagnosis "
        "or treatment."
    )


# ------------------------------------------------------------
# Main chatbot
# ------------------------------------------------------------

def chatbot_reply(message):
    """
    Generate a response for the MediPredict AI Assistant.

    This is an informational rule-based assistant.
    It does not diagnose diseases.
    """

    text = clean_message(message)

    if not text:

        return (
            "Please describe your question or symptoms, "
            "and I will try to guide you."
        )


    # --------------------------------------------------------
    # Emergency check
    # --------------------------------------------------------

    for keyword in EMERGENCY_KEYWORDS:

        if keyword in text:

            return emergency_response()


    # --------------------------------------------------------
    # Greeting
    # --------------------------------------------------------

    if any(
        word in text
        for word in GREETING_WORDS
    ):

        return (
            "Hello! 👋 I am the MediPredict AI Assistant. "
            "I can help you understand hospital services, "
            "find the appropriate department, and guide you "
            "toward appointments. How can I help you today?"
        )


    # --------------------------------------------------------
    # Appointment
    # --------------------------------------------------------

    if any(
        word in text
        for word in APPOINTMENT_WORDS
    ):

        return (
            "You can book an appointment from the "
            "'My Appointments' section after selecting a doctor. "
            "Choose an available date and time, then submit "
            "your appointment request."
        )


    # --------------------------------------------------------
    # Doctor
    # --------------------------------------------------------

    if any(
        word in text
        for word in DOCTOR_WORDS
    ):

        return (
            "You can use the 'Find Doctor' section to search "
            "doctors by name, specialization, or department. "
            "You can then open a doctor's profile and book "
            "an available appointment."
        )


    # --------------------------------------------------------
    # Fever
    # --------------------------------------------------------

    if any(
        word in text
        for word in FEVER_WORDS
    ):

        return (
            "Fever can have many possible causes. "
            "For general guidance, you may start with "
            "General Medicine. If the fever is persistent, "
            "very high, worsening, or accompanied by serious "
            "symptoms, seek medical evaluation."
        )


    # --------------------------------------------------------
    # Cough
    # --------------------------------------------------------

    if any(
        word in text
        for word in COUGH_WORDS
    ):

        return (
            "A cough can occur with many conditions. "
            "General Medicine can be a suitable starting "
            "department for an initial evaluation. "
            "Persistent or worsening breathing symptoms "
            "should be medically evaluated."
        )


    # --------------------------------------------------------
    # Headache
    # --------------------------------------------------------

    if any(
        word in text
        for word in HEADACHE_WORDS
    ):

        return (
            "Headaches have many possible causes. "
            "General Medicine can provide an initial "
            "evaluation, while recurring or specific "
            "neurological symptoms may require a specialist."
        )


    # --------------------------------------------------------
    # Stomach
    # --------------------------------------------------------

    if any(
        word in text
        for word in STOMACH_WORDS
    ):

        return (
            "For stomach, digestive, or acidity-related "
            "symptoms, General Medicine or Gastroenterology "
            "may be relevant depending on the symptoms."
        )


    # --------------------------------------------------------
    # Bed / ICU
    # --------------------------------------------------------

    if any(
        word in text
        for word in BED_WORDS
    ):

        return (
            "Bed and ICU availability is managed by the "
            "hospital administration. Please contact the "
            "hospital or check the Bed & ICU section when "
            "availability information is provided."
        )


    # --------------------------------------------------------
    # Thank you
    # --------------------------------------------------------

    if (
        "thank you" in text
        or "thanks" in text
        or "thank" in text
    ):

        return (
            "You're welcome! 😊 Stay healthy and take care."
        )


    # --------------------------------------------------------
    # Default response
    # --------------------------------------------------------

    return (
        "I can help with hospital services, doctor search, "
        "appointments, symptoms, departments, and general "
        "health information. Please describe your question "
        "in a little more detail."
    )