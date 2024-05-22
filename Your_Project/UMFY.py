import streamlit as st
import datetime
import json
from firebase_config import db
import requests
from PIL import Image
from io import BytesIO

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
.stButton > button {
    color: white !important;
    background-color: black !important;
}
</style>
"""

# Wende die CSS-Styles an
st.markdown(page_bg, unsafe_allow_html=True)

# URL des Logos auf GitHub
logo_url = "https://raw.githubusercontent.com/IHR_GITHUB_BENUTZERNAME/my_project/main/logo.png"

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
def save_response(name, response):
    today = datetime.date.today().strftime("%Y-%m-%d")
    doc_ref = db.collection('responses').document(today)
    doc = doc_ref.get()
    response_data = {"name": name, "response": response}
    if doc.exists:
        data = doc.to_dict()
        if 'responses' in data:
            data['responses'].append(response_data)
        else:
            data['responses'] = [response_data]
        doc_ref.set(data)
    else:
        doc_ref.set({'responses': [response_data]})

# Streamlit App
# Bild von GitHub herunterladen und anzeigen
try:
    response = requests.get(logo_url)
    response.raise_for_status()  # Check if the request was successful
    img = Image.open(BytesIO(response.content))
    # Bildgröße auf ein Viertel der ursprünglichen Größe reduzieren
    width, height = img.size
    img = img.resize((width // 2, height // 2))
    # Bild in der Mitte anzeigen
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center;">
            <img src="data:image/png;base64,{img_to_bytes(img)}" width="{width // 2}" height="{height // 2}">
        </div>
        """,
        unsafe_allow_html=True
    )
except requests.exceptions.RequestException as e:
    st.error(f"Fehler beim Herunterladen des Bildes: {e}")
except Exception as e:
    st.error(f"Fehler beim Laden des Bildes: {e}")

# Funktion, um ein Bild in Base64 umzuwandeln
def img_to_bytes(img):
    from io import BytesIO
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

st.title("Tägliche Umfrage")

question_of_the_day = get_question_of_the_day()
st.write("Frage des Tages:", question_of_the_day)

st.write("Bitte geben Sie Ihren Namen und Ihre Antwort ein:")
user_name = st.text_input("Ihr Name")
user_response = st.text_area("Ihre Antwort")

if st.button("Antwort senden"):
    if user_name and user_response:
        try:
            save_response(user_name, user_response)
            st.success("Ihre Antwort wurde gespeichert.")
        except Exception as e:
            st.error(f"Fehler beim Speichern der Antwort: {e}")
    else:
        st.error("Name und Antwortfeld dürfen nicht leer sein.")

# Anzeigen der gespeicherten Antworten
if st.button("Antworten anzeigen"):
    today = datetime.date.today().strftime("%Y-%m-%d")
    doc_ref = db.collection('responses').document(today)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        if 'responses' in data:
            st.write("Heutige Antworten:")
            for idx, response in enumerate(data['responses']):
                try:
                    name = response.get('name', 'Unbekannt')
                    answer = response.get('response', 'Keine Antwort')
                    st.write(f"{idx + 1}. {name}: {answer}")
                except KeyError as e:
                    st.error(f"Fehler beim Abrufen der Antwort: {e}")
        else:
            st.write("Es gibt keine Antworten für heute.")
    else:
        st.write("Es gibt keine Antworten für heute.")
