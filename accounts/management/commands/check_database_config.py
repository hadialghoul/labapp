from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
from accounts.models import TreatmentStep, Patient
import os


class Command(BaseCommand):
    help = 'Check database configuration and connection'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Database Configuration Check")
        self.stdout.write("=" * 50)
        
        # Check environment variables
        database_url = os.getenv("DATABASE_URL")
        self.stdout.write(f"📊 DATABASE_URL environment variable: {'✅ Set' if database_url else '❌ Not set'}")
        if database_url:
            # Don't print the full URL for security, just the host
            if 'yamabiko.proxy.rlwy.net' in database_url:
                self.stdout.write("🎯 DATABASE_URL points to Railway (yamabiko.proxy.rlwy.net)")
            else:
                self.stdout.write(f"🔍 DATABASE_URL points to: {database_url.split('@')[1].split('/')[0] if '@' in database_url else 'Unknown'}")
        
        # Check Django settings
        db_config = settings.DATABASES['default']
        self.stdout.write(f"🔧 Django DATABASE ENGINE: {db_config.get('ENGINE', 'Not set')}")
        self.stdout.write(f"🏠 Django DATABASE HOST: {db_config.get('HOST', 'Not set')}")
        self.stdout.write(f"🗄️  Django DATABASE NAME: {db_config.get('NAME', 'Not set')}")
        
        # Test actual database connection
        try:
            with connection.cursor() as cursor:
                # Use a query that works for both SQLite and PostgreSQL
                if 'sqlite3' in db_config.get('ENGINE', ''):
                    cursor.execute("SELECT sqlite_version()")
                    version = cursor.fetchone()
                    if version:
                        self.stdout.write(f"✅ Database connection successful")
                        self.stdout.write(f"� Connected to SQLite version: {version[0]}")
                else:
                    cursor.execute("SELECT version()")
                    version = cursor.fetchone()
                    if version:
                        self.stdout.write(f"✅ Database connection successful")
                        self.stdout.write(f"🎯 Connected to PostgreSQL: {version[0]}")
                        
        except Exception as e:
            self.stdout.write(f"❌ Database connection failed: {e}")
        
        self.stdout.write("\n" + "=" * 50)
        
        # Now check treatment steps
        try:
            total_steps = TreatmentStep.objects.count()
            self.stdout.write(f"📊 Total treatment steps found: {total_steps}")
            
            if total_steps > 0:
                # Get some sample data
                recent_steps = TreatmentStep.objects.order_by('-start_date')[:5]
                self.stdout.write(f"\n🔍 Most recent {min(5, total_steps)} steps:")
                for i, step in enumerate(recent_steps, 1):
                    patient_name = step.treatment.patient.user.first_name if step.treatment.patient.user.first_name else step.treatment.patient.user.username
                    self.stdout.write(f"  {i}. {step.name} - {patient_name} - {step.start_date} (Active: {step.is_active}, Notified: {step.notification_sent})")
                
                # Check for the expected September step
                sept_steps = TreatmentStep.objects.filter(start_date__month=9, start_date__year=2025)
                self.stdout.write(f"\n🗓️  September 2025 steps: {sept_steps.count()}")
                if sept_steps.exists():
                    for step in sept_steps:
                        patient_name = step.treatment.patient.user.first_name if step.treatment.patient.user.first_name else step.treatment.patient.user.username
                        self.stdout.write(f"   - {step.name} - {patient_name} - {step.start_date} (Active: {step.is_active}, Notified: {step.notification_sent})")
                else:
                    self.stdout.write("   ❌ No September 2025 steps found!")
                    
                # Check for active steps that should be sending notifications
                active_finished_steps = [
                    step for step in TreatmentStep.objects.filter(is_active=True, notification_sent=False)
                    if step.is_finished()
                ]
                self.stdout.write(f"\n🔔 Active steps ready for notification: {len(active_finished_steps)}")
                for step in active_finished_steps:
                    patient_name = step.treatment.patient.user.first_name if step.treatment.patient.user.first_name else step.treatment.patient.user.username
                    days_finished = (timezone.now().date() - step.start_date).days - step.duration_days
                    self.stdout.write(f"   - {step.name} - {patient_name} - Finished {days_finished} days ago")
                        
        except Exception as e:
            self.stdout.write(f"❌ Error checking treatment steps: {e}")
