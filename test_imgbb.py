#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_project.settings')

# Setup Django
django.setup()

from django.core.files.base import ContentFile
from medical_project.imgbb_storage import ImgBBStorage

def test_imgbb():
    print("🧪 Testing ImgBB Storage...")
    
    # Check if API key is available
    api_key = os.environ.get('IMGBB_API_KEY')
    print(f"🔑 API Key: {'✅ Found' if api_key else '❌ Not found'}")
    
    if not api_key:
        print("❌ Please set IMGBB_API_KEY environment variable")
        return
    
    # Create storage instance
    storage = ImgBBStorage()
    print(f"🏗️ Storage instance created: {storage.__class__.__name__}")
    
    # Create a simple test image (1x1 pixel PNG)
    # This is a minimal PNG file in base64
    test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    
    content = ContentFile(test_image_data, name='test_image.png')
    
    try:
        print("📤 Uploading test image...")
        filename = storage._save('test_image.png', content)
        print(f"✅ Upload successful! Filename: {filename}")
        
        # Test URL retrieval
        url = storage.url(filename)
        print(f"🌐 Image URL: {url}")
        
        # Test exists
        exists = storage.exists(filename)
        print(f"📋 File exists: {exists}")
        
        print("🎉 ImgBB storage test completed successfully!")
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")

if __name__ == "__main__":
    test_imgbb()
