#!/usr/bin/env python
"""
Script to find and fix the phantom 'hadi1' treatment step
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_project.settings')
django.setup()

from accounts.models import TreatmentStep, Patient, Treatment

def find_phantom_step():
    print("🔍 Searching for phantom 'hadi1' step...")
    
    # Search for steps containing 'hadi1'
    steps = TreatmentStep.objects.filter(name__icontains='hadi1')
    
    print(f"Found {steps.count()} steps containing 'hadi1':")
    
    for step in steps:
        print(f"\n📋 Step Details:")
        print(f"   ID: {step.id}")
        print(f"   Name: '{step.name}'")
        print(f"   Active: {step.is_active}")
        print(f"   Completed: {step.is_completed}")
        print(f"   Notification Sent: {step.notification_sent}")
        print(f"   Treatment: {step.treatment}")
        print(f"   Patient: {step.treatment.patient.user.email if step.treatment and step.treatment.patient else 'No patient'}")
        print(f"   Is Finished: {step.is_finished()}")
        
        # Check if this is causing the notifications
        if step.is_finished() and not step.notification_sent and step.is_active:
            print(f"   🚨 THIS STEP IS TRIGGERING NOTIFICATIONS!")
            
            # Offer to fix it
            fix_choice = input(f"\nFix this step? (y/n): ").lower().strip()
            if fix_choice == 'y':
                # Mark as notified to stop emails
                step.notification_sent = True
                step.save()
                print(f"   ✅ Fixed! Marked notification as sent.")
            else:
                print(f"   ⏭️  Skipped.")
    
    # Also check for any steps that might be causing issues
    print(f"\n🔍 Checking all problematic steps (finished but not notified)...")
    
    problematic_steps = TreatmentStep.objects.filter(
        is_active=True,
        is_completed=False,
        notification_sent=False
    )
    
    for step in problematic_steps:
        if step.is_finished():
            print(f"\n⚠️  Problematic Step Found:")
            print(f"   ID: {step.id}")
            print(f"   Name: '{step.name}'")
            print(f"   Patient: {step.treatment.patient.user.email if step.treatment and step.treatment.patient else 'No patient'}")
            print(f"   Is Finished: {step.is_finished()}")

if __name__ == "__main__":
    find_phantom_step()
