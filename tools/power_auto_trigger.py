import requests

# Power Automate flow HTTP endpoint
url = "https://default063f4e7bf4554b2d8f4d6293b5d4ac.0f.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/ad2242f623924f4c823f7ae5655553c6/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=G9NpcbQ74Nds7Or8ct7oQxDfd3WJWMgtZdnIR5P8nnY"

# Optional: Payload data to send to your flow
payload = {
    "refresh": True
}

# Optional: Custom headers (if needed)
headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print("Status code:", response.status_code)
print("Response text:", response.text)