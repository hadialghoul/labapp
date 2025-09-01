from django.core.management.base import BaseCommand
from accounts.models import CustomUser, Doctor, Patient

class Command(BaseCommand):
    help = 'Debug doctor-patient relationships'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== DOCTOR-PATIENT DEBUG ==='))
        
        # Check all doctors
        doctors = Doctor.objects.all()
        self.stdout.write(f'Total doctors: {doctors.count()}')
        
        for doctor in doctors:
            user = doctor.user
            self.stdout.write(f'\n--- Doctor: {user.email} (Doctor ID: {doctor.id}, User ID: {user.id}) ---')
            self.stdout.write(f'  is_doctor: {user.is_doctor}')
            self.stdout.write(f'  is_staff: {user.is_staff}')
            self.stdout.write(f'  is_superuser: {user.is_superuser}')
            
            # Check patients assigned to this doctor
            assigned_patients = Patient.objects.filter(doctor=doctor)
            self.stdout.write(f'  Assigned patients: {assigned_patients.count()}')
            
            for patient in assigned_patients:
                self.stdout.write(f'    - Patient ID {patient.id}: {patient.user.email}')
        
        # Check patients without doctors
        unassigned_patients = Patient.objects.filter(doctor__isnull=True)
        self.stdout.write(f'\n--- Unassigned Patients: {unassigned_patients.count()} ---')
        for patient in unassigned_patients:
            self.stdout.write(f'  - Patient ID {patient.id}: {patient.user.email}')
        
        # Show all patients
        all_patients = Patient.objects.all()
        self.stdout.write(f'\n--- All Patients: {all_patients.count()} ---')
        for patient in all_patients:
            doctor_info = f"Doctor ID: {patient.doctor.id}" if patient.doctor else "No doctor"
            self.stdout.write(f'  - Patient ID {patient.id}: {patient.user.email} ({doctor_info})')
