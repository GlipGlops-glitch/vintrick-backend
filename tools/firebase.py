import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

# Path to your service account key JSON
SERVICE_ACCOUNT_FILE = "serviceAccount.json"

# Your Firestore project ID
PROJECT_ID = "vintrick-291c6"   # <-- replace with your Firebase project ID

# Authenticate and get a token
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/datastore"]
)
auth_req = google.auth.transport.requests.Request()
credentials.refresh(auth_req)
token = credentials.token

# Upload data (create a document)
url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/projects"

# Data to upload
data = {
    "fields": {
        "name": {"stringValue": "Project 0"},
        "owner": {"stringValue": "Casey"},
        "active": {"booleanValue": True},
        "created": {"timestampValue": "2025-08-19T00:00:00Z"}
    }
}

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.status_code)
print(response.json())