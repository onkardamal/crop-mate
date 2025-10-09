#!/usr/bin/env python3
"""
Location Detection Integration Example for CropMate
Demonstrates how to integrate location detection into existing pages
"""

from flask import Flask, render_template, request, jsonify, session
import json

# Example integration for different pages
class LocationIntegration:
    
    @staticmethod
    def get_user_location():
        """Get user's current location from session or detect via IP"""
        # Check if location is stored in session
        user_location = session.get('user_location')
        if user_location:
            return user_location
        
        # Fallback to IP detection
        try:
            from location_service import location_service
            return location_service.detect_location_by_ip()
        except:
        return {
            'city': 'Auto-detect',
            'state': 'Please select',
            'country': 'India',
            'auto_detect': True
        }
    
    @staticmethod
    def enhance_recommendation_page():
        """Enhance crop recommendation with location data"""
        user_location = LocationIntegration.get_user_location()
        
        # Add location context to recommendation
        location_context = {
            'user_city': user_location.get('city'),
            'user_state': user_location.get('state'),
            'location_based_tips': [
                f"Recommendations optimized for {user_location.get('city')}, {user_location.get('state')}",
                f"Local climate conditions in {user_location.get('state')}",
                f"Regional market prices for {user_location.get('city')}"
            ]
        }
        
        return location_context
    
    @staticmethod
    def enhance_market_page():
        """Enhance market trends with location-specific data"""
        user_location = LocationIntegration.get_user_location()
        
        # Mock location-specific market data
        market_data = {
            'local_prices': {
                'rice': {'price': 2500, 'unit': 'per quintal', 'trend': '+5%'},
                'wheat': {'price': 2200, 'unit': 'per quintal', 'trend': '+2%'},
                'maize': {'price': 1800, 'unit': 'per quintal', 'trend': '-1%'}
            },
            'local_markets': [
                f"{user_location.get('city')} Wholesale Market",
                f"{user_location.get('state')} Agricultural Market",
                "Regional Mandi"
            ],
            'weather_impact': f"Weather conditions in {user_location.get('city')} affecting crop prices"
        }
        
        return market_data
    
    @staticmethod
    def enhance_calendar_page():
        """Enhance seasonal calendar with location-specific timing"""
        user_location = LocationIntegration.get_user_location()
        
        # Location-specific seasonal adjustments
        seasonal_adjustments = {
            'kharif_start': 'June',  # Adjust based on region
            'rabi_start': 'October',
            'zaid_start': 'March',
            'location_note': f"Timings adjusted for {user_location.get('state')} climate"
        }
        
        return seasonal_adjustments

# Example Flask routes with location integration
def create_location_enhanced_routes(app):
    """Add location-enhanced routes to Flask app"""
    
    @app.route('/recommend-enhanced')
    def recommend_enhanced():
        """Enhanced recommendation page with location context"""
        location_context = LocationIntegration.enhance_recommendation_page()
        return render_template('recommend.html', 
                             location_context=location_context,
                             user_location=LocationIntegration.get_user_location())
    
    @app.route('/market-enhanced')
    def market_enhanced():
        """Enhanced market page with location-specific data"""
        market_data = LocationIntegration.enhance_market_page()
        return render_template('market.html',
                             market_data=market_data,
                             user_location=LocationIntegration.get_user_location())
    
    @app.route('/calendar-enhanced')
    def calendar_enhanced():
        """Enhanced calendar with location-specific timing"""
        seasonal_data = LocationIntegration.enhance_calendar_page()
        return render_template('calendar.html',
                             seasonal_data=seasonal_data,
                             user_location=LocationIntegration.get_user_location())
    
    @app.route('/api/location/context')
    def get_location_context():
        """API endpoint to get location context for any page"""
        user_location = LocationIntegration.get_user_location()
        
        context = {
            'location': user_location,
            'recommendations': {
                'local_crops': ['Rice', 'Wheat', 'Maize'],  # Based on location
                'best_season': 'Kharif',
                'soil_type': 'Alluvial'  # Based on region
            },
            'market_info': {
                'local_mandi': f"{user_location.get('city')} Agricultural Market",
                'price_trend': 'Stable',
                'demand': 'High'
            },
            'weather_context': {
                'current_season': 'Monsoon',
                'temperature_range': '25-35°C',
                'humidity': 'High'
            }
        }
        
        return jsonify(context)

# JavaScript integration examples
JAVASCRIPT_INTEGRATION = """
// Example: Using location data in your existing JavaScript

// Wait for location detection
window.addEventListener('locationDetected', function(event) {
    const location = event.detail.location;
    console.log('Location detected:', location);
    
    // Update page elements with location data
    updateLocationSpecificContent(location);
});

function updateLocationSpecificContent(location) {
    // Update market prices section
    if (document.getElementById('market-prices')) {
        fetch(`/api/market/local/${location.city}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('market-prices').innerHTML = 
                    generateMarketPricesHTML(data, location);
            });
    }
    
    // Update seasonal calendar
    if (document.getElementById('seasonal-calendar')) {
        fetch(`/api/calendar/local/${location.state}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('seasonal-calendar').innerHTML = 
                    generateCalendarHTML(data, location);
            });
    }
    
    // Update crop recommendations
    if (document.getElementById('crop-recommendations')) {
        fetch(`/api/crops/suitable/${location.state}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('crop-recommendations').innerHTML = 
                    generateCropRecommendationsHTML(data, location);
            });
    }
}

// Example: Manual location override
function setCustomLocation(city, state) {
    const location = { city, state, country: 'India' };
    
    // Update location detector
    if (window.locationDetector) {
        window.locationDetector.setLocation(location);
    }
    
    // Save to backend
    fetch('/api/location/set', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ location })
    }).then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`Location set to ${city}, ${state}`, 'success');
        }
    });
}
"""

# HTML template integration examples
HTML_INTEGRATION_EXAMPLES = """
<!-- Example: Location-aware content in templates -->

<!-- Market page with location context -->
<div class="location-context">
    <h3>Market Trends for <span data-location-city>{{ user_location.city }}</span>, 
        <span data-location-state>{{ user_location.state }}</span></h3>
    <p class="text-muted">Prices updated for your local market</p>
</div>

<!-- Seasonal calendar with location-specific timing -->
<div class="seasonal-calendar">
    <h3>Farming Calendar for {{ user_location.state }}</h3>
    <div class="alert alert-info">
        <i class="bi bi-info-circle"></i>
        Calendar adjusted for {{ user_location.state }} climate conditions
    </div>
</div>

<!-- Crop recommendations with location context -->
<div class="crop-recommendations">
    <h3>Recommended Crops for {{ user_location.city }}</h3>
    <div class="location-tips">
        <ul>
            <li>Optimized for {{ user_location.state }} soil conditions</li>
            <li>Based on {{ user_location.city }} climate data</li>
            <li>Local market demand analysis</li>
        </ul>
    </div>
</div>

<!-- Location selector button -->
<button class="btn btn-outline-primary" onclick="showLocationModal()">
    <i class="bi bi-geo-alt"></i> Change Location
</button>
"""

# Usage instructions
USAGE_INSTRUCTIONS = """
# Location Detection Integration Guide

## 1. Basic Integration

Add to your Flask app:
```python
from location_service import location_service
from location_integration_example import LocationIntegration

# Get user location in any route
user_location = LocationIntegration.get_user_location()
```

## 2. Frontend Integration

Include in your templates:
```html
<script src="{{ url_for('static', filename='location-detector.js') }}"></script>
```

Listen for location events:
```javascript
window.addEventListener('locationDetected', function(event) {
    const location = event.detail.location;
    // Update your page with location data
});
```

## 3. API Endpoints

Available endpoints:
- GET /api/location/detect - Detect location via IP
- GET /api/location/current - Get current location
- POST /api/location/set - Set custom location
- POST /api/location/reverse-geocode - Convert coordinates to location

## 4. Testing

Run the test suite:
```bash
python test_location_detection.py
```

## 5. Customization

Override default behavior:
```python
# Custom fallback location
location_service.default_location = {
    'city': 'Your City',
    'state': 'Your State',
    'country': 'India'
}

# Custom IP APIs
location_service.ip_apis.append({
    'url': 'https://your-api.com/json',
    'parser': your_custom_parser
})
```
"""

if __name__ == "__main__":
    print(USAGE_INSTRUCTIONS)
