import os
import uuid
import requests
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings
from supabase import create_client, Client


class SupabaseStorage(Storage):
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY
        self.bucket_name = settings.SUPABASE_BUCKET_NAME
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

    def _save(self, name, content):
        """Save file to Supabase storage"""
        try:
            # Generate unique filename
            file_extension = os.path.splitext(name)[1]
            unique_name = f"{uuid.uuid4()}{file_extension}"
            
            # Read file content
            content.seek(0)
            file_data = content.read()
            
            print(f"🔄 Uploading to Supabase: {unique_name}")
            print(f"🔄 Bucket: {self.bucket_name}")
            print(f"🔄 File size: {len(file_data)} bytes")
            
            # Upload to Supabase storage
            try:
                response = self.supabase.storage.from_(self.bucket_name).upload(
                    path=unique_name,
                    file=file_data,
                    file_options={
                        "content-type": self._get_content_type(name),
                        "upsert": True
                    }
                )
                
                print(f"✅ Supabase upload response: {response}")
                
                # Check if upload was successful
                if hasattr(response, 'status_code') and response.status_code != 200:
                    raise Exception(f"Upload failed with status: {response.status_code}")
                elif hasattr(response, 'error') and response.error:
                    raise Exception(f"Upload error: {response.error}")
                
                # Verify file was actually uploaded by checking if it exists
                if not self.exists(unique_name):
                    raise Exception("File upload verification failed - file not found after upload")
                
                return unique_name
                
            except Exception as upload_error:
                print(f"❌ Supabase upload failed: {upload_error}")
                # If upload fails, fall back to local storage temporarily
                return self._save_locally(name, content)
                
        except Exception as e:
            print(f"❌ Supabase upload error: {e}")
            return self._save_locally(name, content)

    def _save_locally(self, name, content):
        """Fallback to save locally if Supabase fails"""
        from django.core.files.storage import default_storage
        return default_storage._save(name, content)

    def _open(self, name, mode='rb'):
        """Open file from Supabase storage"""
        try:
            url = self.url(name)
            response = requests.get(url)
            if response.status_code == 200:
                return ContentFile(response.content)
            else:
                raise Exception(f"File not found: {name}")
        except Exception as e:
            print(f"Supabase open error: {e}")
            raise

    def delete(self, name):
        """Delete file from Supabase storage"""
        try:
            response = self.supabase.storage.from_(self.bucket_name).remove([name])
            return response.status_code == 200
        except Exception as e:
            print(f"Supabase delete error: {e}")
            return False

    def exists(self, name):
        """Check if file exists in Supabase storage"""
        try:
            # Try to get the public URL and check if it's accessible
            url = self.url(name)
            response = requests.head(url)
            return response.status_code == 200
        except:
            return False

    def size(self, name):
        """Get file size"""
        try:
            url = self.url(name)
            response = requests.head(url)
            return int(response.headers.get('content-length', 0))
        except:
            return 0

    def url(self, name):
        """Get public URL for file"""
        try:
            response = self.supabase.storage.from_(self.bucket_name).get_public_url(name)
            return response
        except Exception as e:
            print(f"Supabase URL error: {e}")
            return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{name}"

    def _get_content_type(self, name):
        """Get content type based on file extension"""
        extension = os.path.splitext(name)[1].lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.pdf': 'application/pdf',
        }
        return content_types.get(extension, 'application/octet-stream')
