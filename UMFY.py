import streamlit as st
import datetime
from firebase_config import db

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

st.write("Bitte geben Sie Ihre Antwort ein:")
user_response = st.text_area("Ihre Antwort")

if st.button("Antwort senden"):
    if user_response:
        save_response(user_response)
        st.success("Ihre Antwort wurde gespeichert.")
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
        for idx, response in enumerate(data['responses']):
            st.write(f"{idx + 1}. {response}")
    else:
        st.write("Es gibt keine Antworten für heute.")

