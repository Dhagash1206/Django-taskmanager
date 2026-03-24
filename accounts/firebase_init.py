"""Lazy Firebase Admin init for verifying ID tokens."""
import json
import os

import firebase_admin
from firebase_admin import credentials


def get_firebase_app():
    if firebase_admin._apps:
        return firebase_admin.get_app()

    json_blob = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()

    if json_blob:
        info = json.loads(json_blob)
        cred = credentials.Certificate(info)
        return firebase_admin.initialize_app(cred)

    if path:
        cred = credentials.Certificate(path)
        return firebase_admin.initialize_app(cred)

    return None
