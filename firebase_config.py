import firebase_admin
from firebase_admin import credentials, firestore

# Pfad zu deinem Service Account Key JSON
cred = credentials.Certificate(r"https://github.com/DerNino/UMFYfix/blob/main/umfy-29ddb-firebase-adminsdk-gbags-5dbe02c8d5.json")

# Initialisiere die App mit den Service Account Credentials
firebase_admin.initialize_app(cred)

# Firestore-Datenbank initialisieren
db = firestore.client()
