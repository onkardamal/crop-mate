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
import random
from datetime import datetime, timedelta

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

# Live market data simulation
class LiveMarketData:
    def __init__(self):
        self.base_prices = {
            "Rice": 2800,
            "Wheat": 2200,
            "Cotton": 6500,
            "Sugarcane": 315,
            "Maize": 1800,
            "Pulses": 4500,
            "Oilseeds": 5200,
            "Vegetables": 2500,
            "Fruits": 3500
        }
        self.last_update = datetime.now()
        self.price_history = {}
        self.initialize_history()
    
    def initialize_history(self):
        """Initialize price history for all crops"""
        for crop in self.base_prices.keys():
            self.price_history[crop] = []
            base_price = self.base_prices[crop]
            
            # Generate 5 months of historical data
            for i in range(5):
                month_ago = datetime.now() - timedelta(days=30 * (5-i))
                # Add some realistic variation
                variation = random.uniform(-0.1, 0.1)  # ±10% variation
                price = int(base_price * (1 + variation))
                
                self.price_history[crop].append({
                    "date": month_ago.strftime("%Y-%m"),
                    "price": price
                })
    
    def get_live_price(self, crop_name):
        """Get current live price with realistic variations"""
        if crop_name not in self.base_prices:
            return None
        
        base_price = self.base_prices[crop_name]
        
        # Simulate market volatility
        current_hour = datetime.now().hour
        
        # Different volatility patterns throughout the day
        if 9 <= current_hour <= 17:  # Market hours - higher volatility
            variation = random.uniform(-0.05, 0.05)  # ±5% during market hours
        else:  # Off hours - lower volatility
            variation = random.uniform(-0.02, 0.02)  # ±2% off hours
        
        # Add some trend-based variation
        trend_factor = random.choice([-0.02, -0.01, 0, 0.01, 0.02])
        
        live_price = int(base_price * (1 + variation + trend_factor))
        return max(live_price, int(base_price * 0.8))  # Ensure price doesn't drop too much
    
    def get_live_trend(self, crop_name):
        """Get live trend based on recent price movements"""
        if crop_name not in self.price_history:
            return "stable", 0
        
        recent_prices = self.price_history[crop_name][-3:]  # Last 3 months
        if len(recent_prices) < 2:
            return "stable", 0
        
        old_price = recent_prices[0]["price"]
        new_price = recent_prices[-1]["price"]
        
        change_percent = ((new_price - old_price) / old_price) * 100
        
        if change_percent > 3:
            return "increasing", round(change_percent, 1)
        elif change_percent < -3:
            return "decreasing", round(change_percent, 1)
        else:
            return "stable", round(change_percent, 1)
    
    def update_prices(self):
        """Update all prices with live data"""
        updated_data = {}
        
        for crop_name in self.base_prices.keys():
            live_price = self.get_live_price(crop_name)
            trend, change_percent = self.get_live_trend(crop_name)
            
            # Update price history
            current_month = datetime.now().strftime("%Y-%m")
            if not self.price_history[crop_name] or self.price_history[crop_name][-1]["date"] != current_month:
                self.price_history[crop_name].append({
                    "date": current_month,
                    "price": live_price
                })
                # Keep only last 6 months
                if len(self.price_history[crop_name]) > 6:
                    self.price_history[crop_name] = self.price_history[crop_name][-6:]
            
            # Determine volatility based on price stability
            price_variations = [abs(p["price"] - live_price) for p in self.price_history[crop_name][-3:]]
            avg_variation = sum(price_variations) / len(price_variations) if price_variations else 0
            variation_percent = (avg_variation / live_price) * 100
            
            if variation_percent < 5:
                volatility = "low"
            elif variation_percent < 10:
                volatility = "medium"
            elif variation_percent < 15:
                volatility = "high"
            else:
                volatility = "very_high"
            
            updated_data[crop_name] = {
                "current_price": live_price,
                "unit": "per quintal",
                "trend": trend,
                "change_percent": change_percent,
                "price_history": self.price_history[crop_name][-5:],  # Last 5 months
                "seasonal_pattern": MARKET_DATA[crop_name]["seasonal_pattern"],
                "demand_factors": MARKET_DATA[crop_name]["demand_factors"],
                "supply_factors": MARKET_DATA[crop_name]["supply_factors"],
                "market_centers": MARKET_DATA[crop_name]["market_centers"],
                "export_markets": MARKET_DATA[crop_name]["export_markets"],
                "min_support_price": MARKET_DATA[crop_name]["min_support_price"],
                "max_price": MARKET_DATA[crop_name]["max_price"],
                "volatility": volatility,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        self.last_update = datetime.now()
        return updated_data

# Initialize live market data
live_market = LiveMarketData()

@app.route('/api/market/trends')
def api_market_trends():
    """Get live market trends for all crops or specific crop"""
    crop_name = request.args.get('crop')
    period = request.args.get('period', '6months')
    
    # Get live data
    live_data = live_market.update_prices()
    
    if crop_name:
        if crop_name in live_data:
            return jsonify({"trends": live_data[crop_name]})
        else:
            return jsonify({"error": "Crop not found"}), 404
    
    return jsonify({"trends": live_data})

@app.route('/api/market/live-update')
def api_live_update():
    """Get live market update with timestamp"""
    live_data = live_market.update_prices()
    
    return jsonify({
        "live_data": live_data,
        "last_updated": live_market.last_update.strftime("%Y-%m-%d %H:%M:%S"),
        "next_update": (live_market.last_update + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    })

if __name__ == "__main__":
    app.run(debug=True)