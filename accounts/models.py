from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
import random
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage

# Create a local file storage for PDFs (since ImgBB only supports images)
local_file_storage = FileSystemStorage()


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_patient = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] 

    def __str__(self):
        return self.email


class Doctor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    # Add doctor-specific fields
    specialization = models.CharField(max_length=100)

    def __str__(self):
        return f"Dr. {self.user.username}"

class Patient(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    # Add more patient-specific fields here
    phone = models.CharField(max_length=15, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='patients', null=True, blank=True)
   

    def __str__(self):
        return f"Patient: {self.user.username}"




User = get_user_model()
class EmailVerification(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True, blank=True)
    def generate_code(self):
        """Generate a 6-digit code and save it."""
        self.code = str(random.randint(100000, 999999))
        self.save()

    def __str__(self):
        return f"Verification for {self.user.email}"

class PatientTreatment(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='patient_treatment')
    # You can add more fields if needed (e.g., start_date, status)

    def __str__(self):
        return f"Treatment for {self.patient}"

class TreatmentStep(models.Model):
    treatment = models.ForeignKey(PatientTreatment, on_delete=models.CASCADE, related_name='steps')
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(
        upload_to='treatment_steps/', 
        blank=True, 
        null=True
    )
    duration_days = models.PositiveIntegerField()
    start_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=False)  # Only one step should be active at a time
    is_completed = models.BooleanField(default=False)
    notification_sent = models.BooleanField(default=False)  # Track if notification was sent
    order = models.PositiveIntegerField(default=1)  # Step order in treatment

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} ({self.treatment.patient})"

    def is_finished(self):
        """Check if the step duration has passed"""
        return timezone.now().date() >= self.start_date + timezone.timedelta(days=self.duration_days)

    def get_next_step(self):
        """Get the next step in the treatment sequence"""
        return TreatmentStep.objects.filter(
            treatment=self.treatment,
            order__gt=self.order
        ).first()

    def complete_and_move_to_next(self):
        """Mark this step as completed and activate the next step"""
        self.is_completed = True
        self.is_active = False
        self.save()
        
        next_step = self.get_next_step()
        if next_step:
            next_step.is_active = True
            next_step.start_date = timezone.now().date()
            next_step.save()
            return next_step
        return None

    def notify_patient_if_finished(self):
        """Send notification to patient when step duration is completed"""
        if self.is_finished() and not self.notification_sent and self.is_active:
            patient_email = self.treatment.patient.user.email
            patient_name = self.treatment.patient.user.first_name or self.treatment.patient.user.username
            
            # Enhanced email content
            subject = f"🎉 Treatment Step '{self.name}' Completed - Moving to Next Step"
            
            message = f"""
Hello {patient_name},

Congratulations! You have successfully completed the treatment step: "{self.name}"

🎯 What's happening now:
✅ Your current step is now complete
🔄 You are automatically moving to the next step
📸 Photo uploads are optional but encouraged for progress tracking

📱 Optional - To upload progress photos:
- Open your patient app
- Go to Treatment Steps
- Find "{self.name}" step
- Tap "Take Photo" or "Upload Photo"

Next Step:
"""
            
            next_step = self.get_next_step()
            if next_step:
                message += f'Your next step is: "{next_step.name}"\n'
                message += f"Duration: {next_step.duration_days} days\n"
                message += f"Start Date: {timezone.now().date()}\n\n"
            else:
                message += "Congratulations! This was your final treatment step.\n\n"
            
            message += """
📝 Remember:
- Photos help track your progress but are not required
- Follow your treatment plan carefully
- Contact your doctor if you have any questions

Best regards,
Your Medical Treatment Team
            """
            
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=None,
                    recipient_list=[patient_email],
                    fail_silently=False,
                )
                self.notification_sent = True
                self.save()
                return True
            except Exception as e:
                print(f"Failed to send email to {patient_email}: {e}")
                return False
        return False

class Treatment(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='main_treatment')  # changed related_name
    current_stage = models.PositiveIntegerField(default=1)
    qr_image = models.ImageField(
        upload_to='qr_codes/', 
        blank=True, 
        null=True
    )  # QR code image

    def __str__(self):
        return f"Treatment for {self.patient} - Stage {self.current_stage}"

class PatientReport(models.Model):
    """Store generated PDF reports for patients
    
    NOTE: For production App/Play Store deployment:
    - PDF data stored in database (binary field) for reliability
    - Local file storage is ephemeral on Render/Heroku
    - Database storage ensures PDFs survive server restarts
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='reports')
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Store PDF as binary data in database (reliable for production)
    report_data = models.BinaryField(null=True, blank=True, help_text="PDF file stored as binary data")
    original_filename = models.CharField(max_length=255, null=True, blank=True, help_text="Original PDF filename")
    
    # Keep file field for backward compatibility and admin uploads
    report_file = models.FileField(
        upload_to='patient_reports/', 
        storage=local_file_storage,  
        null=True, 
        blank=True,
        help_text="PDF file (will be converted to binary storage)"
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    report_period_start = models.DateField(null=True, blank=True)
    report_period_end = models.DateField(null=True, blank=True)
    title = models.CharField(max_length=200, default="Treatment Progress Report")
    notes = models.TextField(blank=True, help_text="Admin notes about this report")
    is_active = models.BooleanField(default=True, help_text="Set to False to hide from doctors")
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"Report for {self.patient.user.email} - {self.generated_at.strftime('%Y-%m-%d')}"
    
    @property
    def file_size(self):
        """Get file size in a readable format"""
        try:
            size = None
            
            # Try to get size from binary data first
            if hasattr(self, 'report_data') and self.report_data:
                size = len(self.report_data)
            elif self.report_file and hasattr(self.report_file, 'size'):
                size = self.report_file.size
            
            if size is not None:
                if size < 1024:
                    return f"{size} B"
                elif size < 1024 * 1024:
                    return f"{size / 1024:.1f} KB"
                else:
                    return f"{size / (1024 * 1024):.1f} MB"
        except Exception as e:
            print(f"Error getting file_size: {e}")
        return "Unknown"
    
    @property
    def filename(self):
        """Get just the filename without path"""
        try:
            if hasattr(self, 'original_filename') and self.original_filename:
                return self.original_filename
            elif self.report_file:
                return self.report_file.name.split('/')[-1]
        except Exception as e:
            print(f"Error getting filename: {e}")
        return "No file"
    
    def save(self, *args, **kwargs):
        """Convert uploaded file to binary storage for production reliability"""
        try:
            if self.report_file and not self.report_data:
                # Read the file and store as binary data
                self.report_file.seek(0)  # Go to beginning of file
                self.report_data = self.report_file.read()
                
                # Store the original filename
                if not self.original_filename:
                    self.original_filename = self.report_file.name.split('/')[-1]
                    
                print(f"✅ Converted PDF to binary storage: {self.original_filename}")
        except Exception as e:
            print(f"❌ Error processing file: {e}")
            # Continue with save even if file processing fails
        
        super().save(*args, **kwargs)
    
    def get_pdf_data(self):
        """Get PDF data for download (from binary storage)"""
        return self.report_data if self.report_data else None


class TreatmentStepPhoto(models.Model):
    """Multiple photos can be attached to a TreatmentStep by the patient."""
    step = models.ForeignKey(TreatmentStep, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='treatment_step_photos/', storage=default_storage)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.step.name} ({self.step.treatment.patient.user.email})"

    def save(self, *args, **kwargs):
        """Custom save method with detailed logging for debugging"""
        print(f"🔄 Saving photo for step: {self.step.name} (ID: {self.step.id})")
        if self.step.treatment and self.step.treatment.patient:
            print(f"📧 Patient: {self.step.treatment.patient.user.email}")
        else:
            print("⚠️ No patient associated with this step")
        
        # Debug storage information
        storage = self.image.storage
        print(f"📦 Storage backend: {storage.__class__.__name__}")
        print(f"🗂️ Storage module: {storage.__class__.__module__}")
        
        super().save(*args, **kwargs)
        print(f"✅ Photo saved with URL: {self.image.url}")
