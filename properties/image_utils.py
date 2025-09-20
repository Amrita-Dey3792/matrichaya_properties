import os
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from io import BytesIO


def resize_image(image_file, target_width=1200, target_height=650, quality=85):
    """
    Resize an image to the specified dimensions while maintaining aspect ratio.
    The image will be resized to fit within the target dimensions and then cropped to exact size.
    
    Args:
        image_file: Django uploaded file object
        target_width: Target width in pixels (default: 1200)
        target_height: Target height in pixels (default: 650)
        quality: JPEG quality (default: 85)
    
    Returns:
        ContentFile: Processed image as ContentFile
    """
    try:
        # Open the image
        img = Image.open(image_file)
        
        # Convert to RGB if necessary (handles RGBA, P, etc.)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Calculate the scaling factor to fit the image within target dimensions
        width_ratio = target_width / img.width
        height_ratio = target_height / img.height
        
        # Use the larger ratio to ensure the image covers the entire target area
        scale_ratio = max(width_ratio, height_ratio)
        
        # Calculate new dimensions
        new_width = int(img.width * scale_ratio)
        new_height = int(img.height * scale_ratio)
        
        # Resize the image
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Calculate crop box to center the image
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        # Crop the image to exact target dimensions
        img_cropped = img_resized.crop((left, top, right, bottom))
        
        # Save to BytesIO
        output = BytesIO()
        img_cropped.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        # Create ContentFile
        return ContentFile(output.getvalue(), name=image_file.name)
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        # Return original file if processing fails
        return image_file


def delete_image_file(image_path):
    """
    Delete an image file from storage.
    
    Args:
        image_path: Path to the image file
    """
    try:
        if image_path and default_storage.exists(image_path):
            default_storage.delete(image_path)
            print(f"Deleted image: {image_path}")
    except Exception as e:
        print(f"Error deleting image {image_path}: {str(e)}")


def get_image_dimensions(image_file):
    """
    Get the dimensions of an image file.
    
    Args:
        image_file: Image file object
    
    Returns:
        tuple: (width, height) or (None, None) if error
    """
    try:
        img = Image.open(image_file)
        return img.size
    except Exception as e:
        print(f"Error getting image dimensions: {str(e)}")
        return None, None


