from django.http import HttpResponse, Http404
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)

def debug_media_view(request, path):
    """Debug view to check if media files exist"""
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    
    logger.info(f"🔍 Checking media file: {path}")
    logger.info(f"📁 Full path: {full_path}")
    logger.info(f"📂 Media root: {settings.MEDIA_ROOT}")
    logger.info(f"✅ File exists: {os.path.exists(full_path)}")
    
    if os.path.exists(settings.MEDIA_ROOT):
        files = os.listdir(settings.MEDIA_ROOT)
        logger.info(f"📋 Files in media root: {files}")
        
        treatment_photos_path = os.path.join(settings.MEDIA_ROOT, 'treatment_step_photos')
        if os.path.exists(treatment_photos_path):
            treatment_files = os.listdir(treatment_photos_path)
            logger.info(f"📸 Treatment photos: {treatment_files}")
        else:
            logger.info("❌ treatment_step_photos directory does not exist")
    else:
        logger.info("❌ Media root directory does not exist")
    
    # Try to serve the file normally
    from django.views.static import serve
    return serve(request, path, document_root=settings.MEDIA_ROOT)
