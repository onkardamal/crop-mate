from flask import Flask, request, render_template, jsonify
import numpy as np
import pandas as pd
import sklearn
import pickle
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

# Load models and scalers
try:
    model = pickle.load(open('model.pkl', 'rb'))
    sc = pickle.load(open('standscaler.pkl', 'rb'))
    mx = pickle.load(open('minmaxscaler.pkl', 'rb'))
except Exception as e:
    print(f"Error loading models: {str(e)}")
    raise

# Crop information dictionary
CROP_INFO = {
    "Rice": {
        "description": "Rice is a staple food crop that requires warm temperatures and plenty of water.",
        "growing_tips": ["Maintain water level at 2-3 inches", "Plant in well-drained soil", "Requires full sun"],
        "growing_season": "Summer (June-September)",
        "water_requirements": "High (needs standing water)",
        "soil_type": "Clay loam, alluvial soil",
        "expected_yield": "3-6 tons per hectare",
        "market_price": "₹25,000-42,000 per ton",
        "regions": ["West Bengal", "Uttar Pradesh", "Punjab", "Andhra Pradesh", "Odisha", "Chhattisgarh", "Tamil Nadu", "Bihar", "Assam", "Kerala"],
        "image": "rice.png"
    },
    "Maize": {
        "description": "Maize is a versatile crop that can be used for food, feed, and industrial purposes.",
        "growing_tips": ["Plant in warm soil", "Space plants 8-12 inches apart", "Requires regular watering"],
        "growing_season": "Spring to Summer",
        "water_requirements": "Moderate (25-30 inches per season)",
        "soil_type": "Well-drained loamy soil",
        "expected_yield": "8-12 tons per hectare",
        "market_price": "₹16,000-25,000 per ton",
        "regions": ["Karnataka", "Madhya Pradesh", "Maharashtra", "Rajasthan", "Uttar Pradesh", "Bihar", "Himachal Pradesh", "Telangana"],
        "image": "maize.png"
    },
    "Jute": {
        "description": "Jute is a long, soft, shiny vegetable fiber that can be spun into coarse, strong threads.",
        "growing_tips": ["Requires warm and humid climate", "Sow in loamy soil", "Needs plenty of water"],
        "growing_season": "March to May",
        "water_requirements": "High (plenty of water)",
        "soil_type": "Loamy, alluvial soil",
        "expected_yield": "2-3 tons per hectare",
        "market_price": "₹33,000-50,000 per ton",
        "regions": ["West Bengal", "Bihar", "Assam", "Odisha", "Meghalaya"],
        "image": "jute.png"
    },
    "Cotton": {
        "description": "Cotton is a fiber crop that requires warm temperatures and moderate rainfall.",
        "growing_tips": ["Plant in warm soil", "Requires full sun", "Needs well-drained soil"],
        "growing_season": "Spring to Fall",
        "water_requirements": "Moderate to High (20-25 inches per season)",
        "soil_type": "Black soil, alluvial soil",
        "expected_yield": "2-3 bales per acre",
        "market_price": "₹120-150 per kg",
        "regions": ["Maharashtra", "Gujarat", "Telangana", "Andhra Pradesh", "Punjab", "Haryana", "Madhya Pradesh", "Karnataka", "Rajasthan"],
        "image": "cotton.png"
    },
    "Coconut": {
        "description": "Coconut is a tropical crop grown for its fruit and oil.",
        "growing_tips": ["Plant in sandy soil", "Requires high humidity", "Needs regular irrigation"],
        "growing_season": "Year-round in tropics",
        "water_requirements": "High",
        "soil_type": "Sandy, well-drained soil",
        "expected_yield": "10,000-14,000 nuts per hectare",
        "market_price": "₹15,000-22,000 per 1000 nuts",
        "regions": ["Kerala", "Tamil Nadu", "Karnataka", "Andhra Pradesh", "West Bengal", "Odisha", "Goa", "Maharashtra"],
        "image": "coconut.png"
    },
    "Papaya": {
        "description": "Papaya is a tropical fruit crop known for its sweet taste and nutritional value.",
        "growing_tips": ["Plant in well-drained soil", "Requires warm climate", "Irrigate regularly"],
        "growing_season": "Spring to Summer",
        "water_requirements": "Moderate",
        "soil_type": "Loamy, well-drained soil",
        "expected_yield": "40-60 tons per hectare",
        "market_price": "₹20,000-40,000 per ton",
        "regions": ["Andhra Pradesh", "Gujarat", "Maharashtra", "Karnataka", "West Bengal", "Assam", "Kerala", "Tamil Nadu"],
        "image": "papaya.png"
    },
    "Orange": {
        "description": "Orange is a citrus fruit crop grown in subtropical and tropical climates.",
        "growing_tips": ["Plant in well-drained soil", "Requires full sun", "Irrigate during dry periods"],
        "growing_season": "Winter to Spring",
        "water_requirements": "Moderate",
        "soil_type": "Sandy loam, well-drained",
        "expected_yield": "20-30 tons per hectare",
        "market_price": "₹30,000-50,000 per ton",
        "regions": ["Maharashtra", "Madhya Pradesh", "Punjab", "Rajasthan", "Assam", "Nagaland", "Meghalaya"],
        "image": "orange.png"
    },
    "Apple": {
        "description": "Apple is a temperate fruit crop grown in cool climates.",
        "growing_tips": ["Plant in well-drained soil", "Requires chilling hours", "Prune trees regularly"],
        "growing_season": "Spring to Fall",
        "water_requirements": "Moderate",
        "soil_type": "Loamy, well-drained soil",
        "expected_yield": "20-40 tons per hectare",
        "market_price": "₹60,000-100,000 per ton",
        "regions": ["Jammu and Kashmir", "Himachal Pradesh", "Uttarakhand"],
        "image": "apple.png"
    },
    "Muskmelon": {
        "description": "Muskmelon is a sweet, juicy fruit grown in warm climates.",
        "growing_tips": ["Plant in sandy loam soil", "Requires full sun", "Irrigate moderately"],
        "growing_season": "Summer",
        "water_requirements": "Moderate",
        "soil_type": "Sandy loam",
        "expected_yield": "15-20 tons per hectare",
        "market_price": "₹20,000-40,000 per ton",
        "regions": ["Uttar Pradesh", "Punjab", "Haryana", "Rajasthan", "Madhya Pradesh", "Maharashtra", "Gujarat"],
        "image": "muskmelon.png"
    },
    "Watermelon": {
        "description": "Watermelon is a large, juicy fruit crop grown in warm climates.",
        "growing_tips": ["Plant in sandy loam soil", "Requires full sun", "Irrigate regularly"],
        "growing_season": "Summer",
        "water_requirements": "High",
        "soil_type": "Sandy loam",
        "expected_yield": "20-40 tons per hectare",
        "market_price": "₹16,000-33,000 per ton",
        "regions": ["Uttar Pradesh", "Madhya Pradesh", "Rajasthan", "Maharashtra", "Karnataka", "Tamil Nadu", "West Bengal"],
        "image": "watermelon.png"
    },
    "Grapes": {
        "description": "Grapes are a fruit crop grown for eating and wine production.",
        "growing_tips": ["Plant in well-drained soil", "Requires pruning", "Irrigate during dry periods"],
        "growing_season": "Spring to Summer",
        "water_requirements": "Moderate",
        "soil_type": "Sandy loam, well-drained",
        "expected_yield": "10-20 tons per hectare",
        "market_price": "₹80,000-160,000 per ton",
        "regions": ["Maharashtra", "Karnataka", "Tamil Nadu", "Mizoram", "Punjab"],
        "image": "grapes.png"
    },
    "Mango": {
        "description": "Mango is a tropical fruit crop known for its sweet flavor.",
        "growing_tips": ["Plant in well-drained soil", "Requires full sun", "Irrigate during dry periods"],
        "growing_season": "Spring to Summer",
        "water_requirements": "Moderate",
        "soil_type": "Loamy, well-drained soil",
        "expected_yield": "10-20 tons per hectare",
        "market_price": "₹40,000-80,000 per ton",
        "regions": ["Uttar Pradesh", "Andhra Pradesh", "Karnataka", "Bihar", "Gujarat", "Tamil Nadu", "West Bengal"],
        "image": "mango.png"
    },
    "Banana": {
        "description": "Banana is a tropical fruit crop grown for its edible fruit.",
        "growing_tips": ["Plant in rich, well-drained soil", "Requires high humidity", "Irrigate regularly"],
        "growing_season": "Year-round in tropics",
        "water_requirements": "High",
        "soil_type": "Rich, well-drained soil",
        "expected_yield": "30-40 tons per hectare",
        "market_price": "₹20,000-40,000 per ton",
        "regions": ["Tamil Nadu", "Maharashtra", "Gujarat", "Andhra Pradesh", "Karnataka", "Assam", "Madhya Pradesh", "West Bengal"],
        "image": "banana.png"
    },
    "Pomegranate": {
        "description": "Pomegranate is a fruit crop known for its juicy seeds.",
        "growing_tips": ["Plant in loamy soil", "Requires full sun", "Irrigate moderately"],
        "growing_season": "Spring to Summer",
        "water_requirements": "Low to Moderate",
        "soil_type": "Loamy, well-drained soil",
        "expected_yield": "10-15 tons per hectare",
        "market_price": "₹60,000-100,000 per ton",
        "regions": ["Maharashtra", "Karnataka", "Gujarat", "Andhra Pradesh", "Tamil Nadu", "Rajasthan"],
        "image": "pomegranate.png"
    },
    "Lentil": {
        "description": "Lentil is a pulse crop grown for its edible seeds.",
        "growing_tips": ["Plant in cool season", "Requires well-drained soil", "Irrigate moderately"],
        "growing_season": "Winter to Spring",
        "water_requirements": "Low to Moderate",
        "soil_type": "Loamy, well-drained soil",
        "expected_yield": "1-2 tons per hectare",
        "market_price": "₹50,000-75,000 per ton",
        "regions": ["Madhya Pradesh", "Uttar Pradesh", "Bihar", "West Bengal", "Rajasthan", "Maharashtra"],
        "image": "lentil.png"
    },
    "Blackgram": {
        "description": "Blackgram is a pulse crop grown for its edible seeds.",
        "growing_tips": ["Plant in warm season", "Requires well-drained soil", "Irrigate moderately"],
        "growing_season": "Summer to Fall",
        "water_requirements": "Low to Moderate",
        "soil_type": "Loamy, well-drained soil",
        "expected_yield": "0.8-1.2 tons per hectare",
        "market_price": "₹55,000-80,000 per ton",
        "regions": ["Uttar Pradesh", "Madhya Pradesh", "Tamil Nadu", "Andhra Pradesh", "Karnataka", "Maharashtra"],
        "image": "blackgram.png"
    },
    "Mungbean": {
        "description": "Mungbean is a pulse crop grown for its edible seeds.",
        "growing_tips": ["Plant in warm season", "Requires well-drained soil", "Irrigate moderately"],
        "growing_season": "Summer to Fall",
        "water_requirements": "Low to Moderate",
        "soil_type": "Loamy, well-drained soil",
        "expected_yield": "0.8-1.2 tons per hectare",
        "market_price": "₹55,000-80,000 per ton",
        "regions": ["Rajasthan", "Maharashtra", "Karnataka", "Andhra Pradesh", "Tamil Nadu", "Uttar Pradesh"],
        "image": "mungbean.png"
    },
    "Mothbeans": {
        "description": "Mothbeans are a drought-resistant legume crop.",
        "growing_tips": ["Plant in arid regions", "Requires minimal irrigation", "Grows in sandy soil"],
        "growing_season": "Summer",
        "water_requirements": "Low",
        "soil_type": "Sandy, well-drained soil",
        "expected_yield": "0.5-1.0 tons per hectare",
        "market_price": "₹45,000-70,000 per ton",
        "regions": ["Rajasthan", "Gujarat", "Madhya Pradesh", "Uttar Pradesh"],
        "image": "mothbeans.png"
    },
    "Pigeonpeas": {
        "description": "Pigeonpeas are a legume crop grown for their edible seeds.",
        "growing_tips": ["Plant in warm season", "Requires well-drained soil", "Irrigate moderately"],
        "growing_season": "Summer to Fall",
        "water_requirements": "Low to Moderate",
        "soil_type": "Loamy, well-drained soil",
        "expected_yield": "1-2 tons per hectare",
        "market_price": "₹55,000-80,000 per ton",
        "regions": ["Maharashtra", "Karnataka", "Uttar Pradesh", "Madhya Pradesh", "Gujarat", "Andhra Pradesh"],
        "image": "pigeonpeas.png"
    },
    "Kidneybeans": {
        "description": "Kidneybeans are a legume crop grown for their edible seeds.",
        "growing_tips": ["Plant in cool season", "Requires well-drained soil", "Irrigate moderately"],
        "growing_season": "Spring to Summer",
        "water_requirements": "Moderate",
        "soil_type": "Loamy, well-drained soil",
        "expected_yield": "1-2 tons per hectare",
        "market_price": "₹60,000-100,000 per ton",
        "regions": ["Uttarakhand", "Jammu and Kashmir", "Himachal Pradesh", "West Bengal", "Assam"],
        "image": "kidneybeans.png"
    },
    "Chickpea": {
        "description": "Chickpea is a pulse crop grown for its edible seeds.",
        "growing_tips": ["Plant in cool season", "Requires well-drained soil", "Irrigate moderately"],
        "growing_season": "Winter to Spring",
        "water_requirements": "Low to Moderate",
        "soil_type": "Loamy, well-drained soil",
        "expected_yield": "1-2 tons per hectare",
        "market_price": "₹55,000-80,000 per ton",
        "regions": ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Uttar Pradesh", "Karnataka", "Andhra Pradesh"],
        "image": "chickpea.png"
    },
    "Coffee": {
        "description": "Coffee is a tropical crop that requires specific climate conditions.",
        "growing_tips": ["Plant in shade", "Maintain soil pH 6-6.5", "Requires regular pruning"],
        "growing_season": "Year-round in tropical regions",
        "water_requirements": "Moderate (60-100 inches annually)",
        "soil_type": "Volcanic soil, well-drained",
        "expected_yield": "1-2 tons per hectare",
        "market_price": "₹350-600 per kg",
        "regions": ["Karnataka", "Kerala", "Tamil Nadu"],
        "image": "coffee.png"
    }
}

def validate_input(data):
    """Validate input data ranges"""
    ranges = {
        'Nitrogen': (0, 140),
        'Phosporus': (0, 145),
        'Potassium': (0, 205),
        'Temperature': (8.0, 44.0),
        'Humidity': (14.0, 100.0),
        'pH': (3.5, 10.0),
        'Rainfall': (20.0, 300.0)
    }
    
    for key, (min_val, max_val) in ranges.items():
        try:
            value = float(data[key])
            if not min_val <= value <= max_val:
                return False, f"{key} should be between {min_val} and {max_val}"
        except (ValueError, KeyError):
            return False, f"Invalid {key} value"
    return True, ""

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/predict", methods=['POST'])
def predict():
    try:
        # Get form data
        data = {
            'Nitrogen': request.form['Nitrogen'],
            'Phosporus': request.form['Phosporus'],
            'Potassium': request.form['Potassium'],
            'Temperature': request.form['Temperature'],
            'Humidity': request.form['Humidity'],
            'pH': request.form['pH'],
            'Rainfall': request.form['Rainfall']
        }
        
        # Validate input
        is_valid, error_message = validate_input(data)
        if not is_valid:
            return render_template('index.html', error=error_message)
        
        # Prepare features
        feature_list = [float(data[key]) for key in data.keys()]
        single_pred = np.array(feature_list).reshape(1, -1)
        
        # Transform and predict
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
            return render_template('index.html', 
                                result=f"{crop} is the best crop to be cultivated right there",
                                crop_details=crop_details)
        else:
            return render_template('index.html', 
                                error="Sorry, we could not determine the best crop to be cultivated with the provided data.")
            
    except Exception as e:
        return render_template('index.html', error=f"An error occurred: {str(e)}")

@app.route('/compare')
def compare():
    return render_template('compare.html')

@app.route('/api/crops')
def get_crops():
    crops = []
    for name, info in CROP_INFO.items():
        crop_data = {
            'name': name,
            **info
        }
        crops.append(crop_data)
    return jsonify(crops)

@app.route('/recommend')
def recommend():
    return render_template('recommend.html')

@app.route('/profitability')
def profitability():
    return render_template('profitability.html')

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

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

if __name__ == "__main__":
    app.run(debug=True)