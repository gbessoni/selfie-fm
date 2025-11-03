#!/usr/bin/env python3
"""
Test audio generation flow to identify errors
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_audio_generation():
    """Test the complete audio generation flow"""
    
    print("=" * 60)
    print("Testing Audio Generation Flow")
    print("=" * 60)
    
    # Step 1: Get links for user
    print("\n1. Getting links for user jtxcode...")
    response = requests.get(f"{BASE_URL}/api/users/jtxcode/links")
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   ERROR: {response.text}")
        return
    
    links = response.json()
    print(f"   Found {len(links)} links")
    
    if not links:
        print("   No links found!")
        return
    
    link = links[0]
    link_id = link['id']
    print(f"   Using link: {link['title']} (ID: {link_id})")
    print(f"   Current voice_message_audio: {link.get('voice_message_audio', 'None')}")
    
    # Step 2: Generate scripts
    print(f"\n2. Generating scripts for link {link_id}...")
    response = requests.post(f"{BASE_URL}/api/links/{link_id}/generate-scripts")
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   ERROR: {response.text}")
        return
    
    data = response.json()
    scripts = data.get('scripts', [])
    print(f"   Generated {len(scripts)} scripts")
    
    if not scripts:
        print("   No scripts generated!")
        return
    
    # Step 3: Select a script
    print(f"\n3. Selecting first script for link {link_id}...")
    script = scripts[0]['script']
    print(f"   Script text: {script[:100]}...")
    
    response = requests.post(
        f"{BASE_URL}/api/links/{link_id}/select-script",
        json={"script": script, "script_index": 0}
    )
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   ERROR: {response.text}")
        return
    
    print("   ✓ Script selected")
    
    # Step 4: Generate audio
    print(f"\n4. Generating audio for link {link_id}...")
    response = requests.post(f"{BASE_URL}/api/links/{link_id}/generate-audio")
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   ERROR: {response.text}")
        print(f"   Response content: {response.content}")
        return
    
    audio_data = response.json()
    print(f"   ✓ Audio generated!")
    print(f"   Audio path: {audio_data.get('audio_path')}")
    
    # Step 5: Verify in database
    print(f"\n5. Verifying link was updated...")
    response = requests.get(f"{BASE_URL}/api/users/jtxcode/links")
    links = response.json()
    updated_link = next((l for l in links if l['id'] == link_id), None)
    
    if updated_link:
        print(f"   voice_message_audio: {updated_link.get('voice_message_audio')}")
        print(f"   voice_message_text: {updated_link.get('voice_message_text', 'None')[:50]}...")
        
        if updated_link.get('voice_message_audio'):
            print("\n✅ SUCCESS! Audio generation completed and saved to database")
        else:
            print("\n❌ FAILED! Audio not saved to database")
    else:
        print("   ❌ Could not find link in response")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_audio_generation()
