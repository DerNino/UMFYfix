import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

# Load Firebase credentials from Streamlit secrets
firebase_config = st.secrets["firebase"]

# Initialize Firebase Admin SDK
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)

db = firestore.client()
