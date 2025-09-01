from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Patient, PatientReport
from accounts.pdf_reports import PatientReportGenerator
from django.core.files.base import ContentFile
import io
from datetime import datetime

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate sample PDF reports for all patients'

    def add_arguments(self, parser):
        parser.add_argument(
            '--patient-id',
            type=int,
            help='Generate report for specific patient ID only',
        )

    def handle(self, *args, **options):
        try:
            # Get admin user to assign as report generator
            admin_user = User.objects.filter(is_staff=True).first()
            if not admin_user:
                self.stdout.write(
                    self.style.ERROR('No admin user found. Please create an admin user first.')
                )
                return

            # Get patients to generate reports for
            if options['patient_id']:
                patients = Patient.objects.filter(id=options['patient_id'])
                if not patients.exists():
                    self.stdout.write(
                        self.style.ERROR(f'Patient with ID {options["patient_id"]} not found.')
                    )
                    return
            else:
                patients = Patient.objects.all()

            if not patients.exists():
                self.stdout.write(
                    self.style.WARNING('No patients found.')
                )
                return

            generated_count = 0
            for patient in patients:
                try:
                    # Check if patient already has recent reports
                    existing_reports = patient.reports.filter(is_active=True).count()
                    
                    self.stdout.write(f'Generating report for patient: {patient.user.email}')
                    
                    # Generate PDF using our report generator
                    generator = PatientReportGenerator()
                    pdf_bytes = generator.generate_patient_report(patient)
                    
                    if pdf_bytes:
                        # Create PatientReport instance
                        report = PatientReport.objects.create(
                            patient=patient,
                            generated_by=admin_user,
                            title=f"Treatment Progress Report - {datetime.now().strftime('%B %Y')}",
                            notes=f"Sample report generated via management command. Patient has {existing_reports} existing reports."
                        )
                        
                        # Save PDF file
                        filename = f"patient_report_{patient.user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        report.report_file.save(
                            filename,
                            ContentFile(pdf_bytes),
                            save=True
                        )
                        
                        generated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Generated report for {patient.user.email} (ID: {report.id})')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'Failed to generate PDF for {patient.user.email}')
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error generating report for {patient.user.email}: {str(e)}')
                    )

            self.stdout.write(
                self.style.SUCCESS(f'\nCompleted! Generated {generated_count} reports for {patients.count()} patients.')
            )
            
            if generated_count > 0:
                self.stdout.write(
                    self.style.SUCCESS('You can now view these reports in the mobile app!')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Command failed: {str(e)}')
            )
