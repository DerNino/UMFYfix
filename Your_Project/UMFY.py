import streamlit as st
import datetime
import requests
import json
from firebase_config import db

# Function to load questions from the GitHub file
@st.cache_data
def load_questions():
    url = "https://raw.githubusercontent.com/DerNino/your_project/main/fragen.json"
    response = requests.get(url)
    questions = response.json()["questions"]
    return questions

# Function to get the question of the day
def get_question_of_the_day():
    questions = load_questions()
    today = datetime.date.today()
    question_index = today.toordinal() % len(questions)
    return questions[question_index]

# Function to save responses in Firebase
def save_response(response, question):
    today = datetime.date.today().strftime("%Y-%m-%d")
    doc_ref = db.collection('responses').document(today)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        if 'responses' in data:
            data['responses'].append({"question": question, "response": response})
        else:
            data['responses'] = [{"question": question, "response": response}]
        doc_ref.set(data)
    else:
        doc_ref.set({'responses': [{"question": question, "response": response}]})

# Streamlit App
st.title("Antworten App")

# Get the question of the day
question_of_the_day = get_question_of_the_day()
st.write(f"Frage des Tages: {question_of_the_day}")

st.write("Bitte geben Sie Ihre Antwort ein:")
user_response = st.text_area("Ihre Antwort")

if st.button("Antwort senden"):
    if user_response:
        try:
            save_response(user_response, question_of_the_day)
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
    if doc.exists:
        data = doc.to_dict()
        st.write("Heutige Antworten:")
        for idx, item in enumerate(data['responses']):
            st.write(f"{idx + 1}. {item['response']} (Frage: {item['question']})")
    else:
        st.write("Es gibt keine Antworten für heute.")

