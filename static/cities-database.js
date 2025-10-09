/**
 * Comprehensive Indian Cities Database for CropMate
 * Includes major cities, districts, and agricultural regions
 */

const INDIAN_CITIES = [
    // Maharashtra
    { city: 'Mumbai', state: 'Maharashtra', district: 'Mumbai', region: 'Konkan' },
    { city: 'Pune', state: 'Maharashtra', district: 'Pune', region: 'Western Maharashtra' },
    { city: 'Nagpur', state: 'Maharashtra', district: 'Nagpur', region: 'Vidarbha' },
    { city: 'Nashik', state: 'Maharashtra', district: 'Nashik', region: 'Northern Maharashtra' },
    { city: 'Aurangabad', state: 'Maharashtra', district: 'Aurangabad', region: 'Marathwada' },
    { city: 'Solapur', state: 'Maharashtra', district: 'Solapur', region: 'Western Maharashtra' },
    { city: 'Amravati', state: 'Maharashtra', district: 'Amravati', region: 'Vidarbha' },
    { city: 'Kolhapur', state: 'Maharashtra', district: 'Kolhapur', region: 'Western Maharashtra' },
    { city: 'Ichalkaranji', state: 'Maharashtra', district: 'Kolhapur', region: 'Western Maharashtra' },
    { city: 'Sangli', state: 'Maharashtra', district: 'Sangli', region: 'Western Maharashtra' },
    { city: 'Satara', state: 'Maharashtra', district: 'Satara', region: 'Western Maharashtra' },
    { city: 'Jalgaon', state: 'Maharashtra', district: 'Jalgaon', region: 'Northern Maharashtra' },
    { city: 'Akola', state: 'Maharashtra', district: 'Akola', region: 'Vidarbha' },
    { city: 'Latur', state: 'Maharashtra', district: 'Latur', region: 'Marathwada' },
    { city: 'Dhule', state: 'Maharashtra', district: 'Dhule', region: 'Northern Maharashtra' },
    { city: 'Nanded', state: 'Maharashtra', district: 'Nanded', region: 'Marathwada' },
    { city: 'Parbhani', state: 'Maharashtra', district: 'Parbhani', region: 'Marathwada' },
    { city: 'Bhusawal', state: 'Maharashtra', district: 'Jalgaon', region: 'Northern Maharashtra' },
    { city: 'Chandrapur', state: 'Maharashtra', district: 'Chandrapur', region: 'Vidarbha' },
    { city: 'Jalna', state: 'Maharashtra', district: 'Jalna', region: 'Marathwada' },

    // Karnataka
    { city: 'Bangalore', state: 'Karnataka', district: 'Bangalore Urban', region: 'South Karnataka' },
    { city: 'Mysore', state: 'Karnataka', district: 'Mysore', region: 'South Karnataka' },
    { city: 'Hubli', state: 'Karnataka', district: 'Dharwad', region: 'North Karnataka' },
    { city: 'Mangalore', state: 'Karnataka', district: 'Dakshina Kannada', region: 'Coastal Karnataka' },
    { city: 'Belgaum', state: 'Karnataka', district: 'Belagavi', region: 'North Karnataka' },
    { city: 'Gulbarga', state: 'Karnataka', district: 'Kalaburagi', region: 'North Karnataka' },
    { city: 'Davanagere', state: 'Karnataka', district: 'Davanagere', region: 'Central Karnataka' },
    { city: 'Bellary', state: 'Karnataka', district: 'Ballari', region: 'North Karnataka' },
    { city: 'Bijapur', state: 'Karnataka', district: 'Vijayapura', region: 'North Karnataka' },
    { city: 'Shimoga', state: 'Karnataka', district: 'Shivamogga', region: 'Central Karnataka' },

    // Tamil Nadu
    { city: 'Chennai', state: 'Tamil Nadu', district: 'Chennai', region: 'Northern Tamil Nadu' },
    { city: 'Coimbatore', state: 'Tamil Nadu', district: 'Coimbatore', region: 'Western Tamil Nadu' },
    { city: 'Madurai', state: 'Tamil Nadu', district: 'Madurai', region: 'Southern Tamil Nadu' },
    { city: 'Tiruchirapalli', state: 'Tamil Nadu', district: 'Tiruchirappalli', region: 'Central Tamil Nadu' },
    { city: 'Salem', state: 'Tamil Nadu', district: 'Salem', region: 'Western Tamil Nadu' },
    { city: 'Tirunelveli', state: 'Tamil Nadu', district: 'Tirunelveli', region: 'Southern Tamil Nadu' },
    { city: 'Tiruppur', state: 'Tamil Nadu', district: 'Tiruppur', region: 'Western Tamil Nadu' },
    { city: 'Erode', state: 'Tamil Nadu', district: 'Erode', region: 'Western Tamil Nadu' },
    { city: 'Vellore', state: 'Tamil Nadu', district: 'Vellore', region: 'Northern Tamil Nadu' },
    { city: 'Thoothukudi', state: 'Tamil Nadu', district: 'Thoothukudi', region: 'Southern Tamil Nadu' },

    // Gujarat
    { city: 'Ahmedabad', state: 'Gujarat', district: 'Ahmedabad', region: 'Central Gujarat' },
    { city: 'Surat', state: 'Gujarat', district: 'Surat', region: 'South Gujarat' },
    { city: 'Vadodara', state: 'Gujarat', district: 'Vadodara', region: 'Central Gujarat' },
    { city: 'Rajkot', state: 'Gujarat', district: 'Rajkot', region: 'Saurashtra' },
    { city: 'Bhavnagar', state: 'Gujarat', district: 'Bhavnagar', region: 'Saurashtra' },
    { city: 'Jamnagar', state: 'Gujarat', district: 'Jamnagar', region: 'Saurashtra' },
    { city: 'Junagadh', state: 'Gujarat', district: 'Junagadh', region: 'Saurashtra' },
    { city: 'Gandhinagar', state: 'Gujarat', district: 'Gandhinagar', region: 'Central Gujarat' },
    { city: 'Nadiad', state: 'Gujarat', district: 'Kheda', region: 'Central Gujarat' },
    { city: 'Anand', state: 'Gujarat', district: 'Anand', region: 'Central Gujarat' },

    // Rajasthan
    { city: 'Jaipur', state: 'Rajasthan', district: 'Jaipur', region: 'Eastern Rajasthan' },
    { city: 'Jodhpur', state: 'Rajasthan', district: 'Jodhpur', region: 'Western Rajasthan' },
    { city: 'Udaipur', state: 'Rajasthan', district: 'Udaipur', region: 'Southern Rajasthan' },
    { city: 'Kota', state: 'Rajasthan', district: 'Kota', region: 'Southern Rajasthan' },
    { city: 'Bikaner', state: 'Rajasthan', district: 'Bikaner', region: 'Western Rajasthan' },
    { city: 'Ajmer', state: 'Rajasthan', district: 'Ajmer', region: 'Central Rajasthan' },
    { city: 'Bharatpur', state: 'Rajasthan', district: 'Bharatpur', region: 'Eastern Rajasthan' },
    { city: 'Alwar', state: 'Rajasthan', district: 'Alwar', region: 'Eastern Rajasthan' },
    { city: 'Sikar', state: 'Rajasthan', district: 'Sikar', region: 'Eastern Rajasthan' },
    { city: 'Pali', state: 'Rajasthan', district: 'Pali', region: 'Western Rajasthan' },

    // Uttar Pradesh
    { city: 'Lucknow', state: 'Uttar Pradesh', district: 'Lucknow', region: 'Central Uttar Pradesh' },
    { city: 'Kanpur', state: 'Uttar Pradesh', district: 'Kanpur Nagar', region: 'Central Uttar Pradesh' },
    { city: 'Agra', state: 'Uttar Pradesh', district: 'Agra', region: 'Western Uttar Pradesh' },
    { city: 'Varanasi', state: 'Uttar Pradesh', district: 'Varanasi', region: 'Eastern Uttar Pradesh' },
    { city: 'Meerut', state: 'Uttar Pradesh', district: 'Meerut', region: 'Western Uttar Pradesh' },
    { city: 'Allahabad', state: 'Uttar Pradesh', district: 'Prayagraj', region: 'Central Uttar Pradesh' },
    { city: 'Bareilly', state: 'Uttar Pradesh', district: 'Bareilly', region: 'Northern Uttar Pradesh' },
    { city: 'Gorakhpur', state: 'Uttar Pradesh', district: 'Gorakhpur', region: 'Eastern Uttar Pradesh' },
    { city: 'Aligarh', state: 'Uttar Pradesh', district: 'Aligarh', region: 'Western Uttar Pradesh' },
    { city: 'Moradabad', state: 'Uttar Pradesh', district: 'Moradabad', region: 'Northern Uttar Pradesh' },

    // West Bengal
    { city: 'Kolkata', state: 'West Bengal', district: 'Kolkata', region: 'South Bengal' },
    { city: 'Asansol', state: 'West Bengal', district: 'Paschim Bardhaman', region: 'South Bengal' },
    { city: 'Siliguri', state: 'West Bengal', district: 'Darjeeling', region: 'North Bengal' },
    { city: 'Durgapur', state: 'West Bengal', district: 'Paschim Bardhaman', region: 'South Bengal' },
    { city: 'Bardhaman', state: 'West Bengal', district: 'Purba Bardhaman', region: 'South Bengal' },
    { city: 'Malda', state: 'West Bengal', district: 'Malda', region: 'North Bengal' },
    { city: 'Baharampur', state: 'West Bengal', district: 'Murshidabad', region: 'South Bengal' },
    { city: 'Habra', state: 'West Bengal', district: 'North 24 Parganas', region: 'South Bengal' },
    { city: 'Kharagpur', state: 'West Bengal', district: 'Paschim Medinipur', region: 'South Bengal' },
    { city: 'Shantipur', state: 'West Bengal', district: 'Nadia', region: 'South Bengal' },

    // Andhra Pradesh
    { city: 'Visakhapatnam', state: 'Andhra Pradesh', district: 'Visakhapatnam', region: 'Coastal Andhra' },
    { city: 'Vijayawada', state: 'Andhra Pradesh', district: 'Krishna', region: 'Coastal Andhra' },
    { city: 'Guntur', state: 'Andhra Pradesh', district: 'Guntur', region: 'Coastal Andhra' },
    { city: 'Nellore', state: 'Andhra Pradesh', district: 'Nellore', region: 'Coastal Andhra' },
    { city: 'Kurnool', state: 'Andhra Pradesh', district: 'Kurnool', region: 'Rayalaseema' },
    { city: 'Rajahmundry', state: 'Andhra Pradesh', district: 'East Godavari', region: 'Coastal Andhra' },
    { city: 'Tirupati', state: 'Andhra Pradesh', district: 'Chittoor', region: 'Rayalaseema' },
    { city: 'Kadapa', state: 'Andhra Pradesh', district: 'YSR Kadapa', region: 'Rayalaseema' },
    { city: 'Anantapur', state: 'Andhra Pradesh', district: 'Anantapur', region: 'Rayalaseema' },
    { city: 'Chittoor', state: 'Andhra Pradesh', district: 'Chittoor', region: 'Rayalaseema' },

    // Telangana
    { city: 'Hyderabad', state: 'Telangana', district: 'Hyderabad', region: 'Central Telangana' },
    { city: 'Warangal', state: 'Telangana', district: 'Warangal', region: 'Northern Telangana' },
    { city: 'Nizamabad', state: 'Telangana', district: 'Nizamabad', region: 'Northern Telangana' },
    { city: 'Khammam', state: 'Telangana', district: 'Khammam', region: 'Southern Telangana' },
    { city: 'Karimnagar', state: 'Telangana', district: 'Karimnagar', region: 'Northern Telangana' },
    { city: 'Mahabubnagar', state: 'Telangana', district: 'Mahabubnagar', region: 'Southern Telangana' },
    { city: 'Nalgonda', state: 'Telangana', district: 'Nalgonda', region: 'Southern Telangana' },
    { city: 'Adilabad', state: 'Telangana', district: 'Adilabad', region: 'Northern Telangana' },
    { city: 'Medak', state: 'Telangana', district: 'Medak', region: 'Central Telangana' },
    { city: 'Rangareddy', state: 'Telangana', district: 'Rangareddy', region: 'Central Telangana' },

    // Madhya Pradesh
    { city: 'Bhopal', state: 'Madhya Pradesh', district: 'Bhopal', region: 'Central Madhya Pradesh' },
    { city: 'Indore', state: 'Madhya Pradesh', district: 'Indore', region: 'Western Madhya Pradesh' },
    { city: 'Gwalior', state: 'Madhya Pradesh', district: 'Gwalior', region: 'Northern Madhya Pradesh' },
    { city: 'Jabalpur', state: 'Madhya Pradesh', district: 'Jabalpur', region: 'Eastern Madhya Pradesh' },
    { city: 'Ujjain', state: 'Madhya Pradesh', district: 'Ujjain', region: 'Western Madhya Pradesh' },
    { city: 'Sagar', state: 'Madhya Pradesh', district: 'Sagar', region: 'Central Madhya Pradesh' },
    { city: 'Dewas', state: 'Madhya Pradesh', district: 'Dewas', region: 'Western Madhya Pradesh' },
    { city: 'Satna', state: 'Madhya Pradesh', district: 'Satna', region: 'Eastern Madhya Pradesh' },
    { city: 'Ratlam', state: 'Madhya Pradesh', district: 'Ratlam', region: 'Western Madhya Pradesh' },
    { city: 'Rewa', state: 'Madhya Pradesh', district: 'Rewa', region: 'Eastern Madhya Pradesh' },

    // Delhi
    { city: 'New Delhi', state: 'Delhi', district: 'New Delhi', region: 'National Capital Region' },
    { city: 'Delhi', state: 'Delhi', district: 'Central Delhi', region: 'National Capital Region' },

    // Punjab
    { city: 'Chandigarh', state: 'Punjab', district: 'Chandigarh', region: 'Northern Punjab' },
    { city: 'Ludhiana', state: 'Punjab', district: 'Ludhiana', region: 'Central Punjab' },
    { city: 'Amritsar', state: 'Punjab', district: 'Amritsar', region: 'Northern Punjab' },
    { city: 'Jalandhar', state: 'Punjab', district: 'Jalandhar', region: 'Central Punjab' },
    { city: 'Patiala', state: 'Punjab', district: 'Patiala', region: 'Central Punjab' },
    { city: 'Bathinda', state: 'Punjab', district: 'Bathinda', region: 'Southern Punjab' },
    { city: 'Mohali', state: 'Punjab', district: 'SAS Nagar', region: 'Central Punjab' },
    { city: 'Firozpur', state: 'Punjab', district: 'Firozpur', region: 'Southern Punjab' },
    { city: 'Batala', state: 'Punjab', district: 'Gurdaspur', region: 'Northern Punjab' },
    { city: 'Pathankot', state: 'Punjab', district: 'Pathankot', region: 'Northern Punjab' },

    // Haryana
    { city: 'Gurgaon', state: 'Haryana', district: 'Gurugram', region: 'Southern Haryana' },
    { city: 'Faridabad', state: 'Haryana', district: 'Faridabad', region: 'Southern Haryana' },
    { city: 'Panipat', state: 'Haryana', district: 'Panipat', region: 'Northern Haryana' },
    { city: 'Ambala', state: 'Haryana', district: 'Ambala', region: 'Northern Haryana' },
    { city: 'Yamunanagar', state: 'Haryana', district: 'Yamunanagar', region: 'Northern Haryana' },
    { city: 'Rohtak', state: 'Haryana', district: 'Rohtak', region: 'Central Haryana' },
    { city: 'Hisar', state: 'Haryana', district: 'Hisar', region: 'Central Haryana' },
    { city: 'Karnal', state: 'Haryana', district: 'Karnal', region: 'Central Haryana' },
    { city: 'Sonipat', state: 'Haryana', district: 'Sonipat', region: 'Central Haryana' },
    { city: 'Panchkula', state: 'Haryana', district: 'Panchkula', region: 'Northern Haryana' }
];

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = INDIAN_CITIES;
}
