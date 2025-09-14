from django.core.management.base import BaseCommand
from accounts.models import Treatment, TreatmentStep, TreatmentStepPhoto
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Fixes all *_url fields by re-uploading images to ImgBB if needed.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting ImgBB URL fix for all models...'))
        self.fix_treatment()
        self.fix_treatment_step()
        self.fix_treatment_step_photo()
        self.stdout.write(self.style.SUCCESS('Done!'))

    def upload_to_imgbb(self, file_path, file_name):
        import requests
        api_key = getattr(settings, 'IMGBB_API_KEY', None)
        if not api_key:
            self.stdout.write(self.style.ERROR('IMGBB_API_KEY not set in settings.'))
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
            self.stdout.write(self.style.ERROR(f'ImgBB upload failed for {file_name}: {response.text}'))
            return None

    def fix_treatment(self):
        for obj in Treatment.objects.all():
            if obj.qr_image and not obj.qr_image_url:
                file_path = obj.qr_image.path
                if os.path.exists(file_path):
                    self.stdout.write(f'Uploading Treatment QR: {file_path}')
                    url = self.upload_to_imgbb(file_path, os.path.basename(file_path))
                    if url:
                        obj.qr_image_url = url
                        obj.save(update_fields=['qr_image_url'])
                        self.stdout.write(self.style.SUCCESS(f'Updated Treatment {obj.id}'))

    def fix_treatment_step(self):
        for obj in TreatmentStep.objects.all():
            if obj.image and not obj.image_url:
                file_path = obj.image.path
                if os.path.exists(file_path):
                    self.stdout.write(f'Uploading Step Image: {file_path}')
                    url = self.upload_to_imgbb(file_path, os.path.basename(file_path))
                    if url:
                        obj.image_url = url
                        obj.save(update_fields=['image_url'])
                        self.stdout.write(self.style.SUCCESS(f'Updated Step {obj.id}'))

    def fix_treatment_step_photo(self):
        for obj in TreatmentStepPhoto.objects.all():
            if obj.image and not obj.image_url:
                file_path = obj.image.path
                if os.path.exists(file_path):
                    self.stdout.write(f'Uploading Step Photo: {file_path}')
                    url = self.upload_to_imgbb(file_path, os.path.basename(file_path))
                    if url:
                        obj.image_url = url
                        obj.save(update_fields=['image_url'])
                        self.stdout.write(self.style.SUCCESS(f'Updated StepPhoto {obj.id}'))
