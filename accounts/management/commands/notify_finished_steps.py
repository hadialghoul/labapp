from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import TreatmentStep

class Command(BaseCommand):
    help = 'Notify patients when their treatment step duration is finished and handle step progression.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--auto-progress',
            action='store_true',
            help='Automatically progress to next step after notification',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually sending emails',
        )

    def handle(self, *args, **options):
        # Only check active steps that haven't been notified yet
        steps = TreatmentStep.objects.filter(
            is_active=True,
            is_completed=False,
            notification_sent=False
        )
        
        notified_count = 0
        progressed_count = 0
        
        self.stdout.write(f"Checking {steps.count()} active treatment steps...")
        
        for step in steps:
            if step.is_finished():
                if options['dry_run']:
                    self.stdout.write(
                        self.style.WARNING(
                            f"[DRY RUN] Would notify {step.treatment.patient.user.email} "
                            f"for step '{step.name}'"
                        )
                    )
                    notified_count += 1
                else:
                    # Send notification
                    success = step.notify_patient_if_finished()
                    if success:
                        patient_email = step.treatment.patient.user.email
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ Notification sent to {patient_email} for step '{step.name}'"
                            )
                        )
                        notified_count += 1
                        
                        # Auto-progress if enabled (photos are optional)
                        if options['auto_progress']:
                            next_step = step.complete_and_move_to_next()
                            if next_step:
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"  → Auto-progressed to next step: '{next_step.name}'"
                                    )
                                )
                                progressed_count += 1
                            else:
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"  → Treatment completed! No more steps."
                                    )
                                )
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f"✗ Failed to send notification for step '{step.name}'"
                            )
                        )
        
        # Summary
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(
                    f'\n[DRY RUN] Would send {notified_count} notifications.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Sent {notified_count} notifications.'
                )
            )
            if options['auto_progress']:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Progressed {progressed_count} patients to next steps.'
                    )
                )
