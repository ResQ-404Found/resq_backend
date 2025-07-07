import firebase_admin
from firebase_admin import credentials
import os
import json

def init_firebase():
    with open("secrets/firebase_service_account.json") as f:
        cred_dict = json.load(f)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    print("[INFO] Firebase Admin SDK Initialized!")