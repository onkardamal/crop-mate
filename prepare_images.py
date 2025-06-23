from PIL import Image
import os
import sys

def prepare_image(input_path, output_path, size=(300, 300)):
    """
    Prepare an image by resizing and optimizing it.
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save processed image
        size (tuple): Target size (width, height)
    """
    try:
        # Open the image
        with Image.open(input_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize image maintaining aspect ratio
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Create new image with white background
            new_img = Image.new('RGB', size, (255, 255, 255))
            
            # Calculate position to center the image
            offset = ((size[0] - img.size[0]) // 2,
                     (size[1] - img.size[1]) // 2)
            
            # Paste the resized image onto the white background
            new_img.paste(img, offset)
            
            # Save the optimized image
            new_img.save(output_path, 'PNG', optimize=True, quality=85)
            
            print(f"Successfully processed: {os.path.basename(output_path)}")
            
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")

def main():
    # Create output directory if it doesn't exist
    output_dir = "static/images"
    os.makedirs(output_dir, exist_ok=True)
    
    # List of required crop images
    required_crops = [
        "rice", "maize", "jute", "cotton", "coconut", "papaya", "orange",
        "apple", "muskmelon", "watermelon", "grapes", "mango", "banana",
        "pomegranate", "lentil", "blackgram", "mungbean", "mothbeans",
        "pigeonpeas", "kidneybeans", "chickpea", "coffee"
    ]
    
    if len(sys.argv) < 2:
        print("Usage: python prepare_images.py <input_directory>")
        print("\nThe input directory should contain your crop images.")
        print("The script will process all images and save them in static/images/")
        print("\nExample: python prepare_images.py ./my_crop_images/")
        return
    
    input_dir = sys.argv[1]
    
    # Process each required crop
    for crop in required_crops:
        # Look for the image in the input directory
        input_path = None
        for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            possible_path = os.path.join(input_dir, f"{crop}{ext}")
            if os.path.exists(possible_path):
                input_path = possible_path
                break
        
        if input_path:
            output_path = os.path.join(output_dir, f"{crop}.png")
            prepare_image(input_path, output_path)
        else:
            print(f"Warning: No image found for {crop}")

if __name__ == "__main__":
    main() 