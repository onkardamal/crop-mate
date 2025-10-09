"""
Location Detection Service for CropMate
Handles IP geolocation and reverse geocoding
"""

import requests
import json
from flask import request, jsonify
import logging

class LocationService:
    def __init__(self):
        self.ip_apis = [
            {
                'url': 'https://ipapi.co/json/',
                'parser': self._parse_ipapi_co
            },
            {
                'url': 'https://ipinfo.io/json',
                'parser': self._parse_ipinfo_io
            },
            {
                'url': 'https://www.geoplugin.net/json.gp',
                'parser': self._parse_geoplugin
            }
        ]
        
        self.reverse_geo_apis = [
            {
                'url': 'https://api.bigdatacloud.net/data/reverse-geocode-client',
                'parser': self._parse_bigdatacloud
            },
            {
                'url': 'https://api.opencagedata.com/geocode/v1/json',
                'parser': self._parse_opencage
            }
        ]

    def get_client_ip(self):
        """Extract client IP from request headers"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr

    def detect_location_by_ip(self, ip_address=None):
        """Detect location using IP address with multiple fallback APIs"""
        if not ip_address:
            ip_address = self.get_client_ip()
        
        for api in self.ip_apis:
            try:
                response = requests.get(api['url'], timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    location = api['parser'](data)
                    if location and location.get('city'):
                        logging.info(f"Location detected via {api['url']}: {location}")
                        return location
            except Exception as e:
                logging.warning(f"IP geolocation API {api['url']} failed: {e}")
                continue
        
        # Fallback to auto-detected location based on IP
        # Try to get more accurate location from IP
        try:
            # Use a more reliable IP geolocation service
            response = requests.get('https://ipapi.co/json/', timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('city') and data.get('region'):
                    return {
                        'city': data.get('city', 'Unknown'),
                        'state': data.get('region', 'Unknown'),
                        'country': data.get('country_name', 'India'),
                        'latitude': data.get('latitude'),
                        'longitude': data.get('longitude')
                    }
        except:
            pass
        
        # Final fallback - let user choose
        return {
            'city': 'Auto-detect',
            'state': 'Please select',
            'country': 'India',
            'latitude': None,
            'longitude': None,
            'auto_detect': True
        }

    def reverse_geocode(self, latitude, longitude):
        """Reverse geocode coordinates to location"""
        for api in self.reverse_geo_apis:
            try:
                if 'bigdatacloud' in api['url']:
                    url = f"{api['url']}?latitude={latitude}&longitude={longitude}&localityLanguage=en"
                    response = requests.get(url, timeout=5)
                elif 'opencage' in api['url']:
                    # Note: Requires API key for production use
                    url = f"{api['url']}?q={latitude}+{longitude}&key=YOUR_API_KEY"
                    response = requests.get(url, timeout=5)
                else:
                    continue
                
                if response.status_code == 200:
                    data = response.json()
                    location = api['parser'](data)
                    if location and location.get('city'):
                        logging.info(f"Reverse geocoding successful: {location}")
                        return location
            except Exception as e:
                logging.warning(f"Reverse geocoding API {api['url']} failed: {e}")
                continue
        
        # Fallback based on coordinates
        return self._get_location_by_coordinates(latitude, longitude)

    def _parse_ipapi_co(self, data):
        """Parse ipapi.co response"""
        return {
            'city': data.get('city'),
            'state': data.get('region'),
            'country': data.get('country_name'),
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'ip': data.get('ip')
        }

    def _parse_ipinfo_io(self, data):
        """Parse ipinfo.io response"""
        lat_lng = data.get('loc', '').split(',')
        return {
            'city': data.get('city'),
            'state': data.get('region'),
            'country': data.get('country'),
            'latitude': float(lat_lng[0]) if len(lat_lng) == 2 else None,
            'longitude': float(lat_lng[1]) if len(lat_lng) == 2 else None,
            'ip': data.get('ip')
        }

    def _parse_geoplugin(self, data):
        """Parse geoplugin.net response"""
        return {
            'city': data.get('geoplugin_city'),
            'state': data.get('geoplugin_region'),
            'country': data.get('geoplugin_countryName'),
            'latitude': float(data.get('geoplugin_latitude', 0)),
            'longitude': float(data.get('geoplugin_longitude', 0)),
            'ip': data.get('geoplugin_request')
        }

    def _parse_bigdatacloud(self, data):
        """Parse BigDataCloud reverse geocoding response"""
        return {
            'city': data.get('city') or data.get('locality'),
            'state': data.get('principalSubdivision'),
            'country': data.get('countryName'),
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude')
        }

    def _parse_opencage(self, data):
        """Parse OpenCage reverse geocoding response"""
        if data.get('results'):
            result = data['results'][0]
            components = result.get('components', {})
            return {
                'city': components.get('city') or components.get('town') or components.get('village'),
                'state': components.get('state'),
                'country': components.get('country'),
                'latitude': result.get('geometry', {}).get('lat'),
                'longitude': result.get('geometry', {}).get('lng')
            }
        return None

    def _get_location_by_coordinates(self, latitude, longitude):
        """Fallback location detection based on coordinates"""
        # Simple coordinate-based location detection for India
        if 6.0 <= latitude <= 37.0 and 68.0 <= longitude <= 97.0:
            # Major Indian cities by approximate coordinates
            cities = [
                {'city': 'Mumbai', 'state': 'Maharashtra', 'lat': 19.0760, 'lng': 72.8777},
                {'city': 'Delhi', 'state': 'Delhi', 'lat': 28.6139, 'lng': 77.2090},
                {'city': 'Bangalore', 'state': 'Karnataka', 'lat': 12.9716, 'lng': 77.5946},
                {'city': 'Kolkata', 'state': 'West Bengal', 'lat': 22.5726, 'lng': 88.3639},
                {'city': 'Chennai', 'state': 'Tamil Nadu', 'lat': 13.0827, 'lng': 80.2707},
                {'city': 'Hyderabad', 'state': 'Telangana', 'lat': 17.3850, 'lng': 78.4867},
                {'city': 'Pune', 'state': 'Maharashtra', 'lat': 18.5204, 'lng': 73.8567},
                {'city': 'Ahmedabad', 'state': 'Gujarat', 'lat': 23.0225, 'lng': 72.5714}
            ]
            
            # Find closest city
            min_distance = float('inf')
            closest_city = cities[0]
            
            for city in cities:
                distance = ((latitude - city['lat']) ** 2 + (longitude - city['lng']) ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    closest_city = city
            
            return {
                'city': closest_city['city'],
                'state': closest_city['state'],
                'country': 'India',
                'latitude': latitude,
                'longitude': longitude
            }
        
        # Try to get location from coordinates first
        try:
            response = requests.get(f'https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={latitude}&longitude={longitude}&localityLanguage=en', timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('city') or data.get('locality'):
                    return {
                        'city': data.get('city') or data.get('locality'),
                        'state': data.get('principalSubdivision'),
                        'country': data.get('countryName', 'India'),
                        'latitude': latitude,
                        'longitude': longitude
                    }
        except:
            pass
        
        # Fallback based on coordinates
        return {
            'city': 'Auto-detect',
            'state': 'Please select',
            'country': 'India',
            'latitude': latitude,
            'longitude': longitude,
            'auto_detect': True
        }

# Global instance
location_service = LocationService()
