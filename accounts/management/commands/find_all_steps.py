from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import TreatmentStep
from datetime import datetime

class Command(BaseCommand):
    help = 'Find all treatment steps including inactive ones'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Searching for ALL treatment steps (active and inactive)...")
        
        # Get ALL steps, not just active ones
        all_steps = TreatmentStep.objects.all().order_by('-start_date')
        
        self.stdout.write(f"Found {all_steps.count()} total steps:")
        
        for step in all_steps:
            self.stdout.write(f"\n📋 Step: '{step.name}'")
            self.stdout.write(f"   ID: {step.id}")
            self.stdout.write(f"   Start Date: {step.start_date}")
            self.stdout.write(f"   Duration: {step.duration_days} days")
            self.stdout.write(f"   Is Completed: {step.is_completed}")
            self.stdout.write(f"   Is Active: {step.is_active}")
            self.stdout.write(f"   Notification Sent: {step.notification_sent}")
            
            # Check if this is your September 9th step
            if step.start_date and step.start_date.day == 9 and step.start_date.month == 9:
                self.stdout.write(self.style.WARNING("   🎯 THIS MIGHT BE YOUR STEP3 FROM SEPT 9th!"))
                
                # Show why it's not being processed
                if not step.is_active:
                    self.stdout.write(self.style.ERROR("   ❌ PROBLEM: Step is marked as INACTIVE"))
                elif step.is_completed:
                    self.stdout.write(self.style.ERROR("   ❌ PROBLEM: Step is marked as COMPLETED"))
                elif step.notification_sent:
                    self.stdout.write(self.style.WARNING("   ⚠️  Step already notified"))
                else:
                    self.stdout.write(self.style.SUCCESS("   ✅ Step should be eligible for notifications"))
            
            # Patient info
            if step.treatment and step.treatment.patient:
                patient_email = step.treatment.patient.user.email
                self.stdout.write(f"   Patient: {patient_email}")
            else:
                self.stdout.write(f"   Patient: ❌ NO PATIENT ASSIGNED")
                if step.start_date and step.start_date.day == 9:
                    self.stdout.write(self.style.ERROR("   🚨 THIS IS WHY IT'S NOT SENDING EMAILS - NO PATIENT!"))
