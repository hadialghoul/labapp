from django.core.management.base import BaseCommand
from accounts.models import PatientReport
import os


class Command(BaseCommand):
    help = 'Clean up PatientReport records that reference missing files and migrate them'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Checking PatientReport records...")
        
        # Get all reports
        all_reports = PatientReport.objects.all()
        total_reports = all_reports.count()
        self.stdout.write(f"📊 Total PatientReport records: {total_reports}")
        
        if total_reports == 0:
            self.stdout.write("✅ No PatientReport records found")
            return
        
        # Check for reports with missing files
        problematic_reports = []
        binary_reports = 0
        file_reports = 0
        
        for report in all_reports:
            if report.report_data:  # Has binary data
                binary_reports += 1
                self.stdout.write(f"✅ Report {report.id}: Has binary data ({len(report.report_data)} bytes)")
            elif report.report_file:  # Has file reference
                file_reports += 1
                try:
                    # Check if the file actually exists
                    if report.report_file.file and os.path.exists(report.report_file.path):
                        self.stdout.write(f"📁 Report {report.id}: File exists at {report.report_file.path}")
                    else:
                        self.stdout.write(f"❌ Report {report.id}: File missing - {report.report_file.name}")
                        problematic_reports.append(report)
                except Exception as e:
                    self.stdout.write(f"❌ Report {report.id}: Error checking file - {e}")
                    problematic_reports.append(report)
            else:
                self.stdout.write(f"❓ Report {report.id}: No file or binary data")
                problematic_reports.append(report)
        
        self.stdout.write(f"\n📊 Summary:")
        self.stdout.write(f"  ✅ Reports with binary data: {binary_reports}")
        self.stdout.write(f"  📁 Reports with files: {file_reports}")
        self.stdout.write(f"  ❌ Problematic reports: {len(problematic_reports)}")
        
        if problematic_reports:
            self.stdout.write(f"\n🧹 Problematic reports that should be removed:")
            for report in problematic_reports:
                patient_name = report.patient.user.first_name if report.patient.user.first_name else report.patient.user.username
                self.stdout.write(f"  - Report {report.id}: {patient_name} - {report.generated_at}")
            
            # Ask for confirmation to delete
            if input("\nDelete these problematic reports? (y/N): ").lower() == 'y':
                deleted_count = 0
                for report in problematic_reports:
                    report.delete()
                    deleted_count += 1
                
                self.stdout.write(f"✅ Deleted {deleted_count} problematic reports")
            else:
                self.stdout.write("⏭️  Skipped deletion")
        
        self.stdout.write("\n✅ PatientReport cleanup complete")
