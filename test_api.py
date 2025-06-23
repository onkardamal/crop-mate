import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_crops_list():
    print("\nTesting /api/crops endpoint...")
    response = requests.get(f'{BASE_URL}/api/crops')
    print(f"Status Code: {response.status_code}")
    print("Response:", response.json())
    return response.json()

def test_crop_details(crop_name):
    print(f"\nTesting /api/crops/{crop_name} endpoint...")
    response = requests.get(f'{BASE_URL}/api/crops/{crop_name}')
    print(f"Status Code: {response.status_code}")
    print("Response:", json.dumps(response.json(), indent=2))
    return response.json()

def verify_crop_data(crop_data):
    required_fields = [
        'name', 'description', 'growing_season', 'water_requirements',
        'soil_type', 'expected_yield', 'market_price', 'regions',
        'climate_suitability', 'soil_compatibility', 'profitability'
    ]
    
    print("\nVerifying crop data structure...")
    for field in required_fields:
        if field not in crop_data:
            print(f"❌ Missing field: {field}")
        else:
            print(f"✅ Found field: {field}")
            
    if 'climate_suitability' in crop_data:
        climate_fields = ['temperature', 'humidity', 'rainfall', 'sunlight', 'wind']
        for field in climate_fields:
            if field not in crop_data['climate_suitability']:
                print(f"❌ Missing climate field: {field}")
            else:
                print(f"✅ Found climate field: {field}")
                
    if 'soil_compatibility' in crop_data:
        soil_fields = ['ph_range', 'drainage', 'fertility']
        for field in soil_fields:
            if field not in crop_data['soil_compatibility']:
                print(f"❌ Missing soil field: {field}")
            else:
                print(f"✅ Found soil field: {field}")
                
    if 'profitability' in crop_data:
        profit_fields = ['investment', 'yield', 'market_price', 'profit_margin']
        for field in profit_fields:
            if field not in crop_data['profitability']:
                print(f"❌ Missing profitability field: {field}")
            else:
                print(f"✅ Found profitability field: {field}")

if __name__ == '__main__':
    # Test the crops list endpoint
    crops = test_crops_list()
    
    if crops and isinstance(crops, list):
        # Test the first crop in detail
        if len(crops) > 0:
            crop_data = test_crop_details(crops[0])
            verify_crop_data(crop_data) 