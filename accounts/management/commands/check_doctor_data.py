from django.core.management.base import BaseCommand
from accounts.models import CustomUser, Doctor, Patient, PatientTreatment, TreatmentStep, Treatment

class Command(BaseCommand):
    help = 'Check and display doctor data relationships'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Checking doctor data...'))
        
        # Check doctors
        doctors = Doctor.objects.all()
        self.stdout.write(f'Total doctors: {doctors.count()}')
        
        for doctor in doctors:
            self.stdout.write(f'\nDoctor: {doctor.user.email} (ID: {doctor.id})')
            self.stdout.write(f'  User ID: {doctor.user.id}')
            
            # Check patients assigned to this doctor
            patients = doctor.patients.all()
            self.stdout.write(f'  Patients assigned: {patients.count()}')
            
            for patient in patients:
                self.stdout.write(f'    - Patient: {patient.user.email} (ID: {patient.id})')
                
                # Check if patient has treatments
                try:
                    treatment = Treatment.objects.get(patient=patient)
                    self.stdout.write(f'      Treatment: ID {treatment.id}, Stage {treatment.current_stage}')
                except Treatment.DoesNotExist:
                    self.stdout.write(f'      No Treatment object found')
                
                # Check if patient has PatientTreatment
                try:
                    patient_treatment = PatientTreatment.objects.get(patient=patient)
                    steps = patient_treatment.steps.all()
                    self.stdout.write(f'      PatientTreatment: ID {patient_treatment.id}, Steps: {steps.count()}')
                except PatientTreatment.DoesNotExist:
                    self.stdout.write(f'      No PatientTreatment object found')
        
        # Check patients without doctors
        patients_without_doctors = Patient.objects.filter(doctor__isnull=True)
        if patients_without_doctors.exists():
            self.stdout.write(f'\nPatients without doctors: {patients_without_doctors.count()}')
            for patient in patients_without_doctors:
                self.stdout.write(f'  - {patient.user.email} (ID: {patient.id})')
