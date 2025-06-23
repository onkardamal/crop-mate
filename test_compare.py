#!/usr/bin/env python3
"""
Test script specifically for CropMate comparison functionality
"""

import requests
import json

def test_crop_comparison():
    """Test the crop comparison functionality"""
    base_url = "http://localhost:5000"
    
    print("🌱 Testing CropMate Comparison Functionality...")
    print("=" * 60)
    
    # Test 1: Check if crops API is working
    try:
        response = requests.get(f"{base_url}/api/crops", timeout=5)
        if response.status_code == 200:
            crops = response.json()
            print(f"✅ Crops API working - Found {len(crops)} crops")
            print(f"   Available crops: {', '.join(crops[:5])}...")
        else:
            print(f"❌ Crops API failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing crops API: {e}")
        return False
    
    # Test 2: Test individual crop details API
    test_crops = ["Rice", "Maize", "Apple"]
    for crop in test_crops:
        try:
            response = requests.get(f"{base_url}/api/crops/{crop}", timeout=5)
            if response.status_code == 200:
                crop_data = response.json()
                print(f"✅ {crop} details API working")
                print(f"   - Description: {crop_data.get('description', 'N/A')[:50]}...")
                print(f"   - Regions: {len(crop_data.get('regions', []))} regions")
                print(f"   - Climate data: {len(crop_data.get('climate_suitability', {}))} factors")
            else:
                print(f"❌ {crop} details API failed with status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing {crop} details: {e}")
    
    # Test 3: Test compare page loads
    try:
        response = requests.get(f"{base_url}/compare", timeout=5)
        if response.status_code == 200:
            print("✅ Compare page loads successfully")
        else:
            print(f"❌ Compare page failed with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing compare page: {e}")
    
    # Test 4: Test specific crop combinations
    test_combinations = [
        ("Rice", "Maize"),
        ("Apple", "Banana"),
        ("Cotton", "Jute")
    ]
    
    print("\n🔍 Testing specific crop combinations:")
    for crop1, crop2 in test_combinations:
        try:
            response1 = requests.get(f"{base_url}/api/crops/{crop1}", timeout=5)
            response2 = requests.get(f"{base_url}/api/crops/{crop2}", timeout=5)
            
            if response1.status_code == 200 and response2.status_code == 200:
                data1 = response1.json()
                data2 = response2.json()
                print(f"✅ {crop1} vs {crop2}: Both crops have data")
                print(f"   - {crop1}: {len(data1.get('regions', []))} regions")
                print(f"   - {crop2}: {len(data2.get('regions', []))} regions")
            else:
                print(f"❌ {crop1} vs {crop2}: Failed to get data")
        except Exception as e:
            print(f"❌ Error testing {crop1} vs {crop2}: {e}")
    
    print("\n🎉 Comparison functionality testing completed!")
    print("=" * 60)
    print("If all tests passed, the comparison feature should work correctly.")
    print("If there are issues, check the browser console for JavaScript errors.")
    
    return True

if __name__ == "__main__":
    test_crop_comparison() 