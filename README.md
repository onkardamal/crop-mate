# CropMate 🌱

**Your all-in-one digital companion for smarter, more profitable, and sustainable farming.**

CropMate is a comprehensive web application that uses machine learning to help farmers make informed decisions about crop selection, comparison, and farming practices. Built with Flask and featuring a modern, responsive UI.

## ✨ Features

### 🌾 Core Features (Fully Working)
- **Crop Recommendation System**: Get personalized crop suggestions based on soil and climate data
- **Crop Comparison Tool**: Compare two crops side-by-side with detailed analytics and interactive maps
- **Profitability Calculator**: Estimate profits for any crop based on area and costs
- **Seasonal Calendar**: Interactive calendar showing best sowing, growing, and harvesting times for all 22 crops
- **Comprehensive Crop Database**: 22 crops with detailed information including growing tips, market prices, and regional suitability

### 🚧 Upcoming Features (Placeholder Pages)
- **Best Practices**: Farming techniques and problem prevention guides
- **Local Suitability**: Crop recommendations based on your state/district
- **Schemes & Support**: Government schemes, subsidies, and support contacts
- **Market Trends**: Recent price trends to help with selling decisions
- **Community**: Farmer tips, Q&A, and success stories

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Crop_Recommendation
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and go to: `http://localhost:5000`

## 📊 How to Use

### Crop Recommendation
1. Navigate to the "Crop Recommendation" page
2. Enter your soil and climate data:
   - **Nitrogen (N)**: 0-140
   - **Phosphorus (P)**: 0-145
   - **Potassium (K)**: 0-205
   - **Temperature**: 8-44°C
   - **Humidity**: 14-100%
   - **pH Value**: 3.5-10
   - **Rainfall**: 20-300mm
3. Click "Get Recommendation" to receive personalized crop suggestions
4. View detailed information about the recommended crop including growing tips, market prices, and suitable regions

### Crop Comparison
1. Navigate to the "Compare Crops" page
2. Select two different crops from the available options
3. View comprehensive comparison including:
   - Climate suitability scores
   - Soil compatibility data
   - Profitability metrics
   - Interactive map showing crop regions
   - Detailed feature comparison table

### Profitability Calculator
1. Navigate to the "Profitability Calculator" page
2. Select a crop from the dropdown menu
3. Enter your farm area (in hectares) and total costs
4. Get instant calculations showing:
   - Expected yield based on crop type
   - Gross revenue at current market prices
   - Net profit after costs
   - Profit margin percentage

### Seasonal Calendar
1. Navigate to the "Seasonal Calendar" page
2. View the comprehensive calendar showing all 22 crops
3. Filter by:
   - **Show All**: View all crops at once
   - **Season**: Filter by Kharif, Rabi, or Zaid seasons
   - **Month**: Filter by specific months
4. Color-coded activities:
   - 🟢 **Green**: Sowing period
   - 🟡 **Yellow**: Growing period
   - 🔴 **Red**: Harvesting period
5. Current month is highlighted with a blue border
6. Hover over cells to see activity details

## 🏗️ Project Structure

```
Crop_Recommendation/
├── app.py                 # Main Flask application
├── data_loader.py         # Crop information and utility functions
├── utils.py              # Input validation and utility functions
├── requirements.txt       # Python dependencies
├── model.pkl             # Trained machine learning model
├── standscaler.pkl       # Standard scaler for data preprocessing
├── minmaxscaler.pkl      # MinMax scaler for data preprocessing
├── Crop_recommendation.csv # Training dataset
├── test_calendar.py      # Calendar functionality tests
├── test_app.py           # Application tests
├── static/
│   ├── images/           # Crop images (22 crops)
│   └── crop.png          # Default crop image
├── templates/
│   ├── index.html        # Home page
│   ├── recommend.html    # Crop recommendation page
│   ├── compare.html      # Crop comparison page
│   ├── profitability.html # Profitability calculator page
│   ├── calendar.html     # Seasonal calendar page
│   └── [other pages]     # Placeholder pages for upcoming features
└── README.md             # This file
```

## 🔧 Technical Details

### Machine Learning Model
- **Algorithm**: Random Forest Classifier
- **Features**: 7 input parameters (N, P, K, Temperature, Humidity, pH, Rainfall)
- **Output**: Crop recommendation from 22 possible crops
- **Accuracy**: High accuracy trained on comprehensive agricultural dataset

### Technologies Used
- **Backend**: Flask (Python web framework)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Machine Learning**: scikit-learn, numpy, pandas
- **Maps**: Leaflet.js for interactive maps
- **Icons**: Bootstrap Icons
- **Data Processing**: Custom utilities for input validation and data parsing

### API Endpoints
- `GET /` - Home page
- `GET /recommend` - Crop recommendation page
- `POST /predict` - Crop prediction API
- `GET /compare` - Crop comparison page
- `GET /profitability` - Profitability calculator page
- `GET /calendar` - Seasonal calendar page
- `GET /api/crops` - List all available crops
- `GET /api/crops/<crop_name>` - Get detailed crop information
- `GET /api/calendar/season/<season>` - Get crops by season
- `GET /api/calendar/month/<month>` - Get crops by month
- `GET /[feature]` - Various feature pages (practices, suitability, etc.)

## 🧪 Testing

Run the comprehensive test suite to verify everything is working:

```bash
# Test the main application
python test_app.py

# Test calendar functionality specifically
python test_calendar.py
```

These tests verify:
- Server connectivity
- Crop recommendation API
- Crops list API
- Individual crop details API
- Calendar data generation
- Seasonal filtering
- Month range parsing
- All application routes

## 📱 Supported Crops

The application supports 22 different crops with comprehensive data:

**Grains & Cereals**: Rice, Maize  
**Fiber Crops**: Jute, Cotton  
**Fruits**: Coconut, Papaya, Orange, Apple, Muskmelon, Watermelon, Grapes, Mango, Banana, Pomegranate  
**Pulses**: Lentil, Blackgram, Mungbean, Mothbeans, Pigeonpeas, Kidneybeans, Chickpea  
**Commercial Crops**: Coffee  

Each crop includes:
- Detailed description and growing tips
- Growing season information (Kharif/Rabi/Zaid)
- Water requirements
- Soil type preferences
- Expected yield estimates
- Current market prices (in Indian Rupees)
- Suitable Indian states/regions
- Climate suitability scores
- Profitability metrics
- Seasonal calendar data

## 🗓️ Seasonal Calendar Features

The enhanced calendar system provides:

- **Complete Coverage**: All 22 crops included with seasonal data
- **Smart Filtering**: Filter by seasons (Kharif, Rabi, Zaid) or specific months
- **Visual Indicators**: Color-coded activities with activity codes (S, G, H)
- **Cross-Year Ranges**: Proper handling of seasons spanning year boundaries
- **Current Month Highlighting**: Blue border around the current month
- **Responsive Design**: Works perfectly on all device sizes
- **Error Handling**: Graceful handling of API failures with user feedback
- **Loading States**: Visual feedback during data loading

## 🎨 UI/UX Features

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modern Interface**: Clean, intuitive design with Bootstrap 5
- **Interactive Elements**: Tooltips, loading states, hover effects
- **Visual Feedback**: Success/error messages, progress indicators
- **Accessibility**: Proper semantic HTML and ARIA labels
- **Performance**: Optimized loading and smooth interactions
- **Color-Coded Calendar**: Intuitive visual representation of farming activities

## 🔮 Future Enhancements

The application is designed to be easily extensible. Planned features include:

1. **Real-time Data Integration**: Live weather and market data
2. **Mobile App**: Native iOS and Android applications
3. **Multi-language Support**: Support for regional Indian languages
4. **Advanced Analytics**: Historical data analysis and trend prediction
5. **Farmer Community**: Social features for knowledge sharing
6. **IoT Integration**: Sensor data integration for precision farming
7. **Weather Integration**: Real-time weather data for better recommendations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Dataset: Crop Recommendation Dataset from Kaggle
- Icons: Bootstrap Icons
- Maps: Leaflet.js
- UI Framework: Bootstrap 5
- Seasonal Data: Based on Indian agricultural practices

---

**Last Updated**: June 2025  
**Version**: 2.0.0  
**Status**: Production Ready with Enhanced Calendar System