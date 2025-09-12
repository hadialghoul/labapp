from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import TreatmentStep
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Check status of treatment steps and why emails might not be sending'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Checking all active treatment steps...")
        
        # Get all active steps
        steps = TreatmentStep.objects.filter(is_active=True).order_by('-start_date')
        
        self.stdout.write(f"Found {steps.count()} active steps:")
        
        for step in steps:
            self.stdout.write(f"\n📋 Step: '{step.name}'")
            self.stdout.write(f"   ID: {step.id}")
            self.stdout.write(f"   Start Date: {step.start_date}")
            self.stdout.write(f"   Duration: {step.duration_days} days")
            self.stdout.write(f"   Is Completed: {step.is_completed}")
            self.stdout.write(f"   Is Active: {step.is_active}")
            self.stdout.write(f"   Notification Sent: {step.notification_sent}")
            
            # Calculate expected end date
            if step.start_date and step.duration_days:
                expected_end = step.start_date + timedelta(days=step.duration_days)
                self.stdout.write(f"   Expected End: {expected_end}")
                self.stdout.write(f"   Today: {timezone.now().date()}")
                
                # Check if finished
                is_finished = step.is_finished()
                self.stdout.write(f"   Is Finished: {is_finished}")
                
                # Check if should send notification
                should_notify = is_finished and not step.notification_sent and step.is_active and not step.is_completed
                self.stdout.write(f"   Should Send Notification: {should_notify}")
                
                if should_notify:
                    self.stdout.write(self.style.SUCCESS("   ✅ THIS STEP IS READY FOR NOTIFICATION!"))
                elif is_finished and step.notification_sent:
                    self.stdout.write(self.style.WARNING("   ⚠️  Notification already sent"))
                elif not is_finished:
                    days_remaining = (expected_end - timezone.now().date()).days
                    self.stdout.write(self.style.WARNING(f"   ⏰ {days_remaining} days remaining"))
                elif step.is_completed:
                    self.stdout.write(self.style.WARNING("   ✅ Step already completed"))
            
            # Patient info
            if step.treatment and step.treatment.patient:
                patient_email = step.treatment.patient.user.email
                self.stdout.write(f"   Patient: {patient_email}")
            else:
                self.stdout.write(f"   Patient: No patient assigned")
        
        self.stdout.write(f"\n📧 Email Configuration Check:")
        from django.conf import settings
        if hasattr(settings, 'EMAIL_BACKEND'):
            self.stdout.write(f"   Email Backend: {settings.EMAIL_BACKEND}")
        else:
            self.stdout.write(self.style.ERROR("   ❌ No EMAIL_BACKEND configured!"))
