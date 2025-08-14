#!/usr/bin/env python3
"""
Simple test script to verify the Flask application works correctly.
"""

import requests
import time
import sys

def test_flask_app():
    """Test the Flask application endpoints."""
    
    base_url = "http://localhost:5000"
    
    print("🚀 Testing Flask Application...")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        print("1. Testing server connectivity...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Server is running successfully!")
        else:
            print(f"   ❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Could not connect to server. Make sure the Flask app is running.")
        print("   💡 Run: python app.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Test tasks API
    try:
        print("2. Testing tasks API...")
        response = requests.get(f"{base_url}/api/tasks")
        if response.status_code == 200:
            tasks = response.json()
            print(f"   ✅ Tasks API working! Found {len(tasks)} tasks")
            for task in tasks:
                print(f"      - {task['title']} ({'Completed' if task['completed'] else 'Pending'})")
        else:
            print(f"   ❌ Tasks API returned status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing tasks API: {e}")
    
    # Test 3: Test weather API
    try:
        print("3. Testing weather API...")
        response = requests.get(f"{base_url}/api/weather")
        if response.status_code == 200:
            weather = response.json()
            print(f"   ✅ Weather API working!")
            print(f"      - Location: {weather.get('location', 'N/A')}")
            print(f"      - Temperature: {weather.get('temperature', 'N/A')}")
            print(f"      - Condition: {weather.get('condition', 'N/A')}")
        else:
            print(f"   ❌ Weather API returned status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing weather API: {e}")
    
    # Test 4: Test adding a task
    try:
        print("4. Testing task creation...")
        new_task = {"title": "Test task from script"}
        response = requests.post(f"{base_url}/api/tasks", json=new_task)
        if response.status_code == 201:
            task = response.json()
            print(f"   ✅ Task created successfully! ID: {task['id']}")
        else:
            print(f"   ❌ Task creation failed with status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error creating task: {e}")
    
    print("=" * 50)
    print("🎉 Testing completed!")
    print(f"🌐 Open your browser and go to: {base_url}")
    print("📖 Check the README.md file for more information")
    
    return True

if __name__ == "__main__":
    # Wait a moment for the server to start if it's not running
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    success = test_flask_app()
    sys.exit(0 if success else 1)
