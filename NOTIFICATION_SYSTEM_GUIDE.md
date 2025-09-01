# Treatment Step Notification System - Setup Guide

## Overview
This system automatically sends email notifications to patients when their treatment step duration is completed, prompts them to take photos, and progresses them to the next step.

## Features
✅ **Automatic Duration Tracking**: Monitors when treatment steps are completed based on duration
✅ **Email Notifications**: Sends professional emails to patients with instructions
✅ **Photo Requirement**: Prompts patients to upload photos before step progression
✅ **Automatic Progression**: Moves patients to next step after photo upload
✅ **Doctor Notifications**: Notifies about patient progress
✅ **Comprehensive Logging**: Tracks all notifications and progressions

## How It Works

### 1. Step Duration Monitoring
- Each `TreatmentStep` has a `duration_days` field
- System calculates if `current_date >= start_date + duration_days`
- Only active, non-completed steps are checked

### 2. Email Notification Process
When a step duration is completed:
1. System sends email to patient with:
   - Congratulations message
   - Photo upload instructions
   - Next step preview
   - App usage guidance

### 3. Photo Upload Trigger
When patient uploads a photo:
1. System checks if step is completed
2. Marks current step as completed
3. Activates next step
4. Sends "next step started" notification

## Database Schema Changes

### New TreatmentStep Fields
```python
class TreatmentStep(models.Model):
    # ... existing fields ...
    is_active = models.BooleanField(default=False)          # Only one active step per patient
    is_completed = models.BooleanField(default=False)       # Step completion status
    notification_sent = models.BooleanField(default=False)  # Prevents duplicate emails
    order = models.PositiveIntegerField(default=1)          # Step sequence order
```

## Management Commands

### Manual Notification Check
```bash
# Check and send notifications (no auto-progression)
python manage.py notify_finished_steps

# Check with auto-progression to next step
python manage.py notify_finished_steps --auto-progress

# Dry run (see what would happen without sending emails)
python manage.py notify_finished_steps --dry-run
```

## Automatic Scheduling

### Windows Task Scheduler Setup
1. Open Task Scheduler (`taskschd.msc`)
2. Create Basic Task
3. Configure:
   - **Name**: Treatment Step Notifications
   - **Trigger**: Daily at 9:00 AM
   - **Action**: Start a program
   - **Program**: `E:\auth\medical_project\run_step_notifications.bat`

### Linux Cron Job Setup
```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 9:00 AM)
0 9 * * * /path/to/your/project/run_step_notifications.sh
```

## Email Configuration

### Django Settings
Ensure your `settings.py` has email configuration:

```python
# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # or your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'Medical Treatment System <your-email@gmail.com>'
```

## Testing the System

### 1. Use the Test Script
```bash
python test_notifications.py
```

### 2. Manual Testing Steps
1. Create a patient with treatment steps
2. Set a step with short duration (1-2 days)
3. Set start_date to past date to make it "finished"
4. Run: `python manage.py notify_finished_steps --dry-run`
5. Run: `python manage.py notify_finished_steps --auto-progress`

### 3. Test Photo Upload Progression
1. Use patient app to upload photo to completed step
2. Check if next step becomes active
3. Verify patient receives "next step" email

## API Endpoints

### Check Step Status
```http
GET /accounts/patients/{patient_id}/treatment-steps/
Authorization: Bearer {token}
```

### Upload Photo (triggers progression)
```http
POST /accounts/treatment-steps/{step_id}/photos/
Authorization: Bearer {token}
Content-Type: multipart/form-data

{
  "image": <file>
}
```

## Email Templates

### Step Completion Email
- Subject: "📸 Treatment Step '{step_name}' Completed - Photo Required"
- Content: Congratulations + photo upload instructions + next step preview

### Next Step Started Email  
- Subject: "🎯 New Treatment Step Started: '{step_name}'"
- Content: New step details + duration + instructions

## Troubleshooting

### Common Issues

1. **Emails not sending**
   - Check email configuration in settings.py
   - Verify SMTP credentials
   - Check spam folder

2. **Steps not progressing**
   - Verify `is_active` and `order` fields are set correctly
   - Check if multiple steps are active (should be only one)

3. **Duplicate notifications**
   - System prevents duplicates with `notification_sent` field
   - Reset field if needed: `step.notification_sent = False; step.save()`

### Debug Commands
```bash
# Check step status
python manage.py shell
>>> from accounts.models import TreatmentStep
>>> for step in TreatmentStep.objects.all():
...     print(f"{step.name}: active={step.is_active}, completed={step.is_completed}, finished={step.is_finished()}")

# Reset notifications for testing
>>> TreatmentStep.objects.update(notification_sent=False)
```

## Production Considerations

1. **Email Rate Limits**: Consider email provider limits
2. **Error Handling**: Monitor logs for failed emails
3. **Database Backups**: Backup before schema changes
4. **Monitoring**: Set up alerts for failed notifications
5. **Testing**: Always test in staging environment first

## Security Notes

- Email credentials should be in environment variables
- Use app-specific passwords for Gmail
- Consider using services like SendGrid or AWS SES for production
- Implement rate limiting for API endpoints

## Next Steps

1. Set up automated scheduling
2. Configure email settings
3. Test with sample patients
4. Monitor logs and performance
5. Add more sophisticated email templates
6. Consider push notifications for mobile app
