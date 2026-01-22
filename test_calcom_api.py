#!/usr/bin/env python3
"""Cal.com API 테스트 스크립트 (Query Parameter 방식)"""
import os
import requests
from dotenv import load_dotenv

load_dotenv('.env')

api_key = os.getenv('CALCOM_API_KEY')
base_url = os.getenv('CALCOM_BASE_URL', 'https://api.cal.com/v1')

if not api_key:
    print("CALCOM_API_KEY가 설정되지 않았습니다.")
    exit(1)

# Authorization 헤더 없이 Content-Type만 설정
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

print(f"Cal.com API 테스트 (v1Query Param)")
print(f"Base URL: {base_url}")
print(f"API Key: {api_key[:20]}...")
print("=" * 60)

# 1. 이벤트 타입 조회
print("\n1. 이벤트 타입 조회:")
try:
    response = requests.get(f"{base_url}/event-types?apiKey={api_key}", headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
    
    if response.status_code == 200:
        data = response.json()
        if 'event_types' in data:
            print(f"   성공! 이벤트 타입 개수: {len(data['event_types'])}")
except Exception as e:
    print(f"   에러: {e}")

# 2. 이벤트 타입 생성 시도
print("\n2. 이벤트 타입 생성 시도:")
try:
    timestamp = str(os.getpid())
    event_type_data = {
        "title": f"Test Task {timestamp}",
        "slug": f"test-task-{timestamp}",
        "length": 30,
        "description": "Test event type via API script"
    }
    response = requests.post(
        f"{base_url}/event-types?apiKey={api_key}",
        headers=headers,
        json=event_type_data,
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   에러: {e}")
