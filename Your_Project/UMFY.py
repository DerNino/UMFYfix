import streamlit as st
import datetime
import json
from firebase_config import db
import os
from PIL import Image
import base64

# CSS-Styles für den Hintergrund und die Schriftfarbe
page_bg = """
<style>
.stApp {
    background-color: #392981;
    color: white;
}
div[data-testid="stText"] {
    color: white;
}
div[data-testid="stMarkdownContainer"] p {
    color: white;
}
h1, h2, h3, h4, h5, h6 {
    color: white;
}
button, .stButton > button {
    color: black !important;
}
.stButton > button {
    background-color: white;
}
</style>
"""

# Wende die CSS-Styles an
st.markdown(page_bg, unsafe_allow_html=True)

# Pfad zum Bild im selben Verzeichnis wie das Skript
IMAGE_PATH = os.path.join(os.path.dirname(__file__), "logo.png")

# Funktion, um ein Bild in Base64 umzuwandeln
def img_to_bytes(img):
    from io import BytesIO
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

# Funktion zum Laden von Fragen aus einer lokalen JSON-Datei im gleichen Verzeichnis
def load_questions():
    file_path = os.path.join(os.path.dirname(__file__), "fragen.json")
    try:
        with open(file_path, 'r') as file:
            questions_data = json.load(file)
            if isinstance(questions_data, dict) and "questions" in questions_data:
                return questions_data["questions"]
            else:
                st.error("Invalid JSON format: 'questions' key not found")
                return []
    except FileNotFoundError as e:
        st.error(f"Error: File not found: {e}")
        return []
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        return []
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return []

# Funktion, um die Frage des Tages zu erhalten
def get_question_of_the_day():
    questions = load_questions()
    if questions:
        today = datetime.date.today()
        return questions[today.day % len(questions)]  # Fragen täglich rotieren
    return "No questions available"

# Funktion zum Speichern von Antworten in Firebase
def save_response(response):
    today = datetime.date.today().strftime("%Y-%m-%d")
    doc_ref = db.collection('responses').document(today)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        data['responses'].append(response)
        doc_ref.set(data)
    else:
        doc_ref.set({'responses': [response]})

# Streamlit App
# Bild laden, Größe ändern und anzeigen
try:
    img = Image.open(IMAGE_PATH)
    img = img.resize((img.width // 2, img.height // 2))  # Bild auf ein Viertel der ursprünglichen Größe reduzieren
    img_str = img_to_bytes(img)
    # Bild zentrieren
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center;">
            <img src="data:image/png;base64,{img_str}" width="{img.width}" height="{img.height}">
        </div>
        """,
        unsafe_allow_html=True
    )
except Exception as e:
    st.error(f"Fehler beim Laden des Bildes: {e}")

st.title("Tägliche Umfrage")

question_of_the_day = get_question_of_the_day()
st.write("Frage des Tages:", question_of_the_day)

st.write("Bitte geben Sie Ihre Antwort ein:")
user_response = st.text_area("Ihre Antwort")

if st.button("Antwort senden"):
    if user_response:
        try:
            save_response(user_response)
            st.success("Ihre Antwort wurde gespeichert.")
        except Exception as e:
            st.error(f"Fehler beim Speichern der Antwort: {e}")
    else:
        st.error("Antwortfeld darf nicht leer sein.")

# Anzeigen der gespeicherten Antworten
if st.button("Antworten anzeigen"):
    today = datetime.date.today().strftime("%Y-%m-%d")
    doc_ref = db.collection('responses').document(today)
    doc = doc_ref.get()
    if doc.exists:  # 'exists' als Eigenschaft verwenden, nicht als Methode
        data = doc.to_dict()
        st.write("Heutige Antworten:")
        for idx, response in enumerate(data['responses']):
            st.write(f"{idx + 1}. {response}")
    else:
        st.write("Es gibt keine Antworten für heute.")
