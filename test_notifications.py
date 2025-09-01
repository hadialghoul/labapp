#!/usr/bin/env python
"""
Test script for the treatment step notification system.
This script helps you test the notification functionality manually.
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

def create_test_data():
    """Create test data for demonstration"""
    print("Creating test data...")
    
    # Create test doctor
    doctor_user, created = CustomUser.objects.get_or_create(
        email='doctor@test.com',
        defaults={
            'username': 'doctor_test',
            'first_name': 'Dr. John',
            'last_name': 'Smith',
            'is_doctor': True
        }
    )
    if created:
        doctor_user.set_password('test123')
        doctor_user.save()
    
    doctor, created = Doctor.objects.get_or_create(
        user=doctor_user,
        defaults={'specialization': 'Orthodontist'}
    )
    
    # Create test patient
    patient_user, created = CustomUser.objects.get_or_create(
        email='patient@test.com',
        defaults={
            'username': 'patient_test',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'is_patient': True
        }
    )
    if created:
        patient_user.set_password('test123')
        patient_user.save()
    
    patient, created = Patient.objects.get_or_create(
        user=patient_user,
        defaults={'doctor': doctor, 'phone': '+1234567890'}
    )
    
    # Create treatment
    treatment, created = PatientTreatment.objects.get_or_create(
        patient=patient
    )
    
    # Create test steps
    steps_data = [
        {
            'name': 'Initial Alignment',
            'description': 'First step to align your teeth properly',
            'duration_days': 2,  # Short duration for testing
            'order': 1,
            'is_active': True,
            'start_date': timezone.now().date() - timedelta(days=3)  # Already finished
        },
        {
            'name': 'Intermediate Adjustment',
            'description': 'Continue the alignment process',
            'duration_days': 7,
            'order': 2,
            'is_active': False
        },
        {
            'name': 'Final Positioning',
            'description': 'Final adjustments for perfect alignment',
            'duration_days': 10,
            'order': 3,
            'is_active': False
        }
    ]
    
    for step_data in steps_data:
        step, created = TreatmentStep.objects.get_or_create(
            treatment=treatment,
            order=step_data['order'],
            defaults=step_data
        )
        if created:
            print(f"Created step: {step.name}")
    
    print("✓ Test data created successfully!")
    return treatment

def test_notifications():
    """Test the notification system"""
    print("\n" + "="*50)
    print("TESTING NOTIFICATION SYSTEM")
    print("="*50)
    
    # Check for finished steps
    finished_steps = TreatmentStep.objects.filter(
        is_active=True,
        is_completed=False,
        notification_sent=False
    )
    
    print(f"Found {finished_steps.count()} active steps to check...")
    
    for step in finished_steps:
        print(f"\nChecking step: {step.name}")
        print(f"Start date: {step.start_date}")
        print(f"Duration: {step.duration_days} days")
        print(f"Is finished: {step.is_finished()}")
        
        if step.is_finished():
            print(f"✓ Step '{step.name}' is finished - sending notification...")
            success = step.notify_patient_if_finished()
            if success:
                print(f"✓ Notification sent to {step.treatment.patient.user.email}")
                
                # Test step progression
                next_step = step.complete_and_move_to_next()
                if next_step:
                    print(f"✓ Progressed to next step: {next_step.name}")
                else:
                    print("✓ Treatment completed - no more steps!")
            else:
                print("✗ Failed to send notification")

def show_step_status():
    """Show current status of all steps"""
    print("\n" + "="*50)
    print("CURRENT STEP STATUS")
    print("="*50)
    
    steps = TreatmentStep.objects.all().order_by('treatment__patient__user__email', 'order')
    
    current_patient = None
    for step in steps:
        patient_email = step.treatment.patient.user.email
        if patient_email != current_patient:
            print(f"\n👤 Patient: {patient_email}")
            current_patient = patient_email
        
        status_icons = []
        if step.is_active:
            status_icons.append("🟢 Active")
        if step.is_completed:
            status_icons.append("✅ Completed")
        if step.notification_sent:
            status_icons.append("📧 Notified")
        if step.is_finished():
            status_icons.append("⏰ Finished")
        
        status = " | ".join(status_icons) if status_icons else "⭕ Inactive"
        
        print(f"  {step.order}. {step.name}")
        print(f"     Status: {status}")
        print(f"     Duration: {step.duration_days} days | Start: {step.start_date}")

def main():
    """Main function"""
    print("🏥 TREATMENT STEP NOTIFICATION TESTER")
    print("="*50)
    
    while True:
        print("\nChoose an option:")
        print("1. Create test data")
        print("2. Test notifications")
        print("3. Show step status")
        print("4. Run dry-run notification check")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            create_test_data()
        elif choice == '2':
            test_notifications()
        elif choice == '3':
            show_step_status()
        elif choice == '4':
            print("\nRunning dry-run check...")
            os.system('python manage.py notify_finished_steps --dry-run')
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
