from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Treatment, TreatmentStep, TreatmentStepPhoto

# --- Treatment ---
@receiver(post_save, sender=Treatment)
def ensure_qr_image_url(sender, instance, **kwargs):
    if instance.qr_image and hasattr(instance.qr_image, 'url'):
        if 'imgbb.com' in instance.qr_image.url:
            if instance.qr_image_url != instance.qr_image.url:
                instance.qr_image_url = instance.qr_image.url
                instance.save(update_fields=['qr_image_url'])
                print(f"[SIGNAL][Treatment] Updated qr_image_url to {instance.qr_image_url}")

# --- TreatmentStep ---
@receiver(post_save, sender=TreatmentStep)
def ensure_step_image_url(sender, instance, **kwargs):
    if instance.image and hasattr(instance.image, 'url'):
        if 'imgbb.com' in instance.image.url:
            if instance.image_url != instance.image.url:
                instance.image_url = instance.image.url
                instance.save(update_fields=['image_url'])
                print(f"[SIGNAL][TreatmentStep] Updated image_url to {instance.image_url}")

# --- TreatmentStepPhoto ---
@receiver(post_save, sender=TreatmentStepPhoto)
def ensure_photo_image_url(sender, instance, **kwargs):
    if instance.image and hasattr(instance.image, 'url'):
        if 'imgbb.com' in instance.image.url:
            if instance.image_url != instance.image.url:
                instance.image_url = instance.image.url
                instance.save(update_fields=['image_url'])
                print(f"[SIGNAL][TreatmentStepPhoto] Updated image_url to {instance.image_url}")
