#!/usr/bin/env python
"""
Quick test - Add a finished step to your account for immediate testing
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_project.settings')
django.setup()

from accounts.models import TreatmentStep, PatientTreatment, Patient, Doctor, CustomUser
from django.utils import timezone

def add_finished_step_to_your_account():
    """Add a finished step to your existing account"""
    
    # Get your email
    your_email = input("Enter your email address: ").strip()
    
    if not your_email:
        print("❌ Email is required!")
        return
    
    try:
        # Find your user account
        user = CustomUser.objects.get(email=your_email)
        print(f"✓ Found user: {user.email}")
        
        # Get patient
        patient = Patient.objects.get(user=user)
        print(f"✓ Found patient: {patient}")
        
        # Get or create treatment
        treatment, created = PatientTreatment.objects.get_or_create(
            patient=patient
        )
        print(f"✓ Treatment: {treatment}")
        
        # Get the highest order number for next step
        last_step = TreatmentStep.objects.filter(treatment=treatment).order_by('-order').first()
        next_order = (last_step.order + 1) if last_step else 1
        
        # Create a step that's already finished
        finished_step = TreatmentStep.objects.create(
            treatment=treatment,
            name=f'🧪 Test Step {next_order} - Ready for Photo',
            description='This is a test step that is already completed. Please take a photo to move to the next step.',
            duration_days=1,
            order=next_order,
            is_active=True,  # This is the current active step
            is_completed=False,  # Not completed yet - waiting for photo
            notification_sent=False,  # No notification sent yet
            start_date=timezone.now().date() - timedelta(days=2)  # Started 2 days ago, so it's finished
        )
        
        print("\n" + "="*60)
        print("🎉 TEST STEP CREATED!")
        print("="*60)
        print(f"📧 Your Email: {your_email}")
        print(f"📋 Step Name: {finished_step.name}")
        print(f"📅 Start Date: {finished_step.start_date} (2 days ago)")
        print(f"⏱️ Duration: {finished_step.duration_days} day")
        print(f"✅ Is Finished: {finished_step.is_finished()}")
        print(f"🟢 Is Active: {finished_step.is_active}")
        
        print("\n🚀 READY TO TEST!")
        print("Run this command now:")
        print("   python manage.py notify_finished_steps --auto-progress")
        print("\n📧 You should receive an email immediately!")
        
        return finished_step
        
    except CustomUser.DoesNotExist:
        print(f"❌ No user found with email: {your_email}")
        print("💡 Create a user account first or use the test_your_email.py script")
        return None
    except Patient.DoesNotExist:
        print(f"❌ No patient found for user: {your_email}")
        print("💡 Create a patient account first")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == '__main__':
    print("🧪 QUICK TEST SETUP")
    print("="*50)
    print("This will add a 'finished' step to your account for immediate testing")
    print("")
    
    step = add_finished_step_to_your_account()
    
    if step:
        print("\n" + "="*60)
        print("NEXT STEPS:")
        print("1. Run: python manage.py notify_finished_steps --auto-progress")
        print("2. Check your email inbox")
        print("3. Take a photo via the React Native app")
        print("4. Watch automatic progression to next step!")
        print("="*60)
