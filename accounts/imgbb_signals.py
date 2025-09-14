



from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Treatment, TreatmentStep, TreatmentStepPhoto
from django.conf import settings
import os
import requests

def upload_to_imgbb(file_path, file_name):
    api_key = getattr(settings, 'IMGBB_API_KEY', None)
    if not api_key:
        print('[SIGNAL][ERROR] IMGBB_API_KEY not set in settings.')
        return None
    with open(file_path, 'rb') as f:
        response = requests.post(
            'https://api.imgbb.com/1/upload',
            params={'key': api_key},
            files={'image': (file_name, f)}
        )
    if response.status_code == 200:
        data = response.json().get('data', {})
        return data.get('url')
    else:
        print(f'[SIGNAL][ERROR] ImgBB upload failed for {file_name}: {response.text}')
        return None

# --- Treatment ---
@receiver(post_save, sender=Treatment)
def ensure_qr_image_url(sender, instance, **kwargs):
    if instance.qr_image:
        # If url is missing or not an ImgBB url, re-upload
        needs_upload = not instance.qr_image_url or 'imgbb.com' not in (instance.qr_image_url or '')
        if needs_upload:
            try:
                file_path = instance.qr_image.path
                if os.path.exists(file_path):
                    url = upload_to_imgbb(file_path, os.path.basename(file_path))
                    if url and url != instance.qr_image_url:
                        instance.qr_image_url = url
                        instance.save(update_fields=['qr_image_url'])
                        print(f"[SIGNAL][Treatment] Uploaded and set qr_image_url to {url}")
            except Exception as e:
                print(f"[SIGNAL][Treatment][ERROR] {e}")

# --- TreatmentStep ---
@receiver(post_save, sender=TreatmentStep)
def ensure_step_image_url(sender, instance, **kwargs):
    if instance.image:
        needs_upload = not instance.image_url or 'imgbb.com' not in (instance.image_url or '')
        if needs_upload:
            try:
                file_path = instance.image.path
                if os.path.exists(file_path):
                    url = upload_to_imgbb(file_path, os.path.basename(file_path))
                    if url and url != instance.image_url:
                        instance.image_url = url
                        instance.save(update_fields=['image_url'])
                        print(f"[SIGNAL][TreatmentStep] Uploaded and set image_url to {url}")
            except Exception as e:
                print(f"[SIGNAL][TreatmentStep][ERROR] {e}")

# --- TreatmentStepPhoto ---
@receiver(post_save, sender=TreatmentStepPhoto)
def ensure_photo_image_url(sender, instance, **kwargs):
    if instance.image:
        needs_upload = not instance.image_url or 'imgbb.com' not in (instance.image_url or '')
        if needs_upload:
            try:
                file_path = instance.image.path
                if os.path.exists(file_path):
                    url = upload_to_imgbb(file_path, os.path.basename(file_path))
                    if url and url != instance.image_url:
                        instance.image_url = url
                        instance.save(update_fields=['image_url'])
                        print(f"[SIGNAL][TreatmentStepPhoto] Uploaded and set image_url to {url}")
            except Exception as e:
                print(f"[SIGNAL][TreatmentStepPhoto][ERROR] {e}")
