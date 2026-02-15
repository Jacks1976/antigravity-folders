#!/usr/bin/env python3
import requests
import json

BASE_URL = 'http://localhost:8000'

print('=== TESTE DE ENDPOINTS ===\n')

# 1. Test /health
print('1. Testing /health')
try:
    r = requests.get(f'{BASE_URL}/health')
    print(f'   Status: {r.status_code}')
    print(f'   Response: {r.json()}\n')
except Exception as e:
    print(f'   ERROR: {e}\n')

# 2. Test GET /events (sem token)
print('2. Testing GET /events (sem autenticação)')
try:
    r = requests.get(f'{BASE_URL}/events')
    print(f'   Status: {r.status_code}')
    data = r.json()
    print(f'   Ok: {data.get("ok")}')
    if data.get('data'):
        print(f'   Results count: {len(data.get("data", {}).get("results", []))}')
    print(f'   Error: {data.get("error_key")}\n')
except Exception as e:
    print(f'   ERROR: {str(e)}\n')

# 3. Test GET /announcements/feed (sem token)
print('3. Testing GET /announcements/feed (sem autenticação)')
try:
    r = requests.get(f'{BASE_URL}/announcements/feed')
    print(f'   Status: {r.status_code}')
    data = r.json()
    print(f'   Ok: {data.get("ok")}')
    print(f'   Error: {data.get("error_key")}\n')
except Exception as e:
    print(f'   ERROR: {str(e)}\n')

# 4. Test GET /members/directory (sem token)
print('4. Testing GET /members/directory (sem autenticação)')
try:
    r = requests.get(f'{BASE_URL}/members/directory')
    print(f'   Status: {r.status_code}')
    data = r.json()
    print(f'   Ok: {data.get("ok")}')
    print(f'   Error Key: {data.get("error_key")}\n')
except Exception as e:
    print(f'   ERROR: {str(e)}\n')

print('=== FIM ===')
