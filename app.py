from flask import Flask, request, render_template, jsonify
import numpy as np
import pandas as pd
import sklearn
import pickle
from werkzeug.exceptions import BadRequest
import warnings
import re
import datetime
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

if __name__ == "__main__":
    app.run(debug=True)