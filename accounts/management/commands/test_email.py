from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Test email sending functionality'

    def add_arguments(self, parser):
        parser.add_argument('--to', type=str, help='Email address to send test to')

    def handle(self, *args, **options):
        to_email = options.get('to') or 'hadialghoul2003@gmail.com'
        
        self.stdout.write(f"🧪 Testing email sending to: {to_email}")
        self.stdout.write(f"📧 Email Backend: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"📨 SMTP Host: {settings.EMAIL_HOST}")
        self.stdout.write(f"👤 From Email: {settings.EMAIL_HOST_USER}")
        
        try:
            send_mail(
                subject='🧪 Test Email from Medical App',
                message='''
This is a test email from your medical notification system.

If you received this email, the email configuration is working correctly!

Test details:
- Sent from: Django Management Command
- Date: Today
- System: Render Production Server

Best regards,
Medical App Team
                ''',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[to_email],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Test email sent successfully to {to_email}'))
            self.stdout.write('📱 Check your inbox (and spam folder) for the test email!')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to send test email: {str(e)}'))
            self.stdout.write(f'📋 Error details: {type(e).__name__}')
            
            # Check common issues
            if 'authentication' in str(e).lower():
                self.stdout.write('🔐 This looks like an authentication issue with Gmail')
            elif 'connection' in str(e).lower():
                self.stdout.write('🌐 This looks like a connection issue to Gmail SMTP')
