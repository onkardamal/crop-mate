# CropMate 🌱

**Your all-in-one digital companion for smarter, more profitable, and sustainable farming.**

CropMate is a comprehensive web application that uses machine learning to help farmers make informed decisions about crop selection, comparison, and farming practices. Built with Flask and featuring a modern, responsive UI.

## ✨ Features

### 🌾 Core Features (Fully Working)
- **Crop Recommendation System**: Get personalized crop suggestions based on soil and climate data
- **Crop Comparison Tool**: Compare two crops side-by-side with detailed analytics and interactive maps
- **Comprehensive Crop Database**: 22 crops with detailed information including growing tips, market prices, and regional suitability

### 🚧 Upcoming Features (Placeholder Pages)
- **Profitability Calculator**: Estimate profits for any crop based on area and costs
- **Seasonal Calendar**: Best sowing, growing, and harvesting times for each crop
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

## 🏗️ Project Structure

```
Crop_Recommendation/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── model.pkl             # Trained machine learning model
├── standscaler.pkl       # Standard scaler for data preprocessing
├── minmaxscaler.pkl      # MinMax scaler for data preprocessing
├── Crop_recommendation.csv # Training dataset
├── static/
│   ├── images/           # Crop images
│   └── crop.png          # Default crop image
├── templates/
│   ├── index.html        # Home page
│   ├── recommend.html    # Crop recommendation page
│   ├── compare.html      # Crop comparison page
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

### API Endpoints
- `GET /` - Home page
- `GET /recommend` - Crop recommendation page
- `POST /predict` - Crop prediction API
- `GET /compare` - Crop comparison page
- `GET /api/crops` - List all available crops
- `GET /api/crops/<crop_name>` - Get detailed crop information
- `GET /[feature]` - Various feature pages (profitability, calendar, etc.)

## 🧪 Testing

Run the comprehensive test suite to verify everything is working:

```bash
python test_app.py
```

This will test:
- Server connectivity
- Crop recommendation API
- Crops list API
- Individual crop details API
- All application routes

## 📱 Supported Crops

The application supports 22 different crops:

**Grains & Cereals**: Rice, Maize  
**Fiber Crops**: Jute, Cotton  
**Fruits**: Coconut, Papaya, Orange, Apple, Muskmelon, Watermelon, Grapes, Mango, Banana, Pomegranate  
**Pulses**: Lentil, Blackgram, Mungbean, Mothbeans, Pigeonpeas, Kidneybeans, Chickpea  
**Commercial Crops**: Coffee  

Each crop includes:
- Detailed description and growing tips
- Growing season information
- Water requirements
- Soil type preferences
- Expected yield estimates
- Current market prices (in Indian Rupees)
- Suitable Indian states/regions
- Climate suitability scores
- Profitability metrics

## 🎨 UI/UX Features

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modern Interface**: Clean, intuitive design with Bootstrap 5
- **Interactive Elements**: Tooltips, loading states, hover effects
- **Visual Feedback**: Success/error messages, progress indicators
- **Accessibility**: Proper semantic HTML and ARIA labels
- **Performance**: Optimized loading and smooth interactions

## 🔮 Future Enhancements

The application is designed to be easily extensible. Planned features include:

1. **Real-time Data Integration**: Live weather and market data
2. **Mobile App**: Native iOS and Android applications
3. **Multi-language Support**: Support for regional Indian languages
4. **Advanced Analytics**: Historical data analysis and trend prediction
5. **Farmer Community**: Social features for knowledge sharing
6. **IoT Integration**: Sensor data integration for precision farming

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Dataset: Crop Recommendation Dataset from Kaggle
- Icons: Bootstrap Icons
- Maps: Leaflet.js
- UI Framework: Bootstrap 5

---

**Made with ❤️ for Indian Farmers**

*CropMate - Empowering farmers with data-driven decisions for a sustainable future.*