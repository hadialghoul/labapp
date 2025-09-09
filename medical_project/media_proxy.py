from django.http import HttpResponse, Http404
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)

def github_media_proxy(request, path):
    """
    Proxy view that serves media files from GitHub storage through Render domain.
    This allows photos stored in GitHub to be accessed via Render URLs.
    """
    try:
        # Construct GitHub raw URL
        github_repo = getattr(settings, 'GITHUB_REPO', 'hadialghoul/medical-photos-storage')
        
        # Try multiple possible paths in GitHub
        possible_paths = [
            f"medical_photos/{path.split('/')[-1]}",  # New format: medical_photos/filename
            path,  # Original path as-is
            f"medical_photos/{path}",  # Full path under medical_photos
        ]
        
        logger.info(f"🔄 Proxying media request: {path}")
        
        for github_path in possible_paths:
            github_url = f"https://raw.githubusercontent.com/{github_repo}/main/{github_path}"
            logger.info(f"🌐 Trying GitHub URL: {github_url}")
            
            # Fetch the file from GitHub
            response = requests.get(github_url, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"✅ Successfully fetched from GitHub: {github_path}")
                
                # Determine content type based on file extension
                content_type = 'application/octet-stream'  # default
                if path.lower().endswith(('.jpg', '.jpeg')):
                    content_type = 'image/jpeg'
                elif path.lower().endswith('.png'):
                    content_type = 'image/png'
                elif path.lower().endswith('.gif'):
                    content_type = 'image/gif'
                elif path.lower().endswith('.webp'):
                    content_type = 'image/webp'
                
                # Return the file content with proper headers
                django_response = HttpResponse(response.content, content_type=content_type)
                django_response['Content-Length'] = len(response.content)
                return django_response
            else:
                logger.info(f"❌ Not found at: {github_path} (status: {response.status_code})")
        
        # If none of the paths worked
        logger.warning(f"❌ GitHub file not found in any location: {path}")
        raise Http404(f"Media file not found: {path}")
            
    except requests.RequestException as e:
        logger.error(f"❌ Error fetching from GitHub: {e}")
        raise Http404(f"Error accessing media file: {path}")
    except Exception as e:
        logger.error(f"❌ Unexpected error in media proxy: {e}")
        raise Http404(f"Error serving media file: {path}")
