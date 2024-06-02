import streamlit as st
import datetime
import json
import os
import requests
from firebase_config import db
from PIL import Image
from io import BytesIO
import base64
import pytz
from requests.auth import HTTPBasicAuth

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
.st-expander {
    background-color: black !important;
}
.st-expander div[role="button"] {
    background-color: black !important;
}
</style>
"""

# Wende die CSS-Styles an
st.markdown(page_bg, unsafe_allow_html=True)

# URL des Logos auf GitHub
logo_url = "https://raw.githubusercontent.com/DerNino/UMFYfix/main/Your_Project/logo.png"

# Funktion, um ein Bild in Base64 umzuwandeln
def img_to_bytes(img):
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
def get_question_of_the_day(date):
    questions = load_questions()
    if questions:
        question_index = date.toordinal() % len(questions)
        return questions[question_index]  # Fragen täglich rotieren basierend auf dem Datum
    return "No questions available"

# Funktion zum Speichern von Antworten und der Frage in Firebase
def save_response_and_question(name, response):
    tz = pytz.timezone('Europe/Berlin')  # Europäische Zeitzone
    today_str = datetime.datetime.now(tz).strftime("%Y-%m-%d")
    question_of_the_day = get_question_of_the_day(datetime.date.today())
    doc_ref = db.collection('responses').document(today_str)
    response_data = {"name": name, "response": response, "comments": []}

    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        if 'responses' in data:
            data['responses'].append(response_data)
        else:
            data['responses'] = [response_data]
        if 'question' not in data:
            data['question'] = question_of_the_day
        doc_ref.set(data)
    else:
        doc_ref.set({'question': question_of_the_day, 'responses': [response_data]})

# Funktion zum Speichern von Kommentaren
def save_comment(date_str, response_index, name, comment):
    doc_ref = db.collection('responses').document(date_str)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        responses = data.get('responses', [])
        if 0 <= response_index < len(responses):
            if 'comments' not in responses[response_index]:
                responses[response_index]['comments'] = []
            responses[response_index]['comments'].append({"name": name, "comment": comment})
            doc_ref.set(data)
            return True
    return False

# Funktion zum Erstellen eines neuen Tages in Firebase
def create_new_day_entry():
    tz = pytz.timezone('Europe/Berlin')  # Europäische Zeitzone
    today = datetime.datetime.now(tz).date()
    today_str = today.strftime("%Y-%m-%d")
    doc_ref = db.collection('responses').document(today_str)

    doc = doc_ref.get()
    if not doc.exists:
        question_of_the_day = get_question_of_the_day(today)
        doc_ref.set({'question': question_of_the_day, 'responses': []})

# GitHub Konfiguration
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]
GITHUB_FILE_PATH = st.secrets["GITHUB_FILE_PATH"]
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"

def get_credentials():
    try:
        response = requests.get(GITHUB_API_URL, headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        })
        if response.status_code == 200:
            file_content = response.json()
            content = file_content['content']
            decoded_content = base64.b64decode(content).decode('utf-8')
            return json.loads(decoded_content)
        else:
            return {}
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Anmeldeinformationen: {e}")
        return {}

def save_credentials(credentials):
    try:
        encoded_content = base64.b64encode(json.dumps(credentials).encode('utf-8')).decode('utf-8')
        response = requests.put(GITHUB_API_URL, headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }, json={
            "message": "Update credentials",
            "content": encoded_content
        })
        if response.status_code == 200:
            st.success("Anmeldeinformationen erfolgreich gespeichert.")
        else:
            st.error("Fehler beim Speichern der Anmeldeinformationen.")
    except Exception as e:
        st.error(f"Fehler beim Speichern der Anmeldeinformationen: {e}")

credentials = get_credentials()

st.sidebar.title("Login/Registrierung")
username = st.sidebar.text_input("Nutzername")
password = st.sidebar.text_input("Passwort", type="password")
login_button = st.sidebar.button("Einloggen")
register_button = st.sidebar.button("Registrieren")

if register_button:
    if username in credentials:
        st.sidebar.error("Nutzername existiert bereits.")
    else:
        credentials[username] = password
        save_credentials(credentials)

if login_button:
    if username in credentials and credentials[username] == password:
        st.sidebar.success("Erfolgreich eingeloggt!")
        st.session_state["user"] = username
    else:
        st.sidebar.error("Ungültige Anmeldeinformationen.")

if "user" in st.session_state:
    st.write(f"Eingeloggt als: {st.session_state['user']}")

    st.title("Tägliche Umfrage")

    # Sicherstellen, dass ein neuer Tag in Firebase erstellt wird
    create_new_day_entry()

    # Frage des Tages basierend auf dem aktuellen Datum
    question_of_the_day = get_question_of_the_day(datetime.date.today())
    st.write("Frage des Tages:", question_of_the_day)

    st.write("Bitte geben Sie Ihren Namen und Ihre Antwort ein:")
    user_name = st.text_input("Ihr Name")
    user_response = st.text_area("Ihre Antwort")

    if st.button("Antwort senden"):
        if user_name and user_response:
            try:
                save_response_and_question(user_name, user_response)
                st.balloons()  # Ballons anzeigen, wenn eine Antwort erfolgreich gesendet wurde
                st.success("Ihre Antwort wurde gespeichert.")
            except Exception as e:
                st.error(f"Fehler beim Speichern der Antwort: {e}")
        else:
            st.error("Name und Antwortfeld dürfen nicht leer sein.")

    # Kalender zur Auswahl eines Datums
    selected_date = st.date_input("Wählen Sie ein Datum aus", datetime.date.today())

    # Anzeigen der gespeicherten Antworten und der Frage für das ausgewählte Datum
    if st.button("Antworten für diesen Tag anzeigen") or st.session_state.get("responses_displayed", False):
        st.session_state["responses_displayed"] = True
        selected_date_str = selected_date.strftime("%Y-%m-%d")
        
        doc_ref = db.collection('responses').document(selected_date_str)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            question_for_selected_date = data.get('question', 'Keine Frage gefunden')
            
            st.write(f"Frage für den {selected_date_str}: {question_for_selected_date}")
            
            if 'responses' in data:
                st.write(f"Antworten vom {selected_date_str}:")
                for idx, response in enumerate(data['responses']):
                    try:
                        name = response.get('name', 'Unbekannt')
                        answer = response.get('response', 'Keine Antwort')
                        st.write(f"{idx + 1}. {name}: {answer}")
                        
                        # Kommentare anzeigen
                        comments = response.get('comments', [])
                        if comments:
                            st.write("Kommentare:")
                            for comment in comments:
                                st.write(f"- {comment['name']}: {comment['comment']}")

                        # Kommentarformular anzeigen
                        comment_key = f"comment_{selected_date_str}_{idx}"
                        if comment_key not in st.session_state:
                            st.session_state[comment_key] = {"name": "", "comment": ""}
                        
                        with st.expander("Kommentieren", expanded=False):
                            st.session_state[comment_key]["name"] = st.text_input(f"Ihr Name (Kommentar) für Antwort {idx + 1}", value=st.session_state[comment_key]["name"], key=f"comment_name_{idx}")
                            st.session_state[comment_key]["comment"] = st.text_area(f"Ihr Kommentar für Antwort {idx + 1}", value=st.session_state[comment_key]["comment"], key=f"comment_text_{idx}")
                            if st.button("Veröffentlichen", key=f"comment_button_{idx}"):
                                comment_name = st.session_state[comment_key]["name"]
                                comment_text = st.session_state[comment_key]["comment"]
                                if comment_name and comment_text:
                                    if save_comment(selected_date_str, idx, comment_name, comment_text):
                                        st.success("Ihr Kommentar wurde gespeichert.")
                                        st.session_state[comment_key] = {"name": "", "comment": ""}
                                        st.experimental_rerun()  # Seite neu laden, um den Kommentar anzuzeigen
                                    else:
                                        st.error("Fehler beim Speichern des Kommentars.")
                                else:
                                    st.error("Name und Kommentar dürfen nicht leer sein.")
                    except KeyError as e:
                        st.error(f"Fehler beim Abrufen der Antwort: {e}")
            else:
                st.write(f"Es gibt keine Antworten für den {selected_date_str}.")
        else:
            st.write(f"Es gibt keine Antworten für den {selected_date_str}.")
else:
    st.write("Bitte melden Sie sich an, um eine Antwort zu senden.")
