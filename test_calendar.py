#!/usr/bin/env python3
"""
Test script for calendar functionality
"""

from app import app, get_calendar_data, get_crops_by_season, get_month_list_from_range

def test_calendar_data():
    """Test calendar data generation"""
    print("Testing calendar data generation...")
    data = get_calendar_data()
    print(f"✓ Generated calendar data for {len(data)} crops")
    
    # Test a few crops
    test_crops = ['Rice', 'Maize', 'Banana']
    for crop in test_crops:
        if crop in data:
            print(f"✓ {crop}: Sowing={len(data[crop]['sowing'])}, Growing={len(data[crop]['growing'])}, Harvesting={len(data[crop]['harvesting'])}")
        else:
            print(f"✗ {crop} not found in calendar data")

def test_seasonal_crops():
    """Test seasonal crop filtering"""
    print("\nTesting seasonal crop filtering...")
    seasons = ['kharif', 'rabi', 'zaid']
    for season in seasons:
        crops = get_crops_by_season(season)
        print(f"✓ {season.title()}: {len(crops)} crops - {crops[:3]}...")

def test_month_parsing():
    """Test month range parsing"""
    print("\nTesting month range parsing...")
    test_ranges = [
        "June-July",
        "Year-round", 
        "October-January",
        "March"
    ]
    for range_str in test_ranges:
        months = get_month_list_from_range(range_str)
        print(f"✓ '{range_str}' -> {months}")

def test_api_endpoints():
    """Test API endpoints"""
    print("\nTesting API endpoints...")
    with app.test_client() as client:
        # Test season endpoint
        response = client.get('/api/calendar/season/kharif')
        if response.status_code == 200:
            data = response.get_json()
            print(f"✓ Season API: {len(data.get('crops', []))} crops returned")
        else:
            print(f"✗ Season API failed with status {response.status_code}")
        
        # Test month endpoint
        response = client.get('/api/calendar/month/6')  # June
        if response.status_code == 200:
            data = response.get_json()
            print(f"✓ Month API: {len(data.get('crops', []))} crops returned")
        else:
            print(f"✗ Month API failed with status {response.status_code}")

if __name__ == "__main__":
    print("Calendar Functionality Test")
    print("=" * 40)
    
    test_calendar_data()
    test_seasonal_crops()
    test_month_parsing()
    test_api_endpoints()
    
    print("\n" + "=" * 40)
    print("Calendar functionality test completed!") 