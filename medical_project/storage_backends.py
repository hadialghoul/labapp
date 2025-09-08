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
            
            # Upload to Supabase storage
            response = self.supabase.storage.from_(self.bucket_name).upload(
                path=unique_name,
                file=file_data,
                file_options={
                    "content-type": self._get_content_type(name),
                    "upsert": True
                }
            )
            
            if response.status_code == 200:
                return unique_name
            else:
                raise Exception(f"Upload failed: {response}")
                
        except Exception as e:
            print(f"Supabase upload error: {e}")
            raise

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
            response = self.supabase.storage.from_(self.bucket_name).list(path=name)
            return len(response) > 0
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
