import streamlit as st
import datetime
import json
import os
from firebase_config import db
import requests
from PIL import Image
from io import BytesIO
import base64
import pytz

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
.css-1d391kg {
    background-color: #392980 !important;
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

# Funktion zum Registrieren eines neuen Benutzers
def register_user(username, password):
    user_ref = db.collection('users').document(username)
    if user_ref.get().exists:
        st.sidebar.error("Benutzername bereits vergeben")
        return False
    else:
        user_ref.set({"password": password})
        st.sidebar.success("Benutzer erfolgreich registriert")
        return True

# Funktion zum Anmelden eines Benutzers
def login_user(username, password):
    user_ref = db.collection('users').document(username)
    user_doc = user_ref.get()
    if user_doc.exists and user_doc.to_dict().get("password") == password:
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        return True
    else:
        st.sidebar.error("Ungültiger Benutzername oder Passwort")
        return False

# Streamlit App
# Bild von GitHub herunterladen und anzeigen
try:
    response = requests.get(logo_url)
    response.raise_for_status()  # Check if the request was successful
    img = Image.open(BytesIO(response.content))
    # Bildgröße auf ein Viertel der ursprünglichen Größe reduzieren
    width, height = img.size
    img = img.resize((width // 2, height // 2))
    # Bild in Base64 umwandeln
    img_str = img_to_bytes(img)
    # Bild in der Mitte anzeigen
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center;">
            <img src="data:image/png;base64,{img_str}" width="{width // 2}" height="{height // 2}">
        </div>
        """,
        unsafe_allow_html=True
    )
except requests.exceptions.RequestException as e:
    st.error(f"Fehler beim Herunterladen des Bildes: {e}")
except Exception as e:
    st.error(f"Fehler beim Laden des Bildes: {e}")

st.title("Tägliche Umfrage")

# Nur fortfahren, wenn der Benutzer eingeloggt ist
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    with st.sidebar:
        st.subheader("Willkommen! Bitte wählen Sie:")
        option = st.selectbox("Option auswählen", ["Anmelden", "Registrieren"])

        if option == "Registrieren":
            st.subheader("Registrierung")
            reg_username = st.text_input("Benutzername (Registrierung)")
            reg_password = st.text_input("Passwort (Registrierung)", type="password")
            if st.button("Registrieren"):
                if reg_username and reg_password:
                    if register_user(reg_username, reg_password):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = reg_username
                        st.experimental_rerun()
        elif option == "Anmelden":
            st.subheader("Anmeldung")
            login_username = st.text_input("Benutzername (Anmeldung)")
            login_password = st.text_input("Passwort (Anmeldung)", type="password")
            if st.button("Anmelden"):
                if login_username and login_password:
                    if login_user(login_username, login_password):
                        st.experimental_rerun()
else:
    st.write(f"Eingeloggt als: {st.session_state['username']}")
    with st.sidebar:
        if st.button("Abmelden"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ""
            st.experimental_rerun()

    # Sicherstellen, dass ein neuer Tag in Firebase erstellt wird
    create_new_day_entry()

    # Frage des Tages basierend auf dem aktuellen Datum
    question_of_the_day = get_question_of_the_day(datetime.date.today())
    st.write("Frage des Tages:", question_of_the_day)

    st.write("Bitte geben Sie Ihre Antwort ein:")
    user_response = st.text_area("Ihre Antwort")

    if st.button("Antwort senden"):
        if user_response:
            try:
                save_response_and_question(st.session_state['username'], user_response)
                st.balloons()  # Ballons anzeigen, wenn eine Antwort erfolgreich gesendet wurde
                st.success("Ihre Antwort wurde gespeichert.")
            except Exception as e:
                st.error(f"Fehler beim Speichern der Antwort: {e}")
        else:
            st.error("Antwortfeld darf nicht leer sein.")

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
                            st.session_state[comment_key] = {"comment": ""}

                        with st.expander("Kommentieren", expanded=False):
                            st.session_state[comment_key]["comment"] = st.text_area(f"Ihr Kommentar für Antwort {idx + 1}", value=st.session_state[comment_key]["comment"], key=f"comment_text_{idx}")
                            if st.button("Veröffentlichen", key=f"comment_button_{idx}"):
                                comment_name = st.session_state['username']
                                comment_text = st.session_state[comment_key]["comment"]
                                if comment_text:
                                    if save_comment(selected_date_str, idx, comment_name, comment_text):
                                        st.success("Ihr Kommentar wurde gespeichert.")
                                        st.session_state[comment_key] = {"comment": ""}
                                        st.experimental_rerun()  # Seite neu laden, um den Kommentar anzuzeigen
                                    else:
                                        st.error("Fehler beim Speichern des Kommentars.")
                                else:
                                    st.error("Kommentar darf nicht leer sein.")
                    except KeyError as e:
                        st.error(f"Fehler beim Abrufen der Antwort: {e}")
            else:
                st.write(f"Es gibt keine Antworten für den {selected_date_str}.")
        else:
            st.write(f"Es gibt keine Antworten für den {selected_date_str}.")
