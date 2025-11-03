#!/usr/bin/env python3
"""
Test script for onboarding endpoint
Tests the /api/links/{link_id}/generate-scripts endpoint
"""
import requests
import os
import sys

# Check if ANTHROPIC_API_KEY is set
anthropic_key = os.getenv('ANTHROPIC_API_KEY')
if not anthropic_key:
    print("❌ ANTHROPIC_API_KEY is not set!")
    print("Please run: export ANTHROPIC_API_KEY='your_key_here'")
    sys.exit(1)
else:
    print(f"✅ ANTHROPIC_API_KEY is set: {anthropic_key[:10]}...")

# Test endpoint
BASE_URL = "http://localhost:8001"
link_id = 1  # Change this to a real link ID from your database

print(f"\n🧪 Testing script generation for link {link_id}...")
print(f"Calling: POST {BASE_URL}/api/links/{link_id}/generate-scripts")

try:
    response = requests.post(f"{BASE_URL}/api/links/{link_id}/generate-scripts")
    
    print(f"\n📊 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Success!")
        print(f"\nResponse data:")
        print(f"  success: {data.get('success')}")
        print(f"  link_id: {data.get('link_id')}")
        print(f"  scripts count: {len(data.get('scripts', []))}")
        
        if data.get('scripts'):
            for i, script in enumerate(data['scripts'], 1):
                print(f"\n  Script {i}:")
                print(f"    word_count: {script.get('word_count')}")
                print(f"    text: {script.get('script')[:100]}...")
    else:
        print("❌ Error!")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print(f"❌ Could not connect to {BASE_URL}")
    print("Make sure the backend is running: cd voicetree/backend && python app.py")
except Exception as e:
    print(f"❌ Error: {e}")
