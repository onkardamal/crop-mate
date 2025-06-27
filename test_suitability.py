from app import app

def test_api_endpoints():
    with app.test_client() as client:
        # Test states API
        response = client.get('/api/states')
        print(f"States API: {response.status_code}")
        if response.status_code == 200:
            states = response.get_json()
            print(f"Number of states: {len(states)}")
            print(f"Sample states: {states[:3]}")
        
        # Test suitability API
        response = client.get('/api/suitability/Karnataka')
        print(f"\nSuitability API: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"State: {data.get('state')}")
            print(f"Number of suitable crops: {len(data.get('suitable_crops', []))}")
            if data.get('suitable_crops'):
                print(f"Top crop: {data['suitable_crops'][0]['crop_name']} - {data['suitable_crops'][0]['suitability_score']}%")
        
        # Test detailed crop analysis
        response = client.get('/api/suitability/crop/Rice/Karnataka')
        print(f"\nDetailed Analysis API: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            analysis = data.get('suitability_analysis', {})
            print(f"Suitability score: {analysis.get('suitability_score')}")
            print(f"Recommendations: {analysis.get('recommendations', [])}")

if __name__ == "__main__":
    test_api_endpoints() 