import streamlit as st
import datetime
import json
from firebase_config import db

# Function to load questions from a local JSON file
def load_questions():
    file_path = "Your_Project/fragen.json"  # Replace with the actual file path
    try:
        with open(file_path, 'r') as file:
            questions = json.load(file)
            return questions["questions"]
    except FileNotFoundError as e:
        st.error(f"Error: File not found: {e}")
        return []
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        return []
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return []

# Function to get the question of the day
def get_question_of_the_day():
    questions = load_questions()
    if questions:
        today = datetime.date.today()
        return questions[today.day % len(questions)]  # Rotate questions daily
    return "No questions available"

# Function to save responses in Firebase
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
st.title("Antworten App")

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
    if doc.exists:  # Use 'exists' as a property, not a method
        data = doc.to_dict()
        st.write("Heutige Antworten:")
        for idx, response in enumerate(data['responses']):
            st.write(f"{idx + 1}. {response}")
    else:
        st.write("Es gibt keine Antworten für heute.")
