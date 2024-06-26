import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    try:
        # Load Firebase credentials from Streamlit secrets
        firebase_config = {
            "type": st.secrets["firebase"]["type"],
            "project_id": st.secrets["firebase"]["project_id"],
            "private_key_id": st.secrets["firebase"]["private_key_id"],
            "private_key": st.secrets["firebase"]["private_key"].replace('\\n', '\n'),
            "client_email": st.secrets["firebase"]["client_email"],
            "client_id": st.secrets["firebase"]["client_id"],
            "auth_uri": st.secrets["firebase"]["auth_uri"],
            "token_uri": st.secrets["firebase"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
        }

        # Initialize Firebase Admin SDK
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)

    except KeyError as e:
        st.error(f"Missing key in secrets configuration: {e}")
    except ValueError as e:
        st.error(f"Error initializing Firebase: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.stop()

db = firestore.client()
