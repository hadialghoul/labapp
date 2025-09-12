from django.core.management.base import BaseCommand
from accounts.models import TreatmentStep

class Command(BaseCommand):
    help = 'Find and fix the phantom hadi1 treatment step causing email spam'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Searching for phantom 'hadi1' step...")
        
        # Search for steps containing 'hadi1'
        steps = TreatmentStep.objects.filter(name__icontains='hadi1')
        
        self.stdout.write(f"Found {steps.count()} steps containing 'hadi1':")
        
        for step in steps:
            self.stdout.write(f"\n📋 Step Details:")
            self.stdout.write(f"   ID: {step.id}")
            self.stdout.write(f"   Name: '{step.name}'")
            self.stdout.write(f"   Active: {step.is_active}")
            self.stdout.write(f"   Completed: {step.is_completed}")
            self.stdout.write(f"   Notification Sent: {step.notification_sent}")
            patient_email = step.treatment.patient.user.email if step.treatment and step.treatment.patient else 'No patient'
            self.stdout.write(f"   Patient: {patient_email}")
            self.stdout.write(f"   Is Finished: {step.is_finished()}")
            
            # Check if this is causing the notifications
            if step.is_finished() and not step.notification_sent and step.is_active:
                self.stdout.write(self.style.ERROR("   🚨 THIS STEP IS TRIGGERING NOTIFICATIONS!"))
                
                # Fix it automatically
                step.notification_sent = True
                step.save()
                self.stdout.write(self.style.SUCCESS("   ✅ FIXED! Marked notification as sent."))
        
        # Also check for any other problematic steps
        self.stdout.write(f"\n🔍 Checking all problematic steps (finished but not notified)...")
        
        problematic_steps = TreatmentStep.objects.filter(
            is_active=True,
            is_completed=False,
            notification_sent=False
        )
        
        fixed_count = 0
        for step in problematic_steps:
            if step.is_finished():
                self.stdout.write(f"\n⚠️  Problematic Step Found:")
                self.stdout.write(f"   ID: {step.id}")
                self.stdout.write(f"   Name: '{step.name}'")
                patient_email = step.treatment.patient.user.email if step.treatment and step.treatment.patient else 'No patient'
                self.stdout.write(f"   Patient: {patient_email}")
                
                # Fix it
                step.notification_sent = True
                step.save()
                fixed_count += 1
                self.stdout.write(self.style.SUCCESS("   ✅ FIXED! Marked notification as sent."))
        
        self.stdout.write(self.style.SUCCESS(f"\n🎉 Fixed {fixed_count} problematic steps. Emails should stop now!"))
