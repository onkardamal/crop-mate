import requests

BASE_URL = 'http://127.0.0.1:5000'

def test_crops_list():
    url = f'{BASE_URL}/api/crops'
    resp = requests.get(url)
    print('GET /api/crops:', resp.status_code)
    print(resp.json())
    return resp.json()

def test_crop_details(crop_name):
    url = f'{BASE_URL}/api/crops/{crop_name}'
    resp = requests.get(url)
    print(f'GET /api/crops/{crop_name}:', resp.status_code)
    print(resp.json())
    return resp.json()

if __name__ == '__main__':
    crops = test_crops_list()
    if crops and isinstance(crops, list):
        for crop in crops[:3]:  # Test first 3 crops
            test_crop_details(crop) 