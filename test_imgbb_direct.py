#!/usr/bin/env python
import requests
import base64

def test_imgbb_api():
    """Test ImgBB API directly"""
    api_key = "de45fe1156e0daedb8b744caade9c005"
    api_url = "https://api.imgbb.com/1/upload"
    
    # Create a simple 1x1 pixel PNG for testing
    test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    
    # Encode to base64
    encoded_content = base64.b64encode(test_image_data).decode('utf-8')
    
    print(f"🧪 Testing ImgBB API...")
    print(f"🔑 API Key: {api_key[:10]}...")
    print(f"📦 Image size: {len(test_image_data)} bytes")
    
    # Prepare API request
    data = {
        'key': api_key,
        'image': encoded_content,
        'name': 'test_image_direct',
    }
    
    try:
        # Send request
        response = requests.post(api_url, data=data, timeout=30)
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ SUCCESS! Image uploaded to: {result['data']['url']}")
                return True
            else:
                print(f"❌ API Error: {result}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    test_imgbb_api()
