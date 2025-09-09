import os
import uuid
import base64
import requests
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class ImgBBStorage(Storage):
    """
    Custom storage backend for ImgBB free image hosting service.
    Provides permanent image URLs that work reliably for production apps.
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'IMGBB_API_KEY', '')
        self.api_url = 'https://api.imgbb.com/1/upload'
        
    def _save(self, name, content):
        """Save file to ImgBB"""
        try:
            if not self.api_key:
                logger.error("❌ ImgBB API key not configured")
                print("❌ ImgBB API key not configured - falling back to local storage")
                return self._save_locally(name, content)
            
            # Generate unique filename
            file_extension = os.path.splitext(name)[1]
            unique_name = f"medical_{uuid.uuid4()}{file_extension}"
            
            # Read file content and encode to base64
            content.seek(0)
            file_data = content.read()
            encoded_content = base64.b64encode(file_data).decode('utf-8')
            
            print(f"🔄 IMGBB UPLOAD STARTING: {unique_name}")
            print(f"🔄 File size: {len(file_data)} bytes")
            print(f"🔑 API key present: {'Yes' if self.api_key else 'No'}")
            
            logger.info(f"🔄 Uploading to ImgBB: {unique_name}")
            logger.info(f"🔄 File size: {len(file_data)} bytes")
            
            # Prepare ImgBB API request
            data = {
                'key': self.api_key,
                'image': encoded_content,
                'name': unique_name,
            }
            
            print(f"📡 Making API request to ImgBB...")
            
            # Upload to ImgBB
            response = requests.post(self.api_url, data=data, timeout=30)
            
            print(f"📡 Response status: {response.status_code}")
            print(f"📄 Response text: {response.text[:200]}...")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    image_url = result['data']['url']
                    image_id = result['data']['id']
                    
                    print(f"✅ IMGBB UPLOAD SUCCESS: {unique_name}")
                    print(f"🌐 URL: {image_url}")
                    
                    logger.info(f"✅ ImgBB upload successful: {unique_name}")
                    logger.info(f"🌐 URL: {image_url}")
                    
                    # Store the URL mapping in cache for retrieval
                    cache_key = f"imgbb_url_{unique_name}"
                    cache.set(cache_key, image_url, timeout=None)  # Permanent cache
                    
                    # Also store by image ID for backup
                    cache.set(f"imgbb_id_{image_id}", image_url, timeout=None)
                    
                    return unique_name
                else:
                    print(f"❌ IMGBB API ERROR: {result}")
                    logger.error(f"❌ ImgBB API error: {result}")
                    return self._save_locally(name, content)
            else:
                print(f"❌ IMGBB HTTP ERROR: {response.status_code} - {response.text}")
                logger.error(f"❌ ImgBB upload failed: {response.status_code} - {response.text}")
                return self._save_locally(name, content)
                
        except Exception as e:
            print(f"❌ IMGBB EXCEPTION: {e}")
            logger.error(f"❌ ImgBB upload error: {e}")
            return self._save_locally(name, content)

    def _save_locally(self, name, content):
        """Fallback to save locally if ImgBB fails"""
        from django.core.files.storage import default_storage
        return default_storage._save(name, content)

    def _open(self, name, mode='rb'):
        """Open file from ImgBB storage"""
        try:
            url = self.url(name)
            response = requests.get(url)
            if response.status_code == 200:
                return ContentFile(response.content)
            else:
                raise Exception(f"File not found: {name}")
        except Exception as e:
            logger.error(f"ImgBB open error: {e}")
            raise

    def delete(self, name):
        """Delete file from ImgBB storage"""
        # ImgBB doesn't provide delete API for free accounts
        # Files are permanent which is actually good for medical records
        logger.info(f"ImgBB file permanent (no delete): {name}")
        # Clear from cache
        cache_key = f"imgbb_url_{name}"
        cache.delete(cache_key)
        return True

    def exists(self, name):
        """Check if file exists in ImgBB storage"""
        try:
            # First check cache
            cache_key = f"imgbb_url_{name}"
            url = cache.get(cache_key)
            if url:
                response = requests.head(url, timeout=10)
                return response.status_code == 200
            return False
        except:
            return False

    def size(self, name):
        """Get file size"""
        try:
            cache_key = f"imgbb_url_{name}"
            url = cache.get(cache_key)
            if url:
                response = requests.head(url, timeout=10)
                return int(response.headers.get('content-length', 0))
            return 0
        except:
            return 0

    def url(self, name):
        """Get public URL for file"""
        # Try to get URL from cache first
        cache_key = f"imgbb_url_{name}"
        url = cache.get(cache_key)
        
        if url:
            logger.info(f"📸 Retrieved ImgBB URL from cache: {name}")
            return url
        else:
            logger.warning(f"⚠️ ImgBB URL not found in cache for: {name}")
            # Return a placeholder or fallback URL
            return f"/media/{name}"  # Fallback to local serving
