from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image(crop_name, size=(300, 300), bg_color=(240, 240, 240), text_color=(100, 100, 100)):
    # Create a new image with the specified background color
    image = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(image)
    
    # Add a border
    draw.rectangle([(0, 0), (size[0]-1, size[1]-1)], outline=(200, 200, 200))
    
    # Add crop name text
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()
    
    # Center the text
    text_width = draw.textlength(crop_name, font=font)
    text_position = ((size[0] - text_width) // 2, size[1] // 2 - 15)
    
    # Draw the text
    draw.text(text_position, crop_name, fill=text_color, font=font)
    
    return image

def main():
    # Create static/images directory if it doesn't exist
    os.makedirs('static/images', exist_ok=True)
    
    # List of crops from CROP_INFO
    crops = [
        "Rice", "Maize", "Jute", "Cotton", "Coconut", "Papaya", "Orange",
        "Apple", "Muskmelon", "Watermelon", "Grapes", "Mango", "Banana",
        "Pomegranate", "Lentil", "Blackgram", "Mungbean", "Mothbeans",
        "Pigeonpeas", "Kidneybeans", "Chickpea", "Coffee"
    ]
    
    # Generate placeholder image for each crop
    for crop in crops:
        image = create_placeholder_image(crop)
        image_path = os.path.join('static/images', f'{crop.lower()}.png')
        image.save(image_path)
        print(f'Created placeholder image for {crop}')

if __name__ == '__main__':
    main() 