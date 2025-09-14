





from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Treatment, TreatmentStep, TreatmentStepPhoto
from django.core.cache import cache

# --- Treatment ---
@receiver(post_save, sender=Treatment)
def set_qr_image_url_from_cache(sender, instance, **kwargs):
	if instance.qr_image and not instance.qr_image_url:
		cache_key = f"imgbb_url_{instance.qr_image.name}"
		url = cache.get(cache_key)
		if url:
			instance.qr_image_url = url
			instance.save(update_fields=['qr_image_url'])
			print(f"[SIGNAL][Treatment] Set qr_image_url from cache: {url}")
		else:
			print(f"[SIGNAL][Treatment][WARN] ImgBB URL not found in cache for: {instance.qr_image.name}")

# --- TreatmentStep ---
@receiver(post_save, sender=TreatmentStep)
def set_step_image_url_from_cache(sender, instance, **kwargs):
	if instance.image and not instance.image_url:
		cache_key = f"imgbb_url_{instance.image.name}"
		url = cache.get(cache_key)
		if url:
			instance.image_url = url
			instance.save(update_fields=['image_url'])
			print(f"[SIGNAL][TreatmentStep] Set image_url from cache: {url}")
		else:
			print(f"[SIGNAL][TreatmentStep][WARN] ImgBB URL not found in cache for: {instance.image.name}")

# --- TreatmentStepPhoto ---
@receiver(post_save, sender=TreatmentStepPhoto)
def set_photo_image_url_from_cache(sender, instance, **kwargs):
	if instance.image and not instance.image_url:
		cache_key = f"imgbb_url_{instance.image.name}"
		url = cache.get(cache_key)
		if url:
			instance.image_url = url
			instance.save(update_fields=['image_url'])
			print(f"[SIGNAL][TreatmentStepPhoto] Set image_url from cache: {url}")
		else:
			print(f"[SIGNAL][TreatmentStepPhoto][WARN] ImgBB URL not found in cache for: {instance.image.name}")
