import streamlit as st
import datetime
import json
from firebase_config import db

# Function to save responses in Firebase
def save_response(question, response):
    today = datetime.date.today().strftime("%Y-%m-%d")
    doc_ref = db.collection('responses').document(today)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        if question in data['responses']:
            data['responses'][question].append(response)
        else:
            data['responses'][question] = [response]
        doc_ref.set(data)
    else:
        doc_ref.set({'responses': {question: [response]}})

# Load questions from fragen.json
def load_questions():
    with open('fragen.json', 'r') as file:
        questions = json.load(file)
    return questions

# Streamlit App
st.title("Antworten App")

st.write("Bitte beantworten Sie die folgenden Fragen:")

questions = load_questions()

responses = {}
for question in questions:
    response = st.text_area(f"{question}", key=question)
    responses[question] = response

if st.button("Antworten senden"):
    all_filled = all(response for response in responses.values())
    if all_filled:
        try:
            for question, response in responses.items():
                save_response(question, response)
            st.success("Ihre Antworten wurden gespeichert.")
        except Exception as e:
            st.error(f"Fehler beim Speichern der Antworten: {e}")
    else:
        st.error("Alle Antwortfelder müssen ausgefüllt sein.")

# Anzeigen der gespeicherten Antworten
if st.button("Antworten anzeigen"):
    today = datetime.date.today().strftime("%Y-%m-%d")
    doc_ref = db.collection('responses').document(today)
    doc = doc_ref.get()
    if doc.exists:  # Use 'exists' as a property, not a method
        data = doc.to_dict()
        st.write("Heutige Antworten:")
        for question, answers in data['responses'].items():
            st.write(f"**{question}**")
            for idx, response in enumerate(answers):
                st.write(f"{idx + 1}. {response}")
    else:
        st.write("Es gibt keine Antworten für heute.")
