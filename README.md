# Crop Recommendation System 🌱

A machine learning-based web application that recommends the best crop to cultivate based on soil and climate conditions.

## Features

- 🌡️ Input validation for soil and climate parameters
- 📊 Real-time crop recommendations using machine learning
- 💡 Detailed growing tips for recommended crops
- 🎨 Modern and responsive user interface
- ⚡ Fast and efficient prediction system

## Technologies Used

- Python 3.8+
- Flask (Web Framework)
- scikit-learn (Machine Learning)
- Bootstrap 5 (Frontend)
- HTML5/CSS3/JavaScript

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Crop_Recommendation.git
cd Crop_Recommendation
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Enter the soil and climate parameters:
   - Nitrogen (N) content in soil
   - Phosphorus (P) content in soil
   - Potassium (K) content in soil
   - Temperature (°C)
   - Humidity (%)
   - pH value
   - Rainfall (mm)

4. Click "Get Recommendation" to receive the best crop suggestion for your conditions.

## Input Ranges

- Nitrogen (N): 0-140
- Phosphorus (P): 0-145
- Potassium (K): 0-205
- Temperature: 8-44°C
- Humidity: 14-100%
- pH: 3.5-10
- Rainfall: 20-300 mm

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Dataset source: [Crop Recommendation Dataset](https://www.kaggle.com/datasets/patelris/crop-recommendation-dataset)
- Icons by [Bootstrap Icons](https://icons.getbootstrap.com/)