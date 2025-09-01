#!/usr/bin/env python
"""
Create a test patient with your email to test notifications
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

def create_test_patient_with_your_email():
    """Create a test patient with your email"""
    
    # Get your email
    your_email = input("Enter your email address: ").strip()
    
    if not your_email:
        print("❌ Email is required!")
        return
    
    print(f"Creating test patient with email: {your_email}")
    
    # Get or create doctor (we'll use existing one)
    try:
        doctor = Doctor.objects.first()
        if not doctor:
            print("❌ No doctor found. Please create a doctor first.")
            return
        print(f"✓ Using doctor: {doctor}")
    except:
        print("❌ Error finding doctor")
        return
    
    # Create or get user
    user, created = CustomUser.objects.get_or_create(
        email=your_email,
        defaults={
            'username': f'test_patient_{your_email.split("@")[0]}',
            'first_name': 'Test',
            'last_name': 'Patient',
            'is_patient': True
        }
    )
    
    if created:
        user.set_password('test123')
        user.save()
        print(f"✓ Created user: {your_email}")
    else:
        print(f"✓ Using existing user: {your_email}")
    
    # Create or get patient
    patient, created = Patient.objects.get_or_create(
        user=user,
        defaults={'doctor': doctor, 'phone': '+1234567890'}
    )
    
    if created:
        print(f"✓ Created patient: {patient}")
    else:
        print(f"✓ Using existing patient: {patient}")
    
    # Create or get treatment
    treatment, created = PatientTreatment.objects.get_or_create(
        patient=patient
    )
    
    if created:
        print(f"✓ Created treatment: {treatment}")
    else:
        print(f"✓ Using existing treatment: {treatment}")
    
    # Clear existing steps for this patient
    existing_steps = TreatmentStep.objects.filter(treatment=treatment)
    if existing_steps.exists():
        print(f"🗑️ Deleting {existing_steps.count()} existing steps...")
        existing_steps.delete()
    
    # Create test steps with first step already finished
    steps_data = [
        {
            'name': '🦷 Initial Teeth Alignment',
            'description': 'First phase of treatment to begin aligning your teeth. Wear aligners for the specified duration and maintain good oral hygiene.',
            'duration_days': 1,  # Very short for immediate testing
            'order': 1,
            'is_active': True,
            'start_date': timezone.now().date() - timedelta(days=2)  # Started 2 days ago, so it's finished
        },
        {
            'name': '🔧 Intermediate Adjustment',
            'description': 'Continue the alignment process with adjusted pressure points. You may experience slight discomfort initially.',
            'duration_days': 7,
            'order': 2,
            'is_active': False
        },
        {
            'name': '✨ Final Positioning',
            'description': 'Final phase to perfect the alignment. Focus on retention and maintaining the new position.',
            'duration_days': 14,
            'order': 3,
            'is_active': False
        }
    ]
    
    for step_data in steps_data:
        step = TreatmentStep.objects.create(
            treatment=treatment,
            **step_data
        )
        status = "🟢 ACTIVE & FINISHED" if step.is_active and step.is_finished() else "⭕ Inactive"
        print(f"✓ Created step: {step.name} [{status}]")
    
    print("\n" + "="*60)
    print("🎉 TEST SETUP COMPLETE!")
    print("="*60)
    print(f"📧 Patient Email: {your_email}")
    print(f"🏥 Doctor: {doctor}")
    print(f"📋 Treatment: {treatment}")
    print("\n🚀 What happens next:")
    print("1. Run the notification command")
    print("2. Check your email for step completion notification")
    print("3. Upload a photo via the app to progress to next step")
    print("\n💡 Commands to test:")
    print("   python manage.py notify_finished_steps --dry-run")
    print("   python manage.py notify_finished_steps --auto-progress")
    
    return treatment

def test_email_directly():
    """Test sending email directly"""
    from django.core.mail import send_mail
    
    your_email = input("Enter your email to test direct email: ").strip()
    
    if not your_email:
        print("❌ Email is required!")
        return
    
    print(f"📧 Sending test email to: {your_email}")
    
    try:
        send_mail(
            subject='🧪 Test Email - Treatment Notification System',
            message='''
Hello!

This is a test email from your medical treatment notification system.

If you received this email, your email configuration is working correctly! 🎉

The system is ready to send:
✅ Step completion notifications
✅ Photo upload reminders  
✅ Next step announcements

Best regards,
Your Medical Treatment Team
            ''',
            from_email=None,  # Uses DEFAULT_FROM_EMAIL
            recipient_list=[your_email],
            fail_silently=False,
        )
        print("✅ Test email sent successfully!")
        print("📱 Check your email inbox (and spam folder)")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your email settings in settings.py")
        print("2. Verify your Gmail app password is correct")
        print("3. Make sure 'Less secure app access' is enabled")

def main():
    print("🧪 EMAIL NOTIFICATION TESTER")
    print("="*50)
    
    while True:
        print("\nChoose an option:")
        print("1. Create test patient with your email")
        print("2. Send test email directly")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            create_test_patient_with_your_email()
        elif choice == '2':
            test_email_directly()
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
