/**
 * Smart Location Detection for CropMate
 * Handles browser geolocation with IP-based fallback
 */

class LocationDetector {
    constructor() {
        this.currentCity = null;
        this.isDetecting = false;
        this.callbacks = [];
        this.fallbackAPIs = [
            'https://ipapi.co/json/',
            'https://ipinfo.io/json',
            'https://www.geoplugin.net/json.gp'
        ];
        
        // Load saved location from localStorage
        this.loadSavedLocation();
    }

    /**
     * Load saved location from localStorage
     */
    loadSavedLocation() {
        try {
            const saved = localStorage.getItem('cropmate_location');
            if (saved) {
                this.currentCity = JSON.parse(saved);
                this.updateLocationUI(this.currentCity);
                return true;
            }
        } catch (e) {
            console.log('No saved location found');
        }
        return false;
    }

    /**
     * Save location to localStorage
     */
    saveLocation(location) {
        try {
            localStorage.setItem('cropmate_location', JSON.stringify(location));
            return true;
        } catch (e) {
            console.error('Failed to save location:', e);
            return false;
        }
    }

    /**
     * Main detection method with fallback chain
     */
    async detectLocation() {
        // If we have a saved location, use it
        if (this.currentCity && !this.currentCity.auto_detect) {
            this.updateLocationUI(this.currentCity);
            this.notifyCallbacks(this.currentCity);
            return this.currentCity;
        }

        if (this.isDetecting) {
            return new Promise(resolve => {
                this.callbacks.push(resolve);
            });
        }

        this.isDetecting = true;
        this.showLoadingState();

        try {
            // Try browser geolocation first
            const location = await this.tryBrowserGeolocation();
            if (location) {
                this.currentCity = location;
                this.hideLoadingState();
                this.notifyCallbacks(location);
                return location;
            }
        } catch (error) {
            console.log('Browser geolocation failed:', error.message);
        }

        // Fallback to IP-based detection
        try {
            const location = await this.tryIPGeolocation();
            if (location) {
                this.currentCity = location;
                this.hideLoadingState();
                this.notifyCallbacks(location);
                return location;
            }
        } catch (error) {
            console.error('IP geolocation failed:', error);
        }

        // Final fallback - prompt user to select
        const defaultLocation = { 
            city: 'Auto-detect', 
            state: 'Please select', 
            country: 'India',
            auto_detect: true 
        };
        this.currentCity = defaultLocation;
        this.hideLoadingState();
        this.notifyCallbacks(defaultLocation);
        
        // Show location selector modal
        setTimeout(() => {
            const locationModal = document.getElementById('locationModal');
            if (locationModal) {
                const modal = new bootstrap.Modal(locationModal);
                modal.show();
            }
        }, 1000);
        
        return defaultLocation;
    }

    /**
     * Try browser geolocation with reverse geocoding
     */
    async tryBrowserGeolocation() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation not supported'));
                return;
            }

            const options = {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000 // 5 minutes
            };

            navigator.geolocation.getCurrentPosition(
                async (position) => {
                    try {
                        const { latitude, longitude } = position.coords;
                        const location = await this.reverseGeocode(latitude, longitude);
                        resolve(location);
                    } catch (error) {
                        reject(error);
                    }
                },
                (error) => {
                    reject(new Error(`Geolocation error: ${error.message}`));
                },
                options
            );
        });
    }

    /**
     * Try IP-based geolocation with multiple fallback APIs
     */
    async tryIPGeolocation() {
        for (const apiUrl of this.fallbackAPIs) {
            try {
                const response = await fetch(apiUrl, {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json',
                    }
                });

                if (!response.ok) continue;

                const data = await response.json();
                const location = this.parseIPLocationData(data, apiUrl);
                
                if (location && location.city) {
                    return location;
                }
            } catch (error) {
                console.log(`API ${apiUrl} failed:`, error.message);
                continue;
            }
        }
        throw new Error('All IP geolocation APIs failed');
    }

    /**
     * Parse location data from different IP APIs
     */
    parseIPLocationData(data, apiUrl) {
        if (apiUrl.includes('ipapi.co')) {
            return {
                city: data.city,
                state: data.region,
                country: data.country_name,
                latitude: data.latitude,
                longitude: data.longitude
            };
        } else if (apiUrl.includes('ipinfo.io')) {
            return {
                city: data.city,
                state: data.region,
                country: data.country,
                latitude: data.loc ? parseFloat(data.loc.split(',')[0]) : null,
                longitude: data.loc ? parseFloat(data.loc.split(',')[1]) : null
            };
        } else if (apiUrl.includes('geoplugin.net')) {
            return {
                city: data.geoplugin_city,
                state: data.geoplugin_region,
                country: data.geoplugin_countryName,
                latitude: parseFloat(data.geoplugin_latitude),
                longitude: parseFloat(data.geoplugin_longitude)
            };
        }
        return null;
    }

    /**
     * Reverse geocode coordinates to city
     */
    async reverseGeocode(lat, lng) {
        try {
            // Try our backend first
            const response = await fetch('/api/location/reverse-geocode', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ latitude: lat, longitude: lng })
            });

            if (response.ok) {
                const data = await response.json();
                return data.location;
            }
        } catch (error) {
            console.log('Backend reverse geocoding failed, trying external API');
        }

        // Fallback to external API
        try {
            const response = await fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lng}&localityLanguage=en`);
            const data = await response.json();
            
            return {
                city: data.city || data.locality,
                state: data.principalSubdivision,
                country: data.countryName,
                latitude: lat,
                longitude: lng
            };
        } catch (error) {
            throw new Error('Reverse geocoding failed');
        }
    }

    /**
     * Get current detected location
     */
    getCurrentLocation() {
        return this.currentCity;
    }

    /**
     * Set location manually (user override)
     */
    setLocation(location) {
        this.currentCity = location;
        this.saveLocation(location);
        this.notifyCallbacks(location);
        this.updateLocationUI(location);
    }

    /**
     * Show loading state
     */
    showLoadingState() {
        const indicator = document.getElementById('location-indicator');
        if (indicator) {
            indicator.innerHTML = '<i class="bi bi-geo-alt-fill text-primary"></i> Detecting location...';
            indicator.className = 'badge bg-primary';
        }
    }

    /**
     * Hide loading state
     */
    hideLoadingState() {
        const indicator = document.getElementById('location-indicator');
        if (indicator) {
            indicator.className = 'badge bg-success';
        }
    }

    /**
     * Update location UI
     */
    updateLocationUI(location) {
        const indicator = document.getElementById('location-indicator');
        if (indicator) {
            if (location.auto_detect) {
                indicator.innerHTML = `<i class="bi bi-geo-alt-fill"></i> ${location.city}`;
                indicator.className = 'badge bg-warning';
                indicator.title = 'Click to set your location';
            } else {
                indicator.innerHTML = `<i class="bi bi-geo-alt-fill"></i> ${location.city}, ${location.state}`;
                indicator.className = 'badge bg-success';
                indicator.title = 'Click to change location';
            }
        }

        // Update any location-dependent elements
        document.querySelectorAll('[data-location-city]').forEach(element => {
            element.textContent = location.city;
        });

        document.querySelectorAll('[data-location-state]').forEach(element => {
            element.textContent = location.state;
        });

        // Trigger custom event for other components
        window.dispatchEvent(new CustomEvent('locationDetected', {
            detail: { location }
        }));
    }

    /**
     * Notify all registered callbacks
     */
    notifyCallbacks(location) {
        this.callbacks.forEach(callback => callback(location));
        this.callbacks = [];
        this.isDetecting = false;
    }

    /**
     * Register callback for location detection
     */
    onLocationDetected(callback) {
        if (this.currentCity) {
            callback(this.currentCity);
        } else {
            this.callbacks.push(callback);
        }
    }
}

// Global instance
window.locationDetector = new LocationDetector();

// Auto-detect on page load
document.addEventListener('DOMContentLoaded', () => {
    window.locationDetector.detectLocation();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LocationDetector;
}
