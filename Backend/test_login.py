#!/usr/bin/env python3
import requests
import json

# Test login
response = requests.post(
    "http://localhost:8001/api/auth/login",
    json={"email": "admin@college.com", "password": "admin123"}
)

print(f"Status Code: {response.status_code}")
print(f"Response Text: {response.text}")
if response.status_code == 200:
    print(f"Response JSON: {json.dumps(response.json(), indent=2)}")
