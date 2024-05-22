import firebase_admin
from firebase_admin import credentials, firestore

# Path to your local service account key file using raw string
cred = credentials.Certificate(r"C:\Users\perre\Documents\GitHub\UMFYfix\umfy-29ddb-firebase-adminsdk-gbags-2dda4d0a53.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
