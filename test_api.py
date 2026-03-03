#!/usr/bin/env python3
import requests
import json

# Test login
login_data = {'email': 'student1@college.com', 'password': 'student123'}
login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)

if login_response.status_code == 200:
    print('✅ Login Successful')
    token = login_response.json()['access_token']
    print(f'Token obtained: {token[:30]}...')
    
    # Test dashboard
    headers = {'Authorization': f'Bearer {token}'}
    dashboard_response = requests.get('http://localhost:8000/api/student/dashboard', headers=headers)
    
    if dashboard_response.status_code == 200:
        print('✅ Dashboard API Working')
        data = dashboard_response.json()
        print(f'   Name: {data.get("name")}')
        print(f'   Department: {data.get("department")}')
        print(f'   Year: {data.get("current_year")}')
        print(f'   Batch: {data.get("batch_year")}')
        print(f'   Assignments: {len(data.get("assignments", []))}')
        print(f'   Quizzes: {len(data.get("quizzes", []))}')
        print(f'   Attendance %: {data.get("attendance", {}).get("attendance_percentage")}')
    else:
        print(f'❌ Dashboard Error: {dashboard_response.status_code}')
        print(dashboard_response.text[:500])
else:
    print(f'❌ Login Failed: {login_response.status_code}')
    print(login_response.text[:500])
