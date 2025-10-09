#!/usr/bin/env python3
"""
Test script for location detection system
Tests both IP geolocation and reverse geocoding functionality
"""

import requests
import json
import sys
from location_service import location_service

def test_ip_geolocation():
    """Test IP-based geolocation"""
    print("🌍 Testing IP Geolocation...")
    try:
        location = location_service.detect_location_by_ip()
        print(f"✅ IP Detection successful:")
        print(f"   City: {location.get('city', 'N/A')}")
        print(f"   State: {location.get('state', 'N/A')}")
        print(f"   Country: {location.get('country', 'N/A')}")
        if location.get('latitude'):
            print(f"   Coordinates: {location.get('latitude')}, {location.get('longitude')}")
        return True
    except Exception as e:
        print(f"❌ IP Detection failed: {e}")
        return False

def test_reverse_geocoding():
    """Test reverse geocoding with known coordinates"""
    print("\n🗺️ Testing Reverse Geocoding...")
    
    # Test coordinates for major Indian cities
    test_coordinates = [
        {"lat": 28.6139, "lng": 77.2090, "expected_city": "Delhi"},
        {"lat": 19.0760, "lng": 72.8777, "expected_city": "Mumbai"},
        {"lat": 12.9716, "lng": 77.5946, "expected_city": "Bangalore"},
        {"lat": 22.5726, "lng": 88.3639, "expected_city": "Kolkata"}
    ]
    
    success_count = 0
    for coord in test_coordinates:
        try:
            location = location_service.reverse_geocode(coord["lat"], coord["lng"])
            print(f"✅ Reverse geocoding for {coord['lat']}, {coord['lng']}:")
            print(f"   Detected: {location.get('city', 'N/A')}, {location.get('state', 'N/A')}")
            print(f"   Expected: {coord['expected_city']}")
            success_count += 1
        except Exception as e:
            print(f"❌ Reverse geocoding failed for {coord['lat']}, {coord['lng']}: {e}")
    
    return success_count == len(test_coordinates)

def test_flask_endpoints():
    """Test Flask location endpoints"""
    print("\n🔗 Testing Flask Endpoints...")
    
    base_url = "http://localhost:5000"
    endpoints = [
        {"url": f"{base_url}/api/location/detect", "method": "GET"},
        {"url": f"{base_url}/api/location/current", "method": "GET"},
        {"url": f"{base_url}/api/location/reverse-geocode", "method": "POST", "data": {
            "latitude": 28.6139,
            "longitude": 77.2090
        }},
        {"url": f"{base_url}/api/location/set", "method": "POST", "data": {
            "location": {
                "city": "Test City",
                "state": "Test State",
                "country": "India"
            }
        }}
    ]
    
    success_count = 0
    for endpoint in endpoints:
        try:
            if endpoint["method"] == "GET":
                response = requests.get(endpoint["url"], timeout=10)
            else:
                response = requests.post(
                    endpoint["url"], 
                    json=endpoint.get("data", {}),
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint['method']} {endpoint['url']}: {data.get('success', 'Unknown')}")
                success_count += 1
            else:
                print(f"❌ {endpoint['method']} {endpoint['url']}: HTTP {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"⚠️  {endpoint['method']} {endpoint['url']}: Flask server not running")
        except Exception as e:
            print(f"❌ {endpoint['method']} {endpoint['url']}: {e}")
    
    return success_count == len(endpoints)

def test_location_parsing():
    """Test location data parsing from different APIs"""
    print("\n📊 Testing Location Data Parsing...")
    
    # Mock data from different APIs
    test_data = [
        {
            "name": "ipapi.co",
            "data": {
                "city": "Mumbai",
                "region": "Maharashtra",
                "country_name": "India",
                "latitude": 19.0760,
                "longitude": 72.8777,
                "ip": "192.168.1.1"
            },
            "parser": location_service._parse_ipapi_co
        },
        {
            "name": "ipinfo.io",
            "data": {
                "city": "Delhi",
                "region": "Delhi",
                "country": "IN",
                "loc": "28.6139,77.2090",
                "ip": "192.168.1.1"
            },
            "parser": location_service._parse_ipinfo_io
        },
        {
            "name": "geoplugin.net",
            "data": {
                "geoplugin_city": "Bangalore",
                "geoplugin_region": "Karnataka",
                "geoplugin_countryName": "India",
                "geoplugin_latitude": "12.9716",
                "geoplugin_longitude": "77.5946",
                "geoplugin_request": "192.168.1.1"
            },
            "parser": location_service._parse_geoplugin
        }
    ]
    
    success_count = 0
    for test in test_data:
        try:
            result = test["parser"](test["data"])
            if result and result.get("city"):
                print(f"✅ {test['name']} parsing successful:")
                print(f"   City: {result.get('city')}")
                print(f"   State: {result.get('state')}")
                print(f"   Country: {result.get('country')}")
                success_count += 1
            else:
                print(f"❌ {test['name']} parsing failed: No city found")
        except Exception as e:
            print(f"❌ {test['name']} parsing failed: {e}")
    
    return success_count == len(test_data)

def main():
    """Run all location detection tests"""
    print("🧪 CropMate Location Detection Test Suite")
    print("=" * 50)
    
    tests = [
        ("IP Geolocation", test_ip_geolocation),
        ("Reverse Geocoding", test_reverse_geocoding),
        ("Flask Endpoints", test_flask_endpoints),
        ("Data Parsing", test_location_parsing)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All location detection tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
