import os
import uuid
import base64
import requests
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings


class GitHubStorage(Storage):
    def __init__(self):
        self.github_token = settings.GITHUB_TOKEN
        self.github_repo = settings.GITHUB_REPO  # format: "username/repo-name"
        self.base_url = f"https://api.github.com/repos/{self.github_repo}/contents"
        self.raw_url = f"https://raw.githubusercontent.com/{self.github_repo}/main"
        
    def _save(self, name, content):
        """Save file to GitHub repository"""
        try:
            # Generate unique filename
            file_extension = os.path.splitext(name)[1]
            unique_name = f"medical_photos/{uuid.uuid4()}{file_extension}"
            
            # Read file content and encode to base64
            content.seek(0)
            file_data = content.read()
            encoded_content = base64.b64encode(file_data).decode('utf-8')
            
            print(f"🔄 Uploading to GitHub: {unique_name}")
            print(f"🔄 Repo: {self.github_repo}")
            print(f"🔄 File size: {len(file_data)} bytes")
            
            # Prepare GitHub API request
            url = f"{self.base_url}/{unique_name}"
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json',
            }
            
            data = {
                'message': f'Upload medical photo: {unique_name}',
                'content': encoded_content,
                'branch': 'main'
            }
            
            # Upload to GitHub
            response = requests.put(url, json=data, headers=headers)
            
            if response.status_code == 201:
                print(f"✅ GitHub upload successful: {unique_name}")
                return unique_name
            else:
                print(f"❌ GitHub upload failed: {response.status_code} - {response.text}")
                # Fall back to local storage
                return self._save_locally(name, content)
                
        except Exception as e:
            print(f"❌ GitHub upload error: {e}")
            return self._save_locally(name, content)

    def _save_locally(self, name, content):
        """Fallback to save locally if GitHub fails"""
        from django.core.files.storage import default_storage
        return default_storage._save(name, content)

    def _open(self, name, mode='rb'):
        """Open file from GitHub storage"""
        try:
            url = self.url(name)
            response = requests.get(url)
            if response.status_code == 200:
                return ContentFile(response.content)
            else:
                raise Exception(f"File not found: {name}")
        except Exception as e:
            print(f"GitHub open error: {e}")
            raise

    def delete(self, name):
        """Delete file from GitHub repository"""
        try:
            # First, get the file's SHA (required for deletion)
            url = f"{self.base_url}/{name}"
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json',
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                sha = response.json().get('sha')
                
                # Delete the file
                data = {
                    'message': f'Delete medical photo: {name}',
                    'sha': sha,
                    'branch': 'main'
                }
                
                delete_response = requests.delete(url, json=data, headers=headers)
                return delete_response.status_code == 200
            else:
                print(f"File not found for deletion: {name}")
                return False
                
        except Exception as e:
            print(f"GitHub delete error: {e}")
            return False

    def exists(self, name):
        """Check if file exists in GitHub repository"""
        try:
            url = f"{self.base_url}/{name}"
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json',
            }
            
            response = requests.get(url, headers=headers)
            return response.status_code == 200
        except:
            return False

    def size(self, name):
        """Get file size"""
        try:
            url = f"{self.base_url}/{name}"
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json',
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get('size', 0)
            return 0
        except:
            return 0

    def url(self, name):
        """Get public URL for file - return Render domain URL that will be proxied"""
        # Return Render domain URL that will be handled by our proxy view
        from django.conf import settings
        return f"{settings.MEDIA_URL}{name}"
