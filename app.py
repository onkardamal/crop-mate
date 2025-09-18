from flask import Flask, request, render_template, jsonify
import numpy as np
import pandas as pd
import sklearn
import pickle
from werkzeug.exceptions import BadRequest
import warnings
import re
import datetime
import requests
import json
from utils import validate_input, parse_range
from data_loader import CROP_INFO, get_climate_suitability, get_soil_ph_range, get_soil_drainage, get_soil_fertility, get_investment_score, get_yield_score, get_market_price_score, get_profit_margin_score

# Suppress scikit-learn version mismatch warnings
warnings.filterwarnings('ignore', category=UserWarning)

app = Flask(__name__)

# Load models and scalers
try:
    model = pickle.load(open('model.pkl', 'rb'))
    sc = pickle.load(open('standscaler.pkl', 'rb'))
    mx = pickle.load(open('minmaxscaler.pkl', 'rb'))
except Exception as e:
    print(f"Error loading models: {str(e)}")
    raise

# Seasonal calendar data
SEASONAL_DATA = {
    "Rice": { "kharif": { "sowing": "June-July", "growing": "July-October", "harvesting": "October-November", "description": "Main rice season in most parts of India" }, "rabi": { "sowing": "November-December", "growing": "December-March", "harvesting": "March-April", "description": "Winter rice in southern states" } },
    "Maize": { "kharif": { "sowing": "June-July", "growing": "July-October", "harvesting": "October-November", "description": "Main maize season" }, "rabi": { "sowing": "October-November", "growing": "November-February", "harvesting": "February-March", "description": "Winter maize in some regions" } },
    "Jute": { "kharif": { "sowing": "March-April", "growing": "April-August", "harvesting": "August-September", "description": "Main jute growing season" } },
    "Cotton": { "kharif": { "sowing": "May-June", "growing": "June-December", "harvesting": "October-January", "description": "Main cotton season" } },
    "Coconut": { "year_round": { "sowing": "Year-round", "growing": "Year-round", "harvesting": "Year-round", "description": "Perennial crop with year-round production" } },
    "Papaya": { "year_round": { "sowing": "Year-round", "growing": "Year-round", "harvesting": "Year-round", "description": "Perennial fruit crop" } },
    "Orange": { "rabi": { "sowing": "July-August", "growing": "August-March", "harvesting": "December-March", "description": "Winter citrus season" } },
    "Apple": { "rabi": { "sowing": "January-February", "growing": "February-September", "harvesting": "September-October", "description": "Temperate fruit season" } },
    "Muskmelon": { "kharif": { "sowing": "February-March", "growing": "March-June", "harvesting": "May-July", "description": "Summer melon season" } },
    "Watermelon": { "kharif": { "sowing": "January-March", "growing": "March-June", "harvesting": "May-July", "description": "Summer watermelon season" } },
    "Grapes": { "rabi": { "sowing": "January-February", "growing": "February-September", "harvesting": "March-September", "description": "Main grape season" } },
    "Mango": { "rabi": { "sowing": "July-August", "growing": "August-May", "harvesting": "March-July", "description": "Mango fruiting season" } },
    "Banana": { "year_round": { "sowing": "Year-round", "growing": "Year-round", "harvesting": "Year-round", "description": "Perennial crop with continuous production" } },
    "Pomegranate": { "rabi": { "sowing": "June-July", "growing": "July-March", "harvesting": "September-March", "description": "Winter pomegranate season" } },
    "Lentil": { "rabi": { "sowing": "October-November", "growing": "November-March", "harvesting": "March-April", "description": "Winter pulse season" } },
    "Blackgram": { "kharif": { "sowing": "June-July", "growing": "July-October", "harvesting": "October-November", "description": "Summer pulse season" } },
    "Mungbean": { "kharif": { "sowing": "June-July", "growing": "July-October", "harvesting": "October-November", "description": "Summer pulse season" } },
    "Mothbeans": { "kharif": { "sowing": "June-July", "growing": "July-October", "harvesting": "October-November", "description": "Drought-resistant summer pulse" } },
    "Pigeonpeas": { "kharif": { "sowing": "June-July", "growing": "July-January", "harvesting": "December-February", "description": "Long-duration pulse crop" } },
    "Kidneybeans": { "rabi": { "sowing": "October-November", "growing": "November-March", "harvesting": "March-April", "description": "Winter bean season" } },
    "Chickpea": { "rabi": { "sowing": "October-November", "growing": "November-March", "harvesting": "March-April", "description": "Winter pulse season" } },
    "Coffee": { "year_round": { "sowing": "Year-round", "growing": "Year-round", "harvesting": "November-March", "description": "Perennial crop with seasonal harvesting" } }
}

# Month mapping for calendar
MONTHS = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
} 

# Indian states and their detailed climate zones
INDIAN_STATES = {
    "Andhra Pradesh": {
        "climate": "tropical", "rainfall": "moderate", "temperature": "hot", "soil": "red_soil",
        "avg_temp": {"min": 20, "max": 35}, "rainfall_mm": 900, "humidity": "moderate",
        "sunlight_hours": 8.5, "altitude": "low", "districts": ["Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna", "Kurnool", "Prakasam", "Srikakulam", "Visakhapatnam", "Vizianagaram", "West Godavari", "YSR Kadapa"]
    },
    "Arunachal Pradesh": {
        "climate": "sub_tropical", "rainfall": "high", "temperature": "moderate", "soil": "mountainous",
        "avg_temp": {"min": 10, "max": 25}, "rainfall_mm": 2800, "humidity": "high",
        "sunlight_hours": 6.5, "altitude": "high", "districts": ["Anjaw", "Changlang", "Dibang Valley", "East Kameng", "East Siang", "Kurung Kumey", "Lohit", "Lower Dibang Valley", "Lower Subansiri", "Papum Pare", "Tawang", "Tirap", "Upper Siang", "Upper Subansiri", "West Kameng", "West Siang"]
    },
    "Assam": {
        "climate": "tropical", "rainfall": "very_high", "temperature": "moderate", "soil": "alluvial",
        "avg_temp": {"min": 15, "max": 30}, "rainfall_mm": 2800, "humidity": "very_high",
        "sunlight_hours": 6.0, "altitude": "low", "districts": ["Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar", "Charaideo", "Chirang", "Darrang", "Dhemaji", "Dhubri", "Dibrugarh", "Dima Hasao", "Goalpara", "Golaghat", "Hailakandi", "Hojai", "Jorhat", "Kamrup", "Kamrup Metropolitan", "Karbi Anglong", "Karimganj", "Kokrajhar", "Lakhimpur", "Majuli", "Morigaon", "Nagaon", "Nalbari", "Sivasagar", "Sonitpur", "South Salmara-Mankachar", "Tinsukia", "Udalguri", "West Karbi Anglong"]
    },
    "Bihar": {
        "climate": "sub_tropical", "rainfall": "moderate", "temperature": "hot", "soil": "alluvial",
        "avg_temp": {"min": 18, "max": 32}, "rainfall_mm": 1200, "humidity": "moderate",
        "sunlight_hours": 7.5, "altitude": "low", "districts": ["Araria", "Arwal", "Aurangabad", "Banka", "Begusarai", "Bhagalpur", "Bhojpur", "Buxar", "Darbhanga", "East Champaran", "Gaya", "Gopalganj", "Jamui", "Jehanabad", "Kaimur", "Katihar", "Khagaria", "Kishanganj", "Lakhisarai", "Madhepura", "Madhubani", "Munger", "Muzaffarpur", "Nalanda", "Nawada", "Patna", "Purnia", "Rohtas", "Saharsa", "Samastipur", "Saran", "Sheikhpura", "Sheohar", "Sitamarhi", "Siwan", "Supaul", "Vaishali", "West Champaran"]
    },
    "Chhattisgarh": {
        "climate": "tropical", "rainfall": "moderate", "temperature": "hot", "soil": "red_soil",
        "avg_temp": {"min": 20, "max": 35}, "rainfall_mm": 1400, "humidity": "moderate",
        "sunlight_hours": 8.0, "altitude": "medium", "districts": ["Balod", "Baloda Bazar", "Balrampur", "Bastar", "Bemetara", "Bijapur", "Bilaspur", "Dantewada", "Dhamtari", "Durg", "Gariaband", "Janjgir-Champa", "Jashpur", "Kabirdham", "Kanker", "Kondagaon", "Korba", "Koriya", "Mahasamund", "Mungeli", "Narayanpur", "Raigarh", "Raipur", "Rajnandgaon", "Sukma", "Surajpur", "Surguja"]
    },
    "Goa": {
        "climate": "tropical", "rainfall": "high", "temperature": "moderate", "soil": "laterite",
        "avg_temp": {"min": 22, "max": 30}, "rainfall_mm": 3000, "humidity": "high",
        "sunlight_hours": 7.0, "altitude": "low", "districts": ["North Goa", "South Goa"]
    },
    "Gujarat": {
        "climate": "arid", "rainfall": "low", "temperature": "hot", "soil": "black_soil",
        "avg_temp": {"min": 22, "max": 38}, "rainfall_mm": 800, "humidity": "low",
        "sunlight_hours": 9.0, "altitude": "low", "districts": ["Ahmedabad", "Amreli", "Anand", "Aravalli", "Banaskantha", "Bharuch", "Bhavnagar", "Botad", "Chhota Udaipur", "Dahod", "Dang", "Devbhoomi Dwarka", "Gandhinagar", "Gir Somnath", "Jamnagar", "Junagadh", "Kheda", "Kutch", "Mahisagar", "Mehsana", "Morbi", "Narmada", "Navsari", "Panchmahal", "Patan", "Porbandar", "Rajkot", "Sabarkantha", "Surat", "Surendranagar", "Tapi", "Vadodara", "Valsad"]
    },
    "Haryana": {
        "climate": "sub_tropical", "rainfall": "low", "temperature": "hot", "soil": "alluvial",
        "avg_temp": {"min": 20, "max": 35}, "rainfall_mm": 600, "humidity": "low",
        "sunlight_hours": 8.5, "altitude": "low", "districts": ["Ambala", "Bhiwani", "Charkhi Dadri", "Faridabad", "Fatehabad", "Gurugram", "Hisar", "Jhajjar", "Jind", "Kaithal", "Karnal", "Kurukshetra", "Mahendragarh", "Nuh", "Palwal", "Panchkula", "Panipat", "Rewari", "Rohtak", "Sirsa", "Sonipat", "Yamunanagar"]
    },
    "Himachal Pradesh": {
        "climate": "temperate", "rainfall": "moderate", "temperature": "cool", "soil": "mountainous",
        "avg_temp": {"min": 5, "max": 25}, "rainfall_mm": 1500, "humidity": "moderate",
        "sunlight_hours": 7.0, "altitude": "high", "districts": ["Bilaspur", "Chamba", "Hamirpur", "Kangra", "Kinnaur", "Kullu", "Lahaul and Spiti", "Mandi", "Shimla", "Sirmaur", "Solan", "Una"]
    },
    "Jharkhand": {
        "climate": "sub_tropical", "rainfall": "moderate", "temperature": "hot", "soil": "red_soil",
        "avg_temp": {"min": 18, "max": 32}, "rainfall_mm": 1200, "humidity": "moderate",
        "sunlight_hours": 7.5, "altitude": "medium", "districts": ["Bokaro", "Chatra", "Deoghar", "Dhanbad", "Dumka", "East Singhbhum", "Garhwa", "Giridih", "Godda", "Gumla", "Hazaribagh", "Jamtara", "Khunti", "Koderma", "Latehar", "Lohardaga", "Pakur", "Palamu", "Ramgarh", "Ranchi", "Sahebganj", "Seraikela Kharsawan", "Simdega", "West Singhbhum"]
    },
    "Karnataka": {
        "climate": "tropical", "rainfall": "moderate", "temperature": "moderate", "soil": "red_soil",
        "avg_temp": {"min": 18, "max": 32}, "rainfall_mm": 1100, "humidity": "moderate",
        "sunlight_hours": 8.0, "altitude": "medium", "districts": ["Bagalkot", "Ballari", "Belagavi", "Bengaluru Rural", "Bengaluru Urban", "Bidar", "Chamarajanagar", "Chikballapur", "Chikkamagaluru", "Chitradurga", "Dakshina Kannada", "Davanagere", "Dharwad", "Gadag", "Hassan", "Haveri", "Kalaburagi", "Kodagu", "Kolar", "Koppal", "Mandya", "Mysuru", "Raichur", "Ramanagara", "Shivamogga", "Tumakuru", "Udupi", "Uttara Kannada", "Vijayapura", "Yadgir"]
    },
    "Kerala": {
        "climate": "tropical", "rainfall": "very_high", "temperature": "moderate", "soil": "laterite",
        "avg_temp": {"min": 22, "max": 30}, "rainfall_mm": 3000, "humidity": "very_high",
        "sunlight_hours": 6.5, "altitude": "low", "districts": ["Alappuzha", "Ernakulam", "Idukki", "Kannur", "Kasaragod", "Kollam", "Kottayam", "Kozhikode", "Malappuram", "Palakkad", "Pathanamthitta", "Thiruvananthapuram", "Thrissur", "Wayanad"]
    },
    "Madhya Pradesh": {
        "climate": "sub_tropical", "rainfall": "moderate", "temperature": "hot", "soil": "black_soil",
        "avg_temp": {"min": 20, "max": 35}, "rainfall_mm": 1200, "humidity": "moderate",
        "sunlight_hours": 8.0, "altitude": "medium", "districts": ["Agar Malwa", "Alirajpur", "Anuppur", "Ashoknagar", "Balaghat", "Barwani", "Betul", "Bhind", "Bhopal", "Burhanpur", "Chhatarpur", "Chhindwara", "Damoh", "Datia", "Dewas", "Dhar", "Dindori", "Guna", "Gwalior", "Harda", "Hoshangabad", "Indore", "Jabalpur", "Jhabua", "Katni", "Khandwa", "Khargone", "Mandla", "Mandsaur", "Morena", "Narsinghpur", "Neemuch", "Panna", "Raisen", "Rajgarh", "Ratlam", "Rewa", "Sagar", "Satna", "Sehore", "Seoni", "Shahdol", "Shajapur", "Sheopur", "Shivpuri", "Sidhi", "Singrauli", "Tikamgarh", "Ujjain", "Umaria", "Vidisha"]
    },
    "Maharashtra": {
        "climate": "tropical", "rainfall": "moderate", "temperature": "hot", "soil": "black_soil",
        "avg_temp": {"min": 20, "max": 35}, "rainfall_mm": 1200, "humidity": "moderate",
        "sunlight_hours": 8.0, "altitude": "medium", "districts": ["Ahmednagar", "Akola", "Amravati", "Aurangabad", "Beed", "Bhandara", "Buldhana", "Chandrapur", "Dhule", "Gadchiroli", "Gondia", "Hingoli", "Jalgaon", "Jalna", "Kolhapur", "Latur", "Mumbai City", "Mumbai Suburban", "Nagpur", "Nanded", "Nashik", "Osmanabad", "Palghar", "Parbhani", "Pune", "Raigad", "Ratnagiri", "Sangli", "Satara", "Sindhudurg", "Solapur", "Thane", "Wardha", "Washim", "Yavatmal"]
    },
    "Manipur": {
        "climate": "sub_tropical", "rainfall": "high", "temperature": "moderate", "soil": "mountainous",
        "avg_temp": {"min": 15, "max": 28}, "rainfall_mm": 2000, "humidity": "high",
        "sunlight_hours": 6.5, "altitude": "high", "districts": ["Bishnupur", "Chandel", "Churachandpur", "Imphal East", "Imphal West", "Jiribam", "Kakching", "Kamjong", "Kangpokpi", "Noney", "Pherzawl", "Senapati", "Tamenglong", "Tengnoupal", "Thoubal", "Ukhrul"]
    },
    "Meghalaya": {
        "climate": "sub_tropical", "rainfall": "very_high", "temperature": "moderate", "soil": "mountainous",
        "avg_temp": {"min": 15, "max": 28}, "rainfall_mm": 3000, "humidity": "very_high",
        "sunlight_hours": 6.0, "altitude": "high", "districts": ["East Garo Hills", "East Jaintia Hills", "East Khasi Hills", "North Garo Hills", "Ri Bhoi", "South Garo Hills", "South West Garo Hills", "South West Khasi Hills", "West Garo Hills", "West Jaintia Hills", "West Khasi Hills"]
    },
    "Mizoram": {
        "climate": "sub_tropical", "rainfall": "high", "temperature": "moderate", "soil": "mountainous",
        "avg_temp": {"min": 15, "max": 28}, "rainfall_mm": 2500, "humidity": "high",
        "sunlight_hours": 6.5, "altitude": "high", "districts": ["Aizawl", "Champhai", "Hnahthial", "Khawzawl", "Kolasib", "Lawngtlai", "Lunglei", "Mamit", "Saiha", "Saitual", "Serchhip"]
    },
    "Nagaland": {
        "climate": "sub_tropical", "rainfall": "high", "temperature": "moderate", "soil": "mountainous",
        "avg_temp": {"min": 15, "max": 28}, "rainfall_mm": 2000, "humidity": "high",
        "sunlight_hours": 6.5, "altitude": "high", "districts": ["Dimapur", "Kiphire", "Kohima", "Longleng", "Mokokchung", "Mon", "Peren", "Phek", "Tuensang", "Wokha", "Zunheboto"]
    },
    "Odisha": {
        "climate": "tropical", "rainfall": "high", "temperature": "hot", "soil": "red_soil",
        "avg_temp": {"min": 20, "max": 35}, "rainfall_mm": 1500, "humidity": "high",
        "sunlight_hours": 7.5, "altitude": "low", "districts": ["Angul", "Balangir", "Balasore", "Bargarh", "Bhadrak", "Bhubaneswar", "Boudh", "Cuttack", "Deogarh", "Dhenkanal", "Gajapati", "Ganjam", "Jagatsinghpur", "Jajpur", "Jharsuguda", "Kalahandi", "Kandhamal", "Kendrapara", "Kendujhar", "Khordha", "Koraput", "Malkangiri", "Mayurbhanj", "Nabarangpur", "Nayagarh", "Nuapada", "Puri", "Rayagada", "Sambalpur", "Subarnapur", "Sundargarh"]
    },
    "Punjab": {
        "climate": "sub_tropical", "rainfall": "low", "temperature": "hot", "soil": "alluvial",
        "avg_temp": {"min": 18, "max": 35}, "rainfall_mm": 600, "humidity": "low",
        "sunlight_hours": 8.5, "altitude": "low", "districts": ["Amritsar", "Barnala", "Bathinda", "Faridkot", "Fatehgarh Sahib", "Fazilka", "Ferozepur", "Gurdaspur", "Hoshiarpur", "Jalandhar", "Kapurthala", "Ludhiana", "Mansa", "Moga", "Muktsar", "Pathankot", "Patiala", "Rupnagar", "Sahibzada Ajit Singh Nagar", "Sangrur", "Shahid Bhagat Singh Nagar", "Tarn Taran"]
    },
    "Rajasthan": {
        "climate": "arid", "rainfall": "very_low", "temperature": "very_hot", "soil": "desert",
        "avg_temp": {"min": 25, "max": 40}, "rainfall_mm": 400, "humidity": "very_low",
        "sunlight_hours": 9.5, "altitude": "low", "districts": ["Ajmer", "Alwar", "Banswara", "Baran", "Barmer", "Bharatpur", "Bhilwara", "Bikaner", "Bundi", "Chittorgarh", "Churu", "Dausa", "Dholpur", "Dungarpur", "Hanumangarh", "Jaipur", "Jaisalmer", "Jalore", "Jhalawar", "Jhunjhunu", "Jodhpur", "Karauli", "Kota", "Nagaur", "Pali", "Pratapgarh", "Rajsamand", "Sawai Madhopur", "Sikar", "Sirohi", "Sri Ganganagar", "Tonk", "Udaipur"]
    },
    "Sikkim": {
        "climate": "temperate", "rainfall": "high", "temperature": "cool", "soil": "mountainous",
        "avg_temp": {"min": 5, "max": 20}, "rainfall_mm": 2500, "humidity": "high",
        "sunlight_hours": 6.0, "altitude": "high", "districts": ["East Sikkim", "North Sikkim", "South Sikkim", "West Sikkim"]
    },
    "Tamil Nadu": {
        "climate": "tropical", "rainfall": "moderate", "temperature": "hot", "soil": "red_soil",
        "avg_temp": {"min": 22, "max": 35}, "rainfall_mm": 1000, "humidity": "moderate",
        "sunlight_hours": 8.0, "altitude": "low", "districts": ["Ariyalur", "Chennai", "Coimbatore", "Cuddalore", "Dharmapuri", "Dindigul", "Erode", "Kanchipuram", "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai", "Ramanathapuram", "Salem", "Sivaganga", "Thanjavur", "Theni", "Thoothukkudi", "Tiruchirappalli", "Tirunelveli", "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur", "Vellore", "Viluppuram", "Virudhunagar"]
    },
    "Telangana": {
        "climate": "tropical", "rainfall": "moderate", "temperature": "hot", "soil": "red_soil",
        "avg_temp": {"min": 20, "max": 35}, "rainfall_mm": 900, "humidity": "moderate",
        "sunlight_hours": 8.5, "altitude": "medium", "districts": ["Adilabad", "Bhadradri Kothagudem", "Hyderabad", "Jagtial", "Jangaon", "Jayashankar Bhupalpally", "Jogulamba Gadwal", "Kamareddy", "Karimnagar", "Khammam", "Kumuram Bheem", "Mahabubabad", "Mahabubnagar", "Mancherial", "Medak", "Medchal–Malkajgiri", "Mulugu", "Nagarkurnool", "Nalgonda", "Narayanpet", "Nirmal", "Nizamabad", "Peddapalli", "Rajanna Sircilla", "Rangareddy", "Sangareddy", "Siddipet", "Suryapet", "Vikarabad", "Wanaparthy", "Warangal Rural", "Warangal Urban", "Yadadri Bhuvanagiri"]
    },
    "Tripura": {
        "climate": "sub_tropical", "rainfall": "high", "temperature": "moderate", "soil": "alluvial",
        "avg_temp": {"min": 15, "max": 30}, "rainfall_mm": 2000, "humidity": "high",
        "sunlight_hours": 6.5, "altitude": "low", "districts": ["Dhalai", "Gomati", "Khowai", "North Tripura", "Sepahijala", "South Tripura", "Unakoti", "West Tripura"]
    },
    "Uttar Pradesh": {
        "climate": "sub_tropical", "rainfall": "moderate", "temperature": "hot", "soil": "alluvial",
        "avg_temp": {"min": 18, "max": 35}, "rainfall_mm": 1000, "humidity": "moderate",
        "sunlight_hours": 7.5, "altitude": "low", "districts": ["Agra", "Aligarh", "Ambedkar Nagar", "Amethi", "Amroha", "Auraiya", "Azamgarh", "Baghpat", "Bahraich", "Ballia", "Balrampur", "Banda", "Barabanki", "Bareilly", "Basti", "Bhadohi", "Bijnor", "Budaun", "Bulandshahr", "Chandauli", "Chitrakoot", "Deoria", "Etah", "Etawah", "Ayodhya", "Farrukhabad", "Fatehpur", "Firozabad", "Gautam Buddha Nagar", "Ghaziabad", "Ghazipur", "Gonda", "Gorakhpur", "Hamirpur", "Hapur", "Hardoi", "Hathras", "Jalaun", "Jaunpur", "Jhansi", "Kannauj", "Kanpur Dehat", "Kanpur Nagar", "Kasganj", "Kaushambi", "Kushinagar", "Lakhimpur Kheri", "Lalitpur", "Lucknow", "Maharajganj", "Mahoba", "Mainpuri", "Mathura", "Mau", "Meerut", "Mirzapur", "Moradabad", "Muzaffarnagar", "Pilibhit", "Pratapgarh", "Prayagraj", "Raebareli", "Rampur", "Saharanpur", "Sambhal", "Sant Kabir Nagar", "Shahjahanpur", "Shamli", "Shravasti", "Siddharthnagar", "Sitapur", "Sonbhadra", "Sultanpur", "Unnao", "Varanasi"]
    },
    "Uttarakhand": {
        "climate": "temperate", "rainfall": "moderate", "temperature": "cool", "soil": "mountainous",
        "avg_temp": {"min": 8, "max": 25}, "rainfall_mm": 1500, "humidity": "moderate",
        "sunlight_hours": 7.0, "altitude": "high", "districts": ["Almora", "Bageshwar", "Chamoli", "Champawat", "Dehradun", "Haridwar", "Nainital", "Pauri Garhwal", "Pithoragarh", "Rudraprayag", "Tehri Garhwal", "Udham Singh Nagar", "Uttarkashi"]
    },
    "West Bengal": {
        "climate": "tropical", "rainfall": "high", "temperature": "moderate", "soil": "alluvial",
        "avg_temp": {"min": 18, "max": 32}, "rainfall_mm": 1800, "humidity": "high",
        "sunlight_hours": 7.0, "altitude": "low", "districts": ["Alipurduar", "Bankura", "Birbhum", "Cooch Behar", "Dakshin Dinajpur", "Darjeeling", "Hooghly", "Howrah", "Jalpaiguri", "Jhargram", "Kalimpong", "Kolkata", "Malda", "Murshidabad", "Nadia", "North 24 Parganas", "Paschim Bardhaman", "Paschim Medinipur", "Purba Bardhaman", "Purba Medinipur", "Purulia", "South 24 Parganas", "Uttar Dinajpur"]
    }
}

# Weather API configuration (using OpenWeatherMap - free tier)
WEATHER_API_KEY = "demo_key"  # Replace with actual API key for production
WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Location detection services
LOCATION_SERVICES = {
    "ipapi": "http://ip-api.com/json/",
    "ipinfo": "https://ipinfo.io/json"
}

# Market data and trends
MARKET_DATA = {
    "Rice": {
        "current_price": 2800,
        "unit": "per quintal",
        "trend": "increasing",
        "change_percent": 5.2,
        "price_history": [
            {"date": "2024-01", "price": 2600},
            {"date": "2024-02", "price": 2650},
            {"date": "2024-03", "price": 2700},
            {"date": "2024-04", "price": 2750},
            {"date": "2024-05", "price": 2800}
        ],
        "seasonal_pattern": "Prices peak during monsoon (July-September)",
        "demand_factors": ["Festival season", "Export demand", "Stock levels"],
        "supply_factors": ["Harvest season", "Weather conditions", "Storage capacity"],
        "market_centers": ["Mumbai", "Delhi", "Kolkata", "Chennai"],
        "export_markets": ["Bangladesh", "Nepal", "Sri Lanka"],
        "min_support_price": 2040,
        "max_price": 3200,
        "volatility": "medium"
    },
    "Wheat": {
        "current_price": 2200,
        "unit": "per quintal",
        "trend": "stable",
        "change_percent": 1.8,
        "price_history": [
            {"date": "2024-01", "price": 2150},
            {"date": "2024-02", "price": 2180},
            {"date": "2024-03", "price": 2200},
            {"date": "2024-04", "price": 2210},
            {"date": "2024-05", "price": 2200}
        ],
        "seasonal_pattern": "Prices stable throughout the year with slight increase in winter",
        "demand_factors": ["Government procurement", "Bakery industry", "Household consumption"],
        "supply_factors": ["Rabi harvest", "Storage facilities", "Transportation"],
        "market_centers": ["Punjab", "Haryana", "Madhya Pradesh", "Uttar Pradesh"],
        "export_markets": ["Afghanistan", "Bangladesh", "Nepal"],
        "min_support_price": 2015,
        "max_price": 2500,
        "volatility": "low"
    },
    "Cotton": {
        "current_price": 6500,
        "unit": "per quintal",
        "trend": "decreasing",
        "change_percent": -3.5,
        "price_history": [
            {"date": "2024-01", "price": 6800},
            {"date": "2024-02", "price": 6700},
            {"date": "2024-03", "price": 6600},
            {"date": "2024-04", "price": 6550},
            {"date": "2024-05", "price": 6500}
        ],
        "seasonal_pattern": "Prices fluctuate based on textile industry demand",
        "demand_factors": ["Textile industry", "Export demand", "Fashion trends"],
        "supply_factors": ["Kharif harvest", "Weather conditions", "Pest attacks"],
        "market_centers": ["Gujarat", "Maharashtra", "Telangana", "Punjab"],
        "export_markets": ["China", "Bangladesh", "Vietnam"],
        "min_support_price": 5726,
        "max_price": 7500,
        "volatility": "high"
    },
    "Sugarcane": {
        "current_price": 315,
        "unit": "per quintal",
        "trend": "increasing",
        "change_percent": 4.8,
        "price_history": [
            {"date": "2024-01", "price": 300},
            {"date": "2024-02", "price": 305},
            {"date": "2024-03", "price": 310},
            {"date": "2024-04", "price": 312},
            {"date": "2024-05", "price": 315}
        ],
        "seasonal_pattern": "Prices peak during crushing season (October-March)",
        "demand_factors": ["Sugar industry", "Ethanol production", "Jaggery making"],
        "supply_factors": ["Crushing season", "Sugar recovery", "Transportation"],
        "market_centers": ["Uttar Pradesh", "Maharashtra", "Karnataka", "Tamil Nadu"],
        "export_markets": ["Sri Lanka", "Nepal", "Bangladesh"],
        "min_support_price": 290,
        "max_price": 350,
        "volatility": "medium"
    },
    "Maize": {
        "current_price": 1800,
        "unit": "per quintal",
        "trend": "increasing",
        "change_percent": 6.2,
        "price_history": [
            {"date": "2024-01", "price": 1700},
            {"date": "2024-02", "price": 1720},
            {"date": "2024-03", "price": 1750},
            {"date": "2024-04", "price": 1780},
            {"date": "2024-05", "price": 1800}
        ],
        "seasonal_pattern": "Prices increase during poultry feed demand season",
        "demand_factors": ["Poultry feed", "Starch industry", "Ethanol production"],
        "supply_factors": ["Kharif harvest", "Storage conditions", "Transportation"],
        "market_centers": ["Karnataka", "Madhya Pradesh", "Maharashtra", "Bihar"],
        "export_markets": ["Bangladesh", "Nepal", "Vietnam"],
        "min_support_price": 1850,
        "max_price": 2200,
        "volatility": "medium"
    },
    "Pulses": {
        "current_price": 4500,
        "unit": "per quintal",
        "trend": "stable",
        "change_percent": 0.5,
        "price_history": [
            {"date": "2024-01", "price": 4480},
            {"date": "2024-02", "price": 4490},
            {"date": "2024-03", "price": 4500},
            {"date": "2024-04", "price": 4505},
            {"date": "2024-05", "price": 4500}
        ],
        "seasonal_pattern": "Prices remain stable with slight variations",
        "demand_factors": ["Household consumption", "Restaurant industry", "Export demand"],
        "supply_factors": ["Rabi harvest", "Import policies", "Storage facilities"],
        "market_centers": ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Uttar Pradesh"],
        "export_markets": ["Bangladesh", "Sri Lanka", "Nepal"],
        "min_support_price": 4000,
        "max_price": 5000,
        "volatility": "low"
    },
    "Oilseeds": {
        "current_price": 5200,
        "unit": "per quintal",
        "trend": "increasing",
        "change_percent": 7.8,
        "price_history": [
            {"date": "2024-01", "price": 4800},
            {"date": "2024-02", "price": 4900},
            {"date": "2024-03", "price": 5000},
            {"date": "2024-04", "price": 5100},
            {"date": "2024-05", "price": 5200}
        ],
        "seasonal_pattern": "Prices increase during festival season",
        "demand_factors": ["Edible oil industry", "Festival demand", "Export markets"],
        "supply_factors": ["Rabi harvest", "Weather conditions", "Import policies"],
        "market_centers": ["Madhya Pradesh", "Rajasthan", "Gujarat", "Maharashtra"],
        "export_markets": ["China", "Bangladesh", "Nepal"],
        "min_support_price": 4500,
        "max_price": 6000,
        "volatility": "high"
    },
    "Vegetables": {
        "current_price": 2500,
        "unit": "per quintal",
        "trend": "decreasing",
        "change_percent": -2.1,
        "price_history": [
            {"date": "2024-01", "price": 2550},
            {"date": "2024-02", "price": 2530},
            {"date": "2024-03", "price": 2520},
            {"date": "2024-04", "price": 2510},
            {"date": "2024-05", "price": 2500}
        ],
        "seasonal_pattern": "Prices vary significantly with seasonal availability",
        "demand_factors": ["Urban consumption", "Restaurant demand", "Export markets"],
        "supply_factors": ["Seasonal production", "Weather conditions", "Transportation"],
        "market_centers": ["Delhi", "Mumbai", "Kolkata", "Chennai"],
        "export_markets": ["UAE", "UK", "USA"],
        "min_support_price": 2000,
        "max_price": 4000,
        "volatility": "very_high"
    },
    "Fruits": {
        "current_price": 3500,
        "unit": "per quintal",
        "trend": "increasing",
        "change_percent": 3.2,
        "price_history": [
            {"date": "2024-01", "price": 3400},
            {"date": "2024-02", "price": 3420},
            {"date": "2024-03", "price": 3450},
            {"date": "2024-04", "price": 3480},
            {"date": "2024-05", "price": 3500}
        ],
        "seasonal_pattern": "Prices peak during off-season periods",
        "demand_factors": ["Urban consumption", "Export demand", "Processing industry"],
        "supply_factors": ["Seasonal production", "Storage facilities", "Transportation"],
        "market_centers": ["Maharashtra", "Karnataka", "Tamil Nadu", "Andhra Pradesh"],
        "export_markets": ["UAE", "UK", "USA", "Netherlands"],
        "min_support_price": 3000,
        "max_price": 5000,
        "volatility": "high"
    }
}

# Market analysis functions
def get_market_trends(crop_name=None, period="6months"):
    """Get market trends for crops"""
    if crop_name:
        if crop_name in MARKET_DATA:
            return MARKET_DATA[crop_name]
        return None
    
    # Return all crops if no specific crop requested
    return MARKET_DATA

def get_price_forecast(crop_name, months=3):
    """Generate price forecast based on historical data and trends"""
    if crop_name not in MARKET_DATA:
        return None
    
    crop_data = MARKET_DATA[crop_name]
    current_price = crop_data['current_price']
    trend = crop_data['trend']
    volatility = crop_data['volatility']
    
    forecast = []
    base_price = current_price
    
    for month in range(1, months + 1):
        # Apply trend factor
        if trend == "increasing":
            change_factor = 1 + (0.02 * month)  # 2% increase per month
        elif trend == "decreasing":
            change_factor = 1 - (0.015 * month)  # 1.5% decrease per month
        else:
            change_factor = 1 + (0.005 * month)  # 0.5% increase per month
        
        # Apply volatility
        volatility_factor = 1
        if volatility == "high":
            volatility_factor = 1 + (0.05 * (month % 2 - 0.5))  # ±5% variation
        elif volatility == "very_high":
            volatility_factor = 1 + (0.08 * (month % 2 - 0.5))  # ±8% variation
        elif volatility == "medium":
            volatility_factor = 1 + (0.03 * (month % 2 - 0.5))  # ±3% variation
        
        forecast_price = int(base_price * change_factor * volatility_factor)
        forecast.append({
            "month": month,
            "price": forecast_price,
            "confidence": "high" if volatility == "low" else "medium"
        })
    
    return forecast

def get_market_insights(crop_name):
    """Get market insights and recommendations"""
    if crop_name not in MARKET_DATA:
        return None
    
    crop_data = MARKET_DATA[crop_name]
    insights = {
        "current_situation": f"Current price is ₹{crop_data['current_price']} {crop_data['unit']}",
        "trend_analysis": f"Price is {crop_data['trend']} by {crop_data['change_percent']}%",
        "recommendations": [],
        "risks": [],
        "opportunities": []
    }
    
    # Generate recommendations based on trend
    if crop_data['trend'] == "increasing":
        insights["recommendations"].append("Consider holding stock for better prices")
        insights["recommendations"].append("Monitor market for peak selling opportunity")
        insights["opportunities"].append("Potential for higher profits in coming months")
    elif crop_data['trend'] == "decreasing":
        insights["recommendations"].append("Consider selling soon to avoid further price drops")
        insights["recommendations"].append("Explore alternative markets or storage options")
        insights["risks"].append("Prices may continue to decline")
    else:
        insights["recommendations"].append("Prices are stable - good time for regular sales")
        insights["recommendations"].append("Focus on quality to get premium prices")
    
    # Add volatility-based insights
    if crop_data['volatility'] == "high":
        insights["risks"].append("High price volatility - monitor market closely")
        insights["recommendations"].append("Consider hedging strategies")
    elif crop_data['volatility'] == "very_high":
        insights["risks"].append("Very high volatility - significant price risk")
        insights["recommendations"].append("Diversify crop portfolio")
    
    return insights

def get_comparative_analysis(crop_names):
    """Compare multiple crops for market analysis"""
    if not crop_names:
        return None
    
    comparison = {
        "crops": [],
        "best_performing": None,
        "most_stable": None,
        "highest_potential": None
    }
    
    best_score = 0
    most_stable_score = 0
    highest_potential_score = 0
    
    for crop_name in crop_names:
        if crop_name not in MARKET_DATA:
            continue
        
        crop_data = MARKET_DATA[crop_name]
        
        # Calculate performance score
        performance_score = crop_data['current_price'] * (1 + crop_data['change_percent']/100)
        
        # Calculate stability score (inverse of volatility)
        stability_scores = {"low": 100, "medium": 70, "high": 40, "very_high": 20}
        stability_score = stability_scores.get(crop_data['volatility'], 50)
        
        # Calculate potential score
        potential_score = performance_score * (1 + crop_data['change_percent']/100)
        
        crop_comparison = {
            "name": crop_name,
            "current_price": crop_data['current_price'],
            "trend": crop_data['trend'],
            "change_percent": crop_data['change_percent'],
            "volatility": crop_data['volatility'],
            "performance_score": performance_score,
            "stability_score": stability_score,
            "potential_score": potential_score
        }
        
        comparison["crops"].append(crop_comparison)
        
        # Track best performers
        if performance_score > best_score:
            best_score = performance_score
            comparison["best_performing"] = crop_name
        
        if stability_score > most_stable_score:
            most_stable_score = stability_score
            comparison["most_stable"] = crop_name
        
        if potential_score > highest_potential_score:
            highest_potential_score = potential_score
            comparison["highest_potential"] = crop_name
    
    return comparison

def get_current_season():
    """Get current season based on month"""
    current_month = datetime.datetime.now().month
    if current_month in [6, 7, 8, 9]: return "kharif"
    elif current_month in [10, 11, 12, 1, 2, 3]: return "rabi"
    else: return "zaid"

def get_crops_by_season(season):
    """Get crops that can be grown in a specific season"""
    return [crop for crop, data in SEASONAL_DATA.items() if season in data or "year_round" in data]

def get_month_list_from_range(month_range_str):
    """Converts a string like 'June-July' or 'Year-round' to a list of month names."""
    if not month_range_str or month_range_str.strip() == "":
        return []
    
    if month_range_str == "Year-round":
        return list(MONTHS.values())

    months = []
    month_names = list(MONTHS.values())
    parts = re.split(r'[,-]', month_range_str.strip())
    
    # Handle single month
    if len(parts) == 1:
        month = parts[0].strip()
        try:
            month_index = month_names.index(month)
            return [month]
        except ValueError:
            return []
    
    # Handle range
    if len(parts) >= 2:
        start_month = parts[0].strip()
        end_month = parts[-1].strip()
        
        try:
            start_index = month_names.index(start_month)
            end_index = month_names.index(end_month)
            
            if start_index <= end_index:
                # Normal range (e.g., June-July)
                return month_names[start_index:end_index+1]
            else:
                # Cross-year range (e.g., October-January)
                return month_names[start_index:] + month_names[:end_index+1]
        except ValueError:
            return []
    
    return []

def get_calendar_data():
    """Prepares all data needed for the calendar template."""
    calendar_data = {}
    
    # First, add all crops from CROP_INFO to ensure all crops are included
    for crop in CROP_INFO.keys():
        calendar_data[crop] = {
            'sowing': [],
            'growing': [],
            'harvesting': []
        }
    
    # Then populate with seasonal data
    for crop, seasons in SEASONAL_DATA.items():
        if crop not in calendar_data:
            calendar_data[crop] = {
                'sowing': [],
                'growing': [],
                'harvesting': []
            }
        
        for season, data in seasons.items():
            # Get months for each activity and remove duplicates
            sowing_months = get_month_list_from_range(data.get('sowing', ''))
            growing_months = get_month_list_from_range(data.get('growing', ''))
            harvesting_months = get_month_list_from_range(data.get('harvesting', ''))
            
            # Add months without duplicates
            for month in sowing_months:
                if month not in calendar_data[crop]['sowing']:
                    calendar_data[crop]['sowing'].append(month)
            
            for month in growing_months:
                if month not in calendar_data[crop]['growing']:
                    calendar_data[crop]['growing'].append(month)
            
            for month in harvesting_months:
                if month not in calendar_data[crop]['harvesting']:
                    calendar_data[crop]['harvesting'].append(month)
    
    return calendar_data

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/predict", methods=['POST'])
def predict():
    try:
        data = {
            'Nitrogen': request.form['Nitrogen'],
            'Phosporus': request.form['Phosporus'],
            'Potassium': request.form['Potassium'],
            'Temperature': request.form['Temperature'],
            'Humidity': request.form['Humidity'],
            'pH': request.form['pH'],
            'Rainfall': request.form['Rainfall']
        }
        is_valid, error_message = validate_input(data)
        if not is_valid:
            return render_template('recommend.html', error=error_message)
        
        feature_list = [float(data[key]) for key in data.keys()]
        single_pred = np.array(feature_list).reshape(1, -1)
        mx_features = mx.transform(single_pred)
        sc_mx_features = sc.transform(mx_features)
        prediction = model.predict(sc_mx_features)

        crop_dict = {1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya", 7: "Orange",
                     8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
                     14: "Pomegranate", 15: "Lentil", 16: "Blackgram", 17: "Mungbean", 18: "Mothbeans",
                     19: "Pigeonpeas", 20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"}

        if prediction[0] in crop_dict:
            crop = crop_dict[prediction[0]]
            crop_details = CROP_INFO.get(crop, {
                "description": "A suitable crop for your soil conditions.",
                "growing_tips": ["Consult local agricultural experts for specific growing tips."],
                "image": "crop.png"
            })
            return render_template('recommend.html', 
                                result=f"{crop} is the best crop to be cultivated right there",
                                crop_details=crop_details)
        else:
            return render_template('recommend.html', 
                                error="Sorry, we could not determine the best crop to be cultivated with the provided data.")
            
    except Exception as e:
        return render_template('recommend.html', error=f"An error occurred: {str(e)}")

@app.route('/compare')
def compare():
    return render_template('compare.html')

@app.route('/api/crops')
def get_crops():
    return jsonify(list(CROP_INFO.keys()))

@app.route('/recommend')
def recommend():
    return render_template('recommend.html')

@app.route('/profitability', methods=['GET', 'POST'])
def profitability():
    crop_names = list(CROP_INFO.keys())
    if request.method == 'POST':
        try:
            crop_name = request.form['crop_name']
            area = float(request.form['area'])
            costs = float(request.form['costs'])

            if area <= 0 or costs <= 0:
                return render_template('profitability.html', crops=crop_names, error="Area and costs must be positive numbers.")
            if crop_name not in CROP_INFO:
                return render_template('profitability.html', crops=crop_names, error="Please select a valid crop.")
            
            crop_data = CROP_INFO[crop_name]
            avg_yield_per_hectare = parse_range(crop_data.get('expected_yield', '0'))
            avg_price_per_ton = parse_range(crop_data.get('market_price', '0'))
            
            total_yield = avg_yield_per_hectare * area
            gross_revenue = total_yield * avg_price_per_ton
            net_profit = gross_revenue - costs
            
            results = {
                'crop_name': crop_name, 'area': area, 'total_costs': costs,
                'avg_yield': avg_yield_per_hectare, 'avg_price': avg_price_per_ton,
                'total_yield': total_yield, 'gross_revenue': gross_revenue,
                'net_profit': net_profit, 'image': crop_data.get('image', 'crop.png')
            }
            return render_template('profitability.html', crops=crop_names, results=results)
        except (ValueError, TypeError):
            return render_template('profitability.html', crops=crop_names, error="Invalid input. Please enter valid numbers for area and costs.")
        except Exception as e:
            return render_template('profitability.html', crops=crop_names, error=f"An error occurred: {str(e)}")
    return render_template('profitability.html', crops=crop_names)

@app.route('/calendar')
def calendar():
    current_season = get_current_season()
    seasonal_crops = get_crops_by_season(current_season)
    template_data = {
        'current_season': current_season.title(),
        'current_month': MONTHS[datetime.datetime.now().month],
        'seasonal_crops': seasonal_crops,
        'all_crops': list(CROP_INFO.keys()),
        'all_seasons': ['kharif', 'rabi', 'zaid'],
        'months': list(MONTHS.values()),
        'calendar_data': get_calendar_data(),
        'crop_images': {crop: info.get('image', 'crop.png') for crop, info in CROP_INFO.items()}
    }
    return render_template('calendar.html', data=template_data)

@app.route('/api/calendar/season/<season>')
def get_seasonal_crops_api(season):
    try:
        crops = get_crops_by_season(season)
        return jsonify({'crops': crops, 'season': season})
    except Exception as e:
        return jsonify({'error': str(e), 'crops': []}), 500

@app.route('/api/calendar/month/<int:month_num>')
def get_monthly_crops_api(month_num):
    try:
        if month_num not in MONTHS:
            return jsonify({'error': 'Invalid month', 'crops': []}), 400
        
        month_name = MONTHS[month_num]
        calendar_data = get_calendar_data()
        monthly_crops = []
        
        for crop, data in calendar_data.items():
            if (month_name in data['sowing'] or 
                month_name in data['growing'] or 
                month_name in data['harvesting']):
                monthly_crops.append(crop)
                
        return jsonify({'crops': monthly_crops, 'month': month_name})
    except Exception as e:
        return jsonify({'error': str(e), 'crops': []}), 500

@app.route('/practices')
def practices():
    return render_template('practices.html')

@app.route('/suitability')
def suitability():
    return render_template('suitability.html')

@app.route('/schemes')
def schemes():
    return render_template('schemes.html')

@app.route('/market')
def market():
    return render_template('market.html')

@app.route('/community')
def community():
    return render_template('community.html')

@app.route('/api/crops/<crop_name>')
def get_crop_details(crop_name):
    if crop_name not in CROP_INFO:
        return jsonify({"error": "Crop not found"}), 404
    
    crop_data = CROP_INFO[crop_name].copy()
    crop_data['climate_suitability'] = {
        'temperature': get_climate_suitability(crop_name, 'temperature'), 'humidity': get_climate_suitability(crop_name, 'humidity'),
        'rainfall': get_climate_suitability(crop_name, 'rainfall'), 'sunlight': get_climate_suitability(crop_name, 'sunlight'),
        'wind': get_climate_suitability(crop_name, 'wind')
    }
    crop_data['soil_compatibility'] = {
        'ph_range': get_soil_ph_range(crop_name), 'drainage': get_soil_drainage(crop_name), 'fertility': get_soil_fertility(crop_name)
    }
    crop_data['profitability'] = {
        'investment': get_investment_score(crop_name), 'yield': get_yield_score(crop_name),
        'market_price': get_market_price_score(crop_name), 'profit_margin': get_profit_margin_score(crop_name)
    }
    return jsonify(crop_data)

@app.route('/api/states')
def get_states():
    """Get all Indian states for the suitability feature."""
    return jsonify(list(INDIAN_STATES.keys()))

@app.route('/api/suitability/<state_name>')
def get_location_suitability(state_name):
    """Get suitable crops for a specific state."""
    try:
        if state_name not in INDIAN_STATES:
            return jsonify({"error": "State not found"}), 404
        
        suitable_crops = get_suitable_crops_for_location(state_name, limit=15)
        state_info = INDIAN_STATES[state_name]
        
        return jsonify({
            "state": state_name,
            "state_info": state_info,
            "suitable_crops": suitable_crops
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/suitability/crop/<crop_name>/<state_name>')
def get_crop_location_details(crop_name, state_name):
    """Get detailed suitability analysis for a specific crop in a specific state."""
    try:
        if crop_name not in CROP_INFO or state_name not in INDIAN_STATES:
            return jsonify({"error": "Crop or state not found"}), 404
        
        suitability_result = calculate_location_suitability(crop_name, state_name)
        crop_data = CROP_INFO[crop_name].copy()
        state_data = INDIAN_STATES[state_name]
        
        # Handle the new return format
        if isinstance(suitability_result, dict):
            suitability_score = suitability_result['total_score']
            detailed_scores = suitability_result['detailed_scores']
            recommendations = suitability_result['recommendations']
        else:
            suitability_score = suitability_result
            detailed_scores = {}
            recommendations = ["Follow standard best practices for this crop."]
        
        # Add suitability analysis
        analysis = {
            "suitability_score": suitability_score,
            "detailed_scores": detailed_scores,
            "recommendations": recommendations,
            "state_climate": state_data,
            "climate_compatibility": {
                "temperature": get_climate_suitability(crop_name, 'temperature'),
                "humidity": get_climate_suitability(crop_name, 'humidity'),
                "rainfall": get_climate_suitability(crop_name, 'rainfall'),
                "sunlight": get_climate_suitability(crop_name, 'sunlight'),
                "wind": get_climate_suitability(crop_name, 'wind')
            },
            "soil_compatibility": {
                "ph_range": get_soil_ph_range(crop_name),
                "drainage": get_soil_drainage(crop_name),
                "fertility": get_soil_fertility(crop_name)
            },
            "regional_preference": state_name in crop_data.get('regions', [])
        }
        
        crop_data['suitability_analysis'] = analysis
        return jsonify(crop_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def calculate_location_suitability(crop_name, state_name, season=None):
    """Calculate detailed suitability score for a crop in a specific state."""
    if crop_name not in CROP_INFO or state_name not in INDIAN_STATES:
        return 0
    
    crop_data = CROP_INFO[crop_name]
    state_data = INDIAN_STATES[state_name]
    
    # Initialize detailed scoring
    scores = {
        'regional_preference': 0,
        'climate_compatibility': 0,
        'soil_compatibility': 0,
        'seasonal_compatibility': 0,
        'market_factors': 0
    }
    
    # 1. Regional Preference (25% weight)
    if state_name in crop_data.get('regions', []):
        scores['regional_preference'] = 25
    else:
        # Check if any neighboring states grow this crop
        neighboring_states = get_neighboring_states(state_name)
        if any(neighbor in crop_data.get('regions', []) for neighbor in neighboring_states):
            scores['regional_preference'] = 15
    
    # 2. Climate Compatibility (35% weight)
    climate_score = 0
    climate_suitability = get_climate_suitability(crop_name, 'temperature')
    
    # Temperature compatibility
    if state_data['climate'] == 'tropical':
        if climate_suitability >= 8:
            climate_score += 15
        elif climate_suitability >= 6:
            climate_score += 10
    elif state_data['climate'] == 'sub_tropical':
        if 5 <= climate_suitability <= 8:
            climate_score += 15
        elif 4 <= climate_suitability <= 9:
            climate_score += 10
    elif state_data['climate'] == 'temperate':
        if climate_suitability <= 7:
            climate_score += 15
        elif climate_suitability <= 8:
            climate_score += 10
    elif state_data['climate'] == 'arid':
        if climate_suitability >= 7:
            climate_score += 12
        elif climate_suitability >= 5:
            climate_score += 8
    
    # Rainfall compatibility
    rainfall_suitability = get_climate_suitability(crop_name, 'rainfall')
    if state_data['rainfall'] == 'very_high' and rainfall_suitability >= 8:
        climate_score += 10
    elif state_data['rainfall'] == 'high' and rainfall_suitability >= 7:
        climate_score += 10
    elif state_data['rainfall'] == 'moderate' and 5 <= rainfall_suitability <= 8:
        climate_score += 10
    elif state_data['rainfall'] == 'low' and rainfall_suitability <= 6:
        climate_score += 10
    elif state_data['rainfall'] == 'very_low' and rainfall_suitability <= 5:
        climate_score += 10
    
    # Humidity compatibility
    humidity_suitability = get_climate_suitability(crop_name, 'humidity')
    if state_data.get('humidity') == 'very_high' and humidity_suitability >= 8:
        climate_score += 5
    elif state_data.get('humidity') == 'high' and humidity_suitability >= 7:
        climate_score += 5
    elif state_data.get('humidity') == 'moderate' and 5 <= humidity_suitability <= 8:
        climate_score += 5
    elif state_data.get('humidity') == 'low' and humidity_suitability <= 6:
        climate_score += 5
    
    scores['climate_compatibility'] = min(climate_score, 35)
    
    # 3. Soil Compatibility (20% weight)
    soil_score = 0
    soil_type = state_data['soil']
    
    # Detailed soil-crop matching
    soil_crop_mapping = {
        'alluvial': ['Rice', 'Wheat', 'Sugarcane', 'Pulses', 'Vegetables'],
        'black_soil': ['Cotton', 'Soybean', 'Groundnut', 'Sunflower', 'Sugarcane'],
        'red_soil': ['Pulses', 'Oilseeds', 'Millets', 'Cotton', 'Tobacco'],
        'laterite': ['Tea', 'Coffee', 'Rubber', 'Cashew', 'Coconut'],
        'mountainous': ['Apples', 'Pears', 'Plums', 'Cherries', 'Tea'],
        'desert': ['Millets', 'Pulses', 'Oilseeds', 'Cactus', 'Drought-resistant crops']
    }
    
    if crop_name in soil_crop_mapping.get(soil_type, []):
        soil_score += 15
    elif any(crop in crop_name for crop in soil_crop_mapping.get(soil_type, [])):
        soil_score += 10
    
    # pH compatibility
    ph_range = get_soil_ph_range(crop_name)
    if ph_range:
        soil_score += 5
    
    scores['soil_compatibility'] = min(soil_score, 20)
    
    # 4. Seasonal Compatibility (15% weight)
    if season:
        seasonal_score = calculate_seasonal_compatibility(crop_name, season, state_data)
        scores['seasonal_compatibility'] = min(seasonal_score, 15)
    else:
        # If no season specified, give moderate score
        scores['seasonal_compatibility'] = 7
    
    # 5. Market Factors (5% weight)
    market_score = 0
    investment_score = get_investment_score(crop_name)
    market_price_score = get_market_price_score(crop_name)
    
    # Consider market factors
    if market_price_score >= 80:
        market_score += 3
    elif market_price_score >= 60:
        market_score += 2
    
    if investment_score <= 50:  # Lower investment is better for small farmers
        market_score += 2
    elif investment_score <= 70:
        market_score += 1
    
    scores['market_factors'] = min(market_score, 5)
    
    # Calculate total weighted score
    total_score = sum(scores.values())
    
    return {
        'total_score': min(total_score, 100),
        'detailed_scores': scores,
        'recommendations': generate_recommendations(scores, crop_name, state_name)
    }

def get_neighboring_states(state_name):
    """Get neighboring states for regional preference calculation."""
    neighbors = {
        "Andhra Pradesh": ["Telangana", "Karnataka", "Tamil Nadu", "Odisha"],
        "Arunachal Pradesh": ["Assam", "Nagaland"],
        "Assam": ["Arunachal Pradesh", "Nagaland", "Manipur", "Mizoram", "Tripura", "Meghalaya", "West Bengal"],
        "Bihar": ["Uttar Pradesh", "Jharkhand", "West Bengal"],
        "Chhattisgarh": ["Madhya Pradesh", "Maharashtra", "Telangana", "Odisha", "Jharkhand", "Uttar Pradesh"],
        "Goa": ["Maharashtra", "Karnataka"],
        "Gujarat": ["Rajasthan", "Madhya Pradesh", "Maharashtra"],
        "Haryana": ["Punjab", "Himachal Pradesh", "Uttar Pradesh", "Rajasthan"],
        "Himachal Pradesh": ["Punjab", "Haryana", "Uttarakhand", "Jammu and Kashmir"],
        "Jharkhand": ["Bihar", "West Bengal", "Odisha", "Chhattisgarh", "Uttar Pradesh"],
        "Karnataka": ["Maharashtra", "Goa", "Kerala", "Tamil Nadu", "Andhra Pradesh", "Telangana"],
        "Kerala": ["Karnataka", "Tamil Nadu"],
        "Madhya Pradesh": ["Rajasthan", "Uttar Pradesh", "Chhattisgarh", "Maharashtra", "Gujarat"],
        "Maharashtra": ["Gujarat", "Madhya Pradesh", "Chhattisgarh", "Telangana", "Karnataka", "Goa"],
        "Manipur": ["Nagaland", "Mizoram", "Assam"],
        "Meghalaya": ["Assam"],
        "Mizoram": ["Manipur", "Tripura", "Assam"],
        "Nagaland": ["Arunachal Pradesh", "Assam", "Manipur"],
        "Odisha": ["West Bengal", "Jharkhand", "Chhattisgarh", "Andhra Pradesh"],
        "Punjab": ["Haryana", "Himachal Pradesh", "Rajasthan"],
        "Rajasthan": ["Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh", "Gujarat"],
        "Sikkim": ["West Bengal"],
        "Tamil Nadu": ["Kerala", "Karnataka", "Andhra Pradesh"],
        "Telangana": ["Maharashtra", "Chhattisgarh", "Andhra Pradesh", "Karnataka"],
        "Tripura": ["Assam", "Mizoram"],
        "Uttar Pradesh": ["Uttarakhand", "Haryana", "Rajasthan", "Madhya Pradesh", "Chhattisgarh", "Jharkhand", "Bihar"],
        "Uttarakhand": ["Himachal Pradesh", "Uttar Pradesh"],
        "West Bengal": ["Sikkim", "Assam", "Bihar", "Jharkhand", "Odisha"]
    }
    return neighbors.get(state_name, [])

def calculate_seasonal_compatibility(crop_name, season, state_data):
    """Calculate seasonal compatibility score."""
    seasonal_crops = {
        'kharif': ['Rice', 'Maize', 'Cotton', 'Jute', 'Sugarcane', 'Pulses'],
        'rabi': ['Wheat', 'Barley', 'Mustard', 'Peas', 'Lentil', 'Chickpea'],
        'zaid': ['Watermelon', 'Muskmelon', 'Cucumber', 'Vegetables']
    }
    
    if crop_name in seasonal_crops.get(season, []):
        return 15
    elif any(crop in crop_name for crop in seasonal_crops.get(season, [])):
        return 10
    else:
        return 5

def generate_recommendations(scores, crop_name, state_name):
    """Generate specific recommendations based on scores."""
    recommendations = []
    
    if scores['regional_preference'] < 15:
        recommendations.append("This crop is not commonly grown in your region. Consider local alternatives.")
    
    if scores['climate_compatibility'] < 20:
        recommendations.append("Climate conditions may not be optimal. Consider irrigation or shade structures.")
    
    if scores['soil_compatibility'] < 10:
        recommendations.append("Soil type may require amendments. Consider soil testing and improvement.")
    
    if scores['seasonal_compatibility'] < 10:
        recommendations.append("Current season may not be ideal. Plan for the next suitable season.")
    
    if scores['market_factors'] < 3:
        recommendations.append("Market conditions may not be favorable. Research local demand.")
    
    if not recommendations:
        recommendations.append("Excellent conditions for this crop! Follow standard best practices.")
    
    return recommendations

def get_suitable_crops_for_location(state_name, limit=10):
    """Get top suitable crops for a specific location."""
    if state_name not in INDIAN_STATES:
        return []
    
    crop_scores = []
    for crop_name in CROP_INFO.keys():
        suitability_result = calculate_location_suitability(crop_name, state_name)
        if isinstance(suitability_result, dict):
            score = suitability_result['total_score']
        else:
            score = suitability_result
            
        if score > 0:
            crop_scores.append({
                'crop_name': crop_name,
                'suitability_score': score,
                'image': CROP_INFO[crop_name].get('image', 'crop.png'),
                'description': CROP_INFO[crop_name].get('description', ''),
                'growing_season': CROP_INFO[crop_name].get('growing_season', ''),
                'water_requirements': CROP_INFO[crop_name].get('water_requirements', ''),
                'expected_yield': CROP_INFO[crop_name].get('expected_yield', ''),
                'market_price': CROP_INFO[crop_name].get('market_price', '')
            })
    
    # Sort by suitability score (descending) and return top results
    crop_scores.sort(key=lambda x: x['suitability_score'], reverse=True)
    return crop_scores[:limit]

def get_user_location_from_ip():
    """Get user's approximate location from IP address."""
    try:
        print("Attempting to get location from IP...")
        # Try multiple location services for better accuracy
        response = requests.get(LOCATION_SERVICES["ipapi"], timeout=5)
        print(f"Location API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Location API data: {data}")
            
            if data.get('status') == 'success':
                location_data = {
                    'city': data.get('city', ''),
                    'region': data.get('regionName', ''),
                    'country': data.get('country', ''),
                    'lat': data.get('lat', 0),
                    'lon': data.get('lon', 0),
                    'timezone': data.get('timezone', '')
                }
                print(f"Location detected: {location_data}")
                return location_data
            else:
                print(f"Location API returned status: {data.get('status')}")
        else:
            print(f"Location API failed with status: {response.status_code}")
    except Exception as e:
        print(f"Error getting location from IP: {e}")
    
    return None

def get_weather_data(lat, lon):
    """Get current weather data for given coordinates."""
    try:
        params = {
            'lat': lat,
            'lon': lon,
            'appid': WEATHER_API_KEY,
            'units': 'metric'  # Use Celsius
        }
        response = requests.get(WEATHER_BASE_URL, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'],
                'wind_speed': data['wind']['speed'],
                'visibility': data.get('visibility', 10000),
                'clouds': data['clouds']['all'],
                'sunrise': data['sys']['sunrise'],
                'sunset': data['sys']['sunset']
            }
    except Exception as e:
        print(f"Error getting weather data: {e}")
    
    return None

def get_weather_forecast(lat, lon):
    """Get 5-day weather forecast."""
    try:
        forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': WEATHER_API_KEY,
            'units': 'metric'
        }
        response = requests.get(forecast_url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data['list'][:5]  # Return next 5 days
    except Exception as e:
        print(f"Error getting weather forecast: {e}")
    
    return None

def map_weather_to_climate_zone(weather_data):
    """Map current weather conditions to climate zones."""
    if not weather_data:
        return 'moderate'
    
    temp = weather_data['temperature']
    humidity = weather_data['humidity']
    
    # Temperature-based classification
    if temp >= 30:
        temp_zone = 'hot'
    elif temp >= 20:
        temp_zone = 'moderate'
    elif temp >= 10:
        temp_zone = 'cool'
    else:
        temp_zone = 'cold'
    
    # Humidity-based classification
    if humidity >= 80:
        humidity_level = 'very_high'
    elif humidity >= 60:
        humidity_level = 'high'
    elif humidity >= 40:
        humidity_level = 'moderate'
    else:
        humidity_level = 'low'
    
    return {
        'temperature_zone': temp_zone,
        'humidity_level': humidity_level,
        'current_temp': temp,
        'current_humidity': humidity
    }

def find_nearest_state(lat, lon):
    """Find the nearest Indian state based on coordinates."""
    # Approximate coordinates of Indian states (simplified)
    state_coordinates = {
        "Andhra Pradesh": (15.9129, 79.7400),
        "Arunachal Pradesh": (28.2180, 94.7278),
        "Assam": (26.2006, 92.9376),
        "Bihar": (25.0961, 85.3131),
        "Chhattisgarh": (21.2787, 81.8661),
        "Goa": (15.2993, 74.1240),
        "Gujarat": (22.2587, 71.1924),
        "Haryana": (29.0588, 76.0856),
        "Himachal Pradesh": (31.1048, 77.1734),
        "Jharkhand": (23.6102, 85.2799),
        "Karnataka": (15.3173, 75.7139),
        "Kerala": (10.8505, 76.2711),
        "Madhya Pradesh": (23.5937, 78.9629),
        "Maharashtra": (19.7515, 75.7139),
        "Manipur": (24.6637, 93.9063),
        "Meghalaya": (25.4670, 91.3662),
        "Mizoram": (23.1645, 92.9376),
        "Nagaland": (26.1584, 94.5624),
        "Odisha": (20.9517, 85.0985),
        "Punjab": (31.1471, 75.3412),
        "Rajasthan": (27.0238, 74.2179),
        "Sikkim": (27.5330, 88.5122),
        "Tamil Nadu": (11.1271, 78.6569),
        "Telangana": (18.1124, 79.0193),
        "Tripura": (23.9408, 91.9882),
        "Uttar Pradesh": (26.8467, 80.9462),
        "Uttarakhand": (30.0668, 79.0193),
        "West Bengal": (22.9868, 87.8550)
    }
    
    min_distance = float('inf')
    nearest_state = None
    
    for state, (state_lat, state_lon) in state_coordinates.items():
        # Calculate distance using Haversine formula
        distance = calculate_distance(lat, lon, state_lat, state_lon)
        if distance < min_distance:
            min_distance = distance
            nearest_state = state
    
    return nearest_state, min_distance

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates using Haversine formula."""
    import math
    
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def get_auto_location_data():
    """Get user's location and weather data automatically."""
    try:
        # Get location from IP
        location_data = get_user_location_from_ip()
        if not location_data:
            return None
        
        # Get weather data (with fallback)
        weather_data = get_weather_data(location_data['lat'], location_data['lon'])
        
        # Find nearest Indian state
        nearest_state, distance = find_nearest_state(location_data['lat'], location_data['lon'])
        
        # Map weather to climate zone (with fallback)
        climate_zone = map_weather_to_climate_zone(weather_data) if weather_data else {
            'temperature_zone': 'moderate',
            'humidity_level': 'moderate',
            'current_temp': 25,  # Default temperature
            'current_humidity': 60  # Default humidity
        }
        
        return {
            'location': location_data,
            'weather': weather_data,
            'nearest_state': nearest_state,
            'distance_km': distance,
            'climate_zone': climate_zone
        }
    except Exception as e:
        print(f"Error in auto location detection: {e}")
        return None

@app.route('/api/auto-detect')
def auto_detect_location():
    """Automatically detect user's location and get weather data."""
    try:
        print("Auto-detection requested...")
        auto_data = get_auto_location_data()
        if not auto_data:
            print("Auto-detection failed - no data returned")
            return jsonify({"error": "Could not detect location automatically"}), 400
        
        print(f"Auto-detection successful: {auto_data['nearest_state']}")
        return jsonify(auto_data)
    except Exception as e:
        print(f"Auto-detection error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/weather-based-recommendations')
def get_weather_based_recommendations():
    """Get crop recommendations based on current weather conditions."""
    try:
        # Get auto-detected data
        auto_data = get_auto_location_data()
        if not auto_data:
            return jsonify({"error": "Could not detect location automatically"}), 400
        
        weather_data = auto_data['weather']
        nearest_state = auto_data['nearest_state']
        climate_zone = auto_data['climate_zone']
        
        if not nearest_state:
            return jsonify({"error": "Could not determine nearest state"}), 400
        
        # Get base recommendations for the nearest state
        base_recommendations = get_suitable_crops_for_location(nearest_state, limit=20)
        
        # Adjust scores based on current weather (or use base scores if weather not available)
        weather_adjusted_recommendations = []
        for crop in base_recommendations:
            if weather_data:
                adjusted_score = adjust_score_for_weather(crop['crop_name'], weather_data, climate_zone)
            else:
                # Use base suitability score if weather data not available
                adjusted_score = crop['suitability_score']
            
            crop['weather_adjusted_score'] = adjusted_score
            crop['weather_conditions'] = {
                'current_temp': climate_zone['current_temp'],
                'current_humidity': climate_zone['current_humidity'],
                'weather_description': weather_data['description'] if weather_data else 'Weather data not available',
                'climate_zone': climate_zone
            }
            weather_adjusted_recommendations.append(crop)
        
        # Sort by weather-adjusted score
        weather_adjusted_recommendations.sort(key=lambda x: x['weather_adjusted_score'], reverse=True)
        
        return jsonify({
            'auto_detected_data': auto_data,
            'recommendations': weather_adjusted_recommendations[:15],
            'weather_summary': {
                'temperature': f"{climate_zone['current_temp']}°C",
                'humidity': f"{climate_zone['current_humidity']}%",
                'description': weather_data['description'] if weather_data else 'Weather data not available',
                'nearest_state': nearest_state,
                'distance_km': round(auto_data['distance_km'], 1)
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def adjust_score_for_weather(crop_name, weather_data, climate_zone):
    """Adjust crop suitability score based on current weather conditions."""
    base_score = 50  # Start with base score
    
    temp = weather_data['temperature']
    humidity = weather_data['humidity']
    
    # Get crop's climate preferences
    temp_suitability = get_climate_suitability(crop_name, 'temperature')
    humidity_suitability = get_climate_suitability(crop_name, 'humidity')
    
    # Temperature adjustment
    if temp_suitability >= 8:  # Crop prefers high temperature
        if temp >= 25:
            base_score += 20
        elif temp >= 20:
            base_score += 10
        else:
            base_score -= 10
    elif temp_suitability <= 5:  # Crop prefers cool temperature
        if temp <= 20:
            base_score += 20
        elif temp <= 25:
            base_score += 10
        else:
            base_score -= 10
    else:  # Moderate temperature preference
        if 15 <= temp <= 30:
            base_score += 15
        else:
            base_score -= 5
    
    # Humidity adjustment
    if humidity_suitability >= 8:  # Crop prefers high humidity
        if humidity >= 70:
            base_score += 15
        elif humidity >= 50:
            base_score += 5
        else:
            base_score -= 10
    elif humidity_suitability <= 5:  # Crop prefers low humidity
        if humidity <= 50:
            base_score += 15
        elif humidity <= 70:
            base_score += 5
        else:
            base_score -= 10
    else:  # Moderate humidity preference
        if 40 <= humidity <= 80:
            base_score += 10
        else:
            base_score -= 5
    
    # Weather description adjustment
    weather_desc = weather_data['description'].lower()
    if 'rain' in weather_desc or 'drizzle' in weather_desc:
        # Good for most crops
        base_score += 10
    elif 'clear' in weather_desc or 'sunny' in weather_desc:
        # Good for sun-loving crops
        if get_climate_suitability(crop_name, 'sunlight') >= 7:
            base_score += 10
    elif 'cloudy' in weather_desc:
        # Moderate for most crops
        base_score += 5
    
    return max(0, min(100, base_score))  # Ensure score is between 0-100

@app.route('/api/smart-recommend', methods=['POST'])
def smart_recommend():
    try:
        data = request.get_json()
        # 1. Soil/Nutrient ML prediction
        soil_features = []
        for key in ['Nitrogen', 'Phosporus', 'Potassium', 'Temperature', 'Humidity', 'pH', 'Rainfall']:
            val = data.get(key)
            if val is None or val == '':
                soil_features.append(0)
            else:
                soil_features.append(float(val))
        ml_pred = model.predict(sc.transform(mx.transform([soil_features])))[0]
        crop_dict = {1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya", 7: "Orange",
                     8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
                     14: "Pomegranate", 15: "Lentil", 16: "Blackgram", 17: "Mungbean", 18: "Mothbeans",
                     19: "Pigeonpeas", 20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"}
        ml_crop = crop_dict.get(ml_pred, None)
        # 2. Local suitability
        state = data.get('state')
        season = data.get('season')
        local_scores = {}
        for crop in CROP_INFO.keys():
            local_result = calculate_location_suitability(crop, state, season) if state else {'total_score': 50}
            local_scores[crop] = local_result['total_score'] if isinstance(local_result, dict) else local_result
        # 3. Weather adjustment
        temp = float(data.get('Temperature', 0))
        humidity = float(data.get('Humidity', 0))
        weather_scores = {}
        for crop in CROP_INFO.keys():
            temp_suit = get_climate_suitability(crop, 'temperature')
            hum_suit = get_climate_suitability(crop, 'humidity')
            score = 0
            if temp_suit >= 8 and temp >= 25:
                score += 10
            elif temp_suit <= 5 and temp <= 20:
                score += 10
            else:
                score += 5
            if hum_suit >= 8 and humidity >= 70:
                score += 10
            elif hum_suit <= 5 and humidity <= 50:
                score += 10
            else:
                score += 5
            weather_scores[crop] = score
        # 4. Season fit
        season_scores = {}
        for crop in CROP_INFO.keys():
            if season:
                season_scores[crop] = calculate_seasonal_compatibility(crop, season, INDIAN_STATES.get(state, {}))
            else:
                season_scores[crop] = 7
        # 5. Profitability
        profit_scores = {}
        area = float(data.get('area', 0) or 0)
        costs = float(data.get('costs', 0) or 0)
        for crop in CROP_INFO.keys():
            try:
                avg_yield = parse_range(CROP_INFO[crop].get('expected_yield', '0'))
                avg_price = parse_range(CROP_INFO[crop].get('market_price', '0'))
                total_yield = avg_yield * area if area else 0
                gross_revenue = total_yield * avg_price
                net_profit = gross_revenue - costs if area and costs else 0
                score = 10 if net_profit > 0 else 5
                profit_scores[crop] = score
            except:
                profit_scores[crop] = 5
        # Weighted sum for all crops
        crop_results = []
        for crop in CROP_INFO.keys():
            ml_score = 100 if crop == ml_crop else 60
            local_score = local_scores.get(crop, 50)
            weather_score = weather_scores.get(crop, 10)
            season_score = season_scores.get(crop, 7)
            profit_score = profit_scores.get(crop, 5)
            total = (ml_score*0.3 + local_score*0.25 + weather_score*0.2 + season_score*0.1 + profit_score*0.15)
            avg_yield = parse_range(CROP_INFO[crop].get('expected_yield', '0'))
            avg_price = parse_range(CROP_INFO[crop].get('market_price', '0'))
            total_yield = avg_yield * area if area else 0
            gross_revenue = total_yield * avg_price
            estimated_profit = gross_revenue - costs if area and costs else None
            crop_results.append({
                'crop': crop,
                'total_score': int(round(total)),
                'breakdown': {
                    'soil_score': ml_score,
                    'local_score': local_score,
                    'weather_score': weather_score,
                    'season_score': season_score,
                    'profit_score': profit_score
                },
                'estimated_profit': int(estimated_profit) if estimated_profit is not None else None,
                'description': CROP_INFO[crop].get('description', ''),
                'image': CROP_INFO[crop].get('image', 'crop.png')
            })
        # Sort and pick top 3
        crop_results.sort(key=lambda x: x['total_score'], reverse=True)
        top_crops = crop_results[:3]
        return jsonify({'top_crops': top_crops})
    except Exception as e:
        return jsonify({'error': f'Error in recommendation: {str(e)}'})

@app.route('/api/schemes')
def get_schemes():
    schemes = [
        {
            'name': 'PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)',
            'description': 'Income support of ₹6,000/year to all farmer families in three equal installments.',
            'eligibility': 'All small and marginal farmers (landholding up to 2 hectares).',
            'benefits': 'Direct cash transfer to bank account.',
            'link': 'https://pmkisan.gov.in/',
            'states': 'all',
            'crops': 'all'
        },
        {
            'name': 'PMFBY (Pradhan Mantri Fasal Bima Yojana)',
            'description': 'Crop insurance scheme for farmers against crop loss due to natural calamities. Covers all major crops.',
            'eligibility': 'All farmers growing notified crops in notified areas.',
            'benefits': 'Low premium insurance for crops.',
            'link': 'https://pmfby.gov.in/',
            'states': 'all',
            'crops': 'all'
        },
        {
            'name': 'Soil Health Card Scheme',
            'description': 'Provides soil health cards to farmers with crop-wise recommendations of nutrients and fertilizers.',
            'eligibility': 'All farmers.',
            'benefits': 'Improved soil fertility and productivity.',
            'link': 'https://soilhealth.dac.gov.in/',
            'states': 'all',
            'crops': 'all'
        },
        {
            'name': 'Kisan Credit Card (KCC)',
            'description': 'Provides timely access to credit for farmers for their cultivation and other needs.',
            'eligibility': 'All farmers (individuals/joint borrowers/tenant farmers/sharecroppers).',
            'benefits': 'Short-term credit at low interest rates.',
            'link': 'https://pmkisan.gov.in/Documents/KCC.pdf',
            'states': 'all',
            'crops': 'all'
        },
        {
            'name': 'National Food Security Mission (NFSM)',
            'description': 'Increase production of rice, wheat, pulses, coarse cereals & commercial crops.',
            'eligibility': 'Farmers growing targeted crops.',
            'benefits': 'Subsidies on seeds, fertilizers, and machinery.',
            'link': 'https://nfsm.gov.in/',
            'states': 'all',
            'crops': ['rice', 'wheat', 'pulses', 'coarse cereals', 'commercial crops']
        },
        {
            'name': 'Rashtriya Krishi Vikas Yojana (RKVY)',
            'description': 'Provides states with funds to develop agriculture and allied sectors.',
            'eligibility': 'State governments, farmers benefit via state projects.',
            'benefits': 'Subsidies, infrastructure, and training.',
            'link': 'https://rkvy.nic.in/',
            'states': ['Maharashtra', 'Gujarat', 'Punjab', 'Karnataka', 'Tamil Nadu', 'all'],
            'crops': 'all'
        },
        {
            'name': 'Mukhya Mantri Krishi Ashirwad Yojana',
            'description': 'Jharkhand state scheme: ₹5,000/acre/year to small and marginal farmers.',
            'eligibility': 'Small and marginal farmers of Jharkhand.',
            'benefits': 'Direct cash transfer.',
            'link': 'https://mmkay.jharkhand.gov.in/',
            'states': ['Jharkhand'],
            'crops': 'all'
        },
        {
            'name': 'Telangana Rythu Bandhu',
            'description': 'Telangana state scheme: Investment support of ₹5,000/acre/season to all farmers.',
            'eligibility': 'All farmers of Telangana.',
            'benefits': 'Direct cash transfer.',
            'link': 'https://rythubandhu.telangana.gov.in/',
            'states': ['Telangana'],
            'crops': 'all'
        }
    ]
    state = request.args.get('state')
    crop = request.args.get('crop')
    filtered = []
    for scheme in schemes:
        # State filter
        if state and scheme['states'] != 'all':
            if isinstance(scheme['states'], list):
                if state not in scheme['states'] and 'all' not in scheme['states']:
                    continue
            elif scheme['states'] != state:
                continue
        # Crop filter
        if crop and scheme['crops'] != 'all':
            crop_lower = crop.lower()
            if isinstance(scheme['crops'], list):
                if not any(crop_lower in c.lower() for c in scheme['crops']):
                    continue
            elif crop_lower not in scheme['crops'].lower():
                continue
        # Also allow crop filter to match in description
        if crop and scheme['crops'] == 'all':
            if crop.lower() not in scheme['description'].lower():
                continue
        filtered.append(scheme)
    if not state and not crop:
        filtered = schemes
    return jsonify({'schemes': filtered})

@app.route('/api/market/trends')
def api_market_trends():
    """Get market trends for all crops or specific crop"""
    crop_name = request.args.get('crop')
    period = request.args.get('period', '6months')
    
    trends = get_market_trends(crop_name, period)
    if trends is None:
        return jsonify({"error": "Crop not found"}), 404
    
    return jsonify({"trends": trends})

@app.route('/api/market/forecast/<crop_name>')
def api_price_forecast(crop_name):
    """Get price forecast for a specific crop"""
    months = request.args.get('months', 3, type=int)
    
    forecast = get_price_forecast(crop_name, months)
    if forecast is None:
        return jsonify({"error": "Crop not found"}), 404
    
    return jsonify({"forecast": forecast, "crop": crop_name})

@app.route('/api/market/insights/<crop_name>')
def api_market_insights(crop_name):
    """Get market insights for a specific crop"""
    insights = get_market_insights(crop_name)
    if insights is None:
        return jsonify({"error": "Crop not found"}), 404
    
    return jsonify({"insights": insights, "crop": crop_name})

@app.route('/api/market/compare')
def api_market_compare():
    """Compare multiple crops for market analysis"""
    crops = request.args.getlist('crops')
    
    if not crops:
        return jsonify({"error": "No crops specified"}), 400
    
    comparison = get_comparative_analysis(crops)
    if comparison is None:
        return jsonify({"error": "Invalid crops specified"}), 400
    
    return jsonify({"comparison": comparison})

@app.route('/api/market/top-performers')
def api_top_performers():
    """Get top performing crops based on various metrics"""
    metric = request.args.get('metric', 'performance')  # performance, stability, potential
    
    all_crops = list(MARKET_DATA.keys())
    comparison = get_comparative_analysis(all_crops)
    
    if not comparison:
        return jsonify({"error": "Unable to analyze crops"}), 500
    
    # Sort crops by the requested metric
    if metric == "performance":
        sorted_crops = sorted(comparison["crops"], key=lambda x: x["performance_score"], reverse=True)
    elif metric == "stability":
        sorted_crops = sorted(comparison["crops"], key=lambda x: x["stability_score"], reverse=True)
    elif metric == "potential":
        sorted_crops = sorted(comparison["crops"], key=lambda x: x["potential_score"], reverse=True)
    else:
        return jsonify({"error": "Invalid metric"}), 400
    
    return jsonify({
        "top_performers": sorted_crops[:10],
        "metric": metric,
        "best_crop": comparison.get("best_performing"),
        "most_stable": comparison.get("most_stable"),
        "highest_potential": comparison.get("highest_potential")
    })

@app.route('/api/market/seasonal-analysis')
def api_seasonal_analysis():
    """Get seasonal price patterns for crops"""
    crop_name = request.args.get('crop')
    
    if not crop_name or crop_name not in MARKET_DATA:
        return jsonify({"error": "Crop not found"}), 404
    
    crop_data = MARKET_DATA[crop_name]
    
    seasonal_analysis = {
        "crop": crop_name,
        "seasonal_pattern": crop_data["seasonal_pattern"],
        "price_history": crop_data["price_history"],
        "current_season": get_current_season(),
        "seasonal_recommendations": []
    }
    
    # Add seasonal recommendations
    current_season = get_current_season()
    if current_season == "kharif":
        if crop_name in ["Rice", "Maize", "Cotton"]:
            seasonal_analysis["seasonal_recommendations"].append("Kharif harvest season - prices may stabilize")
        else:
            seasonal_analysis["seasonal_recommendations"].append("Monitor kharif crop prices for market impact")
    elif current_season == "rabi":
        if crop_name in ["Wheat", "Pulses", "Oilseeds"]:
            seasonal_analysis["seasonal_recommendations"].append("Rabi harvest season - consider storage for better prices")
        else:
            seasonal_analysis["seasonal_recommendations"].append("Rabi season may affect overall market sentiment")
    
    return jsonify({"seasonal_analysis": seasonal_analysis})

# Community data and features
COMMUNITY_DATA = {
    "forums": [
        {
            "id": 1,
            "title": "Organic Farming Techniques",
            "description": "Share and learn about organic farming methods, natural pest control, and sustainable practices.",
            "category": "Organic Farming",
            "posts": 45,
            "members": 128,
            "last_activity": "2024-12-28",
            "tags": ["organic", "sustainable", "pest-control"]
        },
        {
            "id": 2,
            "title": "Crop Disease Management",
            "description": "Discuss crop diseases, identification, treatment methods, and prevention strategies.",
            "category": "Plant Health",
            "posts": 67,
            "members": 203,
            "last_activity": "2024-12-27",
            "tags": ["diseases", "treatment", "prevention"]
        },
        {
            "id": 3,
            "title": "Modern Irrigation Systems",
            "description": "Learn about drip irrigation, sprinkler systems, and water conservation techniques.",
            "category": "Irrigation",
            "posts": 34,
            "members": 156,
            "last_activity": "2024-12-26",
            "tags": ["irrigation", "water-conservation", "drip-system"]
        },
        {
            "id": 4,
            "title": "Market Strategies & Pricing",
            "description": "Share market insights, pricing strategies, and selling techniques for better profits.",
            "category": "Marketing",
            "posts": 89,
            "members": 312,
            "last_activity": "2024-12-28",
            "tags": ["marketing", "pricing", "profit"]
        },
        {
            "id": 5,
            "title": "Government Schemes & Subsidies",
            "description": "Discuss government agricultural schemes, subsidies, and how to apply for them.",
            "category": "Government Support",
            "posts": 56,
            "members": 189,
            "last_activity": "2024-12-25",
            "tags": ["schemes", "subsidies", "government"]
        },
        {
            "id": 6,
            "title": "New Farmers Support Group",
            "description": "A supportive community for new and aspiring farmers to learn and grow together.",
            "category": "Beginner Support",
            "posts": 123,
            "members": 445,
            "last_activity": "2024-12-28",
            "tags": ["beginners", "support", "learning"]
        }
    ],
    "success_stories": [
        {
            "id": 1,
            "farmer_name": "Rajesh Kumar",
            "location": "Punjab",
            "crop": "Wheat",
            "story": "Switched to organic wheat farming 3 years ago. Started with 2 acres, now farming 15 acres organically. My wheat fetches 20% premium price in the market. The key was patience and proper soil management.",
            "achievements": ["20% premium pricing", "15 acres organic farming", "Soil health improvement"],
            "tips": ["Start small and scale gradually", "Focus on soil health", "Build market connections"],
            "image": "farmer1.jpg",
            "date": "2024-12-20",
            "likes": 45,
            "comments": 12
        },
        {
            "id": 2,
            "farmer_name": "Lakshmi Devi",
            "location": "Karnataka",
            "crop": "Vegetables",
            "story": "Started vegetable farming after my husband's passing. With community support and proper guidance, I now supply vegetables to 3 local markets. My children are also involved in the business.",
            "achievements": ["3 market supply contracts", "Family business established", "Community leadership"],
            "tips": ["Network with other farmers", "Focus on quality over quantity", "Involve family in farming"],
            "image": "farmer2.jpg",
            "date": "2024-12-18",
            "likes": 67,
            "comments": 23
        },
        {
            "id": 3,
            "farmer_name": "Amrit Singh",
            "location": "Haryana",
            "crop": "Dairy + Crops",
            "story": "Integrated dairy farming with crop cultivation. The manure from dairy helps my crops, and crop residues feed my cattle. This integrated approach increased my income by 40%.",
            "achievements": ["40% income increase", "Integrated farming system", "Sustainable practices"],
            "tips": ["Consider integrated farming", "Use farm waste efficiently", "Diversify income sources"],
            "image": "farmer3.jpg",
            "date": "2024-12-15",
            "likes": 89,
            "comments": 31
        },
        {
            "id": 4,
            "farmer_name": "Sunita Patel",
            "location": "Gujarat",
            "crop": "Cotton",
            "story": "Adopted Bt cotton with proper guidance. Used drip irrigation and proper pest management. My cotton yield increased by 35% and reduced water usage by 40%.",
            "achievements": ["35% yield increase", "40% water savings", "Better pest management"],
            "tips": ["Choose right crop varieties", "Invest in irrigation systems", "Monitor pest levels regularly"],
            "image": "farmer4.jpg",
            "date": "2024-12-12",
            "likes": 56,
            "comments": 18
        }
    ],
    "expert_advice": [
        {
            "id": 1,
            "expert_name": "Dr. Priya Sharma",
            "expertise": "Soil Science",
            "qualification": "PhD in Agricultural Sciences",
            "topic": "Soil Health Management",
            "advice": "Regular soil testing is crucial for sustainable farming. Test your soil every 2-3 years and adjust fertilizer application accordingly. Organic matter content should be maintained above 2% for optimal crop growth.",
            "tips": [
                "Test soil pH and nutrient levels regularly",
                "Add organic matter through composting",
                "Practice crop rotation to maintain soil health",
                "Use cover crops to prevent soil erosion"
            ],
            "image": "expert1.jpg",
            "date": "2024-12-25"
        },
        {
            "id": 2,
            "expert_name": "Prof. Rajesh Verma",
            "expertise": "Agricultural Economics",
            "qualification": "Professor, Agricultural University",
            "topic": "Market Analysis & Pricing",
            "advice": "Understanding market trends and timing your sales can significantly impact your profits. Keep track of seasonal price patterns and government procurement policies. Consider value addition to increase profitability.",
            "tips": [
                "Monitor market prices regularly",
                "Time your sales based on demand patterns",
                "Explore value addition opportunities",
                "Build relationships with buyers"
            ],
            "image": "expert2.jpg",
            "date": "2024-12-22"
        },
        {
            "id": 3,
            "expert_name": "Dr. Amit Kumar",
            "expertise": "Plant Pathology",
            "qualification": "Senior Scientist, ICAR",
            "topic": "Disease Prevention",
            "advice": "Prevention is better than cure in plant disease management. Use disease-resistant varieties, maintain proper spacing, and ensure good air circulation. Regular monitoring helps in early detection and control.",
            "tips": [
                "Choose disease-resistant crop varieties",
                "Maintain proper plant spacing",
                "Ensure good air circulation",
                "Monitor crops regularly for early detection"
            ],
            "image": "expert3.jpg",
            "date": "2024-12-20"
        },
        {
            "id": 4,
            "expert_name": "Smt. Geeta Reddy",
            "expertise": "Organic Farming",
            "qualification": "Certified Organic Farmer & Trainer",
            "topic": "Organic Farming Transition",
            "advice": "Transitioning to organic farming requires patience and proper planning. Start with a small area and gradually expand. Focus on building soil health and learning natural pest control methods.",
            "tips": [
                "Start with a small area for organic farming",
                "Focus on soil health improvement",
                "Learn natural pest control methods",
                "Be patient during the transition period"
            ],
            "image": "expert4.jpg",
            "date": "2024-12-18"
        }
    ],
    "qa_posts": [
        {
            "id": 1,
            "question": "How to control whitefly in cotton crop?",
            "asked_by": "Farmer123",
            "location": "Punjab",
            "date": "2024-12-28",
            "category": "Pest Management",
            "answers": [
                {
                    "id": 1,
                    "answered_by": "Expert_Farmer",
                    "answer": "Use neem oil spray (2%) every 10 days. Also, plant marigold as border crop to attract natural predators. Yellow sticky traps are also effective.",
                    "votes": 15,
                    "date": "2024-12-28"
                },
                {
                    "id": 2,
                    "answered_by": "Dr_Plant_Health",
                    "answer": "Consider using Beauveria bassiana (bio-pesticide) for organic control. Maintain proper spacing and avoid over-fertilization which attracts whiteflies.",
                    "votes": 12,
                    "date": "2024-12-28"
                }
            ],
            "tags": ["cotton", "whitefly", "pest-control"]
        },
        {
            "id": 2,
            "question": "Best time to sow wheat in Uttar Pradesh?",
            "asked_by": "UP_Farmer",
            "location": "Uttar Pradesh",
            "date": "2024-12-27",
            "category": "Crop Timing",
            "answers": [
                {
                    "id": 3,
                    "answered_by": "Wheat_Expert",
                    "answer": "Optimal time is November 15-25 for timely sown wheat. For late sown, December 15-25 is acceptable. Ensure soil moisture is adequate.",
                    "votes": 23,
                    "date": "2024-12-27"
                }
            ],
            "tags": ["wheat", "sowing", "timing"]
        },
        {
            "id": 3,
            "question": "How to increase soil organic matter naturally?",
            "asked_by": "Organic_Learner",
            "location": "Karnataka",
            "date": "2024-12-26",
            "category": "Soil Management",
            "answers": [
                {
                    "id": 4,
                    "answered_by": "Soil_Scientist",
                    "answer": "Add farmyard manure, compost, green manure crops, and crop residues. Practice crop rotation and avoid burning crop stubble.",
                    "votes": 18,
                    "date": "2024-12-26"
                },
                {
                    "id": 5,
                    "answered_by": "Vermicompost_Expert",
                    "answer": "Start vermicomposting with earthworms. It's the fastest way to increase organic matter. Use kitchen waste and crop residues.",
                    "votes": 14,
                    "date": "2024-12-26"
                }
            ],
            "tags": ["soil", "organic-matter", "composting"]
        }
    ],
    "events": [
        {
            "id": 1,
            "title": "Organic Farming Workshop",
            "description": "Learn organic farming techniques, certification process, and market opportunities.",
            "date": "2025-01-15",
            "time": "10:00 AM",
            "location": "Agricultural University, Ludhiana",
            "organizer": "Punjab Agricultural University",
            "type": "Workshop",
            "registration_required": True,
            "max_participants": 50
        },
        {
            "id": 2,
            "title": "Farmer's Market Day",
            "description": "Direct selling opportunity for farmers. Meet consumers and other farmers.",
            "date": "2025-01-20",
            "time": "8:00 AM",
            "location": "City Center, Chandigarh",
            "organizer": "Local Farmer's Association",
            "type": "Market",
            "registration_required": False,
            "max_participants": 100
        },
        {
            "id": 3,
            "title": "Agricultural Technology Exhibition",
            "description": "Latest farming equipment, irrigation systems, and agricultural technologies on display.",
            "date": "2025-02-05",
            "time": "9:00 AM",
            "location": "Exhibition Ground, Delhi",
            "organizer": "Ministry of Agriculture",
            "type": "Exhibition",
            "registration_required": True,
            "max_participants": 200
        }
    ]
}

# Community functions
def get_forum_posts(forum_id=None):
    """Get forum posts and discussions"""
    if forum_id:
        # Return specific forum posts (simplified for demo)
        return {
            "forum": next((f for f in COMMUNITY_DATA["forums"] if f["id"] == forum_id), None),
            "posts": [
                {
                    "id": 1,
                    "title": "Best organic pest control methods",
                    "author": "Organic_Farmer",
                    "content": "Share your experiences with natural pest control methods...",
                    "date": "2024-12-28",
                    "replies": 8,
                    "views": 45
                }
            ]
        }
    return COMMUNITY_DATA["forums"]

def get_success_stories(story_id=None):
    """Get farmer success stories"""
    if story_id:
        return next((s for s in COMMUNITY_DATA["success_stories"] if s["id"] == story_id), None)
    return COMMUNITY_DATA["success_stories"]

def get_expert_advice(advice_id=None):
    """Get expert advice and tips"""
    if advice_id:
        return next((a for a in COMMUNITY_DATA["expert_advice"] if a["id"] == advice_id), None)
    return COMMUNITY_DATA["expert_advice"]

def get_qa_posts(post_id=None):
    """Get Q&A posts"""
    if post_id:
        return next((q for q in COMMUNITY_DATA["qa_posts"] if q["id"] == post_id), None)
    return COMMUNITY_DATA["qa_posts"]

def get_events(event_id=None):
    """Get community events"""
    if event_id:
        return next((e for e in COMMUNITY_DATA["events"] if e["id"] == event_id), None)
    return COMMUNITY_DATA["events"]

def search_community(query, category=None):
    """Search community content"""
    results = {
        "forums": [],
        "success_stories": [],
        "qa_posts": [],
        "expert_advice": []
    }
    
    query_lower = query.lower()
    
    # Search forums
    for forum in COMMUNITY_DATA["forums"]:
        if (query_lower in forum["title"].lower() or 
            query_lower in forum["description"].lower() or
            any(query_lower in tag.lower() for tag in forum["tags"])):
            results["forums"].append(forum)
    
    # Search success stories
    for story in COMMUNITY_DATA["success_stories"]:
        if (query_lower in story["crop"].lower() or
            query_lower in story["story"].lower() or
            any(query_lower in tip.lower() for tip in story["tips"])):
            results["success_stories"].append(story)
    
    # Search Q&A
    for qa in COMMUNITY_DATA["qa_posts"]:
        if (query_lower in qa["question"].lower() or
            any(query_lower in tag.lower() for tag in qa["tags"])):
            results["qa_posts"].append(qa)
    
    # Search expert advice
    for advice in COMMUNITY_DATA["expert_advice"]:
        if (query_lower in advice["topic"].lower() or
            query_lower in advice["advice"].lower()):
            results["expert_advice"].append(advice)
    
    return results

@app.route('/api/community/forums')
def api_community_forums():
    """Get community forums"""
    forum_id = request.args.get('id', type=int)
    forums = get_forum_posts(forum_id)
    return jsonify({"forums": forums})

@app.route('/api/community/success-stories')
def api_success_stories():
    """Get farmer success stories"""
    story_id = request.args.get('id', type=int)
    stories = get_success_stories(story_id)
    return jsonify({"stories": stories})

@app.route('/api/community/expert-advice')
def api_expert_advice():
    """Get expert advice"""
    advice_id = request.args.get('id', type=int)
    advice = get_expert_advice(advice_id)
    return jsonify({"advice": advice})

@app.route('/api/community/qa')
def api_qa_posts():
    """Get Q&A posts"""
    post_id = request.args.get('id', type=int)
    posts = get_qa_posts(post_id)
    return jsonify({"qa_posts": posts})

@app.route('/api/community/events')
def api_community_events():
    """Get community events"""
    event_id = request.args.get('id', type=int)
    events = get_events(event_id)
    return jsonify({"events": events})

@app.route('/api/community/search')
def api_community_search():
    """Search community content"""
    query = request.args.get('q', '')
    category = request.args.get('category')
    
    if not query:
        return jsonify({"error": "Search query required"}), 400
    
    results = search_community(query, category)
    return jsonify({"results": results, "query": query})

@app.route('/api/community/stats')
def api_community_stats():
    """Get community statistics"""
    stats = {
        "total_forums": len(COMMUNITY_DATA["forums"]),
        "total_success_stories": len(COMMUNITY_DATA["success_stories"]),
        "total_experts": len(COMMUNITY_DATA["expert_advice"]),
        "total_qa_posts": len(COMMUNITY_DATA["qa_posts"]),
        "total_events": len(COMMUNITY_DATA["events"]),
        "active_members": 1247,
        "total_posts": 892,
        "top_categories": ["Pest Management", "Soil Health", "Market Strategies", "Organic Farming"]
    }
    return jsonify({"stats": stats})

@app.route('/api/test-images')
def test_images():
    """Test endpoint to verify image paths"""
    import os
    image_dir = 'static/images'
    images = []
    if os.path.exists(image_dir):
        for filename in os.listdir(image_dir):
            if filename.endswith('.png'):
                images.append(filename)
    return jsonify({"images": images, "count": len(images)})

if __name__ == "__main__":
    app.run(debug=True)