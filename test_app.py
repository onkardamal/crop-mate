#!/usr/bin/env python3
"""
Test script for CropMate application
"""

import requests
import json
import time

def test_app():
    """Test the CropMate application"""
    base_url = "http://localhost:5000"
    
    print("🌱 Testing CropMate Application...")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Server is running successfully")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the application with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return False
    
    # Test 2: Test crop recommendation API
    try:
        test_data = {
            'Nitrogen': 50,
            'Phosporus': 50,
            'Potassium': 50,
            'Temperature': 25,
            'Humidity': 70,
            'pH': 6.5,
            'Rainfall': 100
        }
        
        response = requests.post(f"{base_url}/predict", data=test_data, timeout=10)
        if response.status_code == 200:
            print("✅ Crop recommendation API is working")
        else:
            print(f"❌ Crop recommendation API failed with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing crop recommendation: {e}")
    
    # Test 3: Test crops list API
    try:
        response = requests.get(f"{base_url}/api/crops", timeout=5)
        if response.status_code == 200:
            crops = response.json()
            print(f"✅ Crops API working - Found {len(crops)} crops")
        else:
            print(f"❌ Crops API failed with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing crops API: {e}")
    
    # Test 4: Test individual crop details API
    try:
        response = requests.get(f"{base_url}/api/crops/Rice", timeout=5)
        if response.status_code == 200:
            crop_data = response.json()
            print("✅ Individual crop details API is working")
        else:
            print(f"❌ Individual crop details API failed with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing crop details API: {e}")
    
    # Test 5: Test all routes
    routes_to_test = [
        "/recommend",
        "/compare", 
        "/profitability",
        "/calendar",
        "/practices",
        "/suitability",
        "/schemes",
        "/market",
        "/community"
    ]
    
    print("\n📋 Testing all routes:")
    for route in routes_to_test:
        try:
            response = requests.get(f"{base_url}{route}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {route} - OK")
            else:
                print(f"❌ {route} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {route} - Error: {e}")
    
    print("\n🎉 Testing completed!")
    print("=" * 50)
    print("If all tests passed, your CropMate application is working correctly!")
    print("You can now access it at: http://localhost:5000")
    
    return True

if __name__ == "__main__":
    test_app() 