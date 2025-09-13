"""
Quick auth examples (Postman or curl)
1) Get tokens
   POST http://127.0.0.1:8000/accounts/token/
   Body (JSON):
     {
       "email": "user@example.com",
       "password": "yourPassword"
     }
   Response:
     { "access": "<ACCESS>", "refresh": "<REFRESH>" }

+Example with your values
+  POST http://127.0.0.1:8000/accounts/token/
+  Body (JSON):
+    {
+      "email":"hadi@gmail.com",
+      "password":"Hadi1234"
+    }

2) Verify token (must include trailing slash)
   GET http://127.0.0.1:8000/accounts/me/
   Header:
     Authorization: Bearer <ACCESS>

3) Doctor’s patients
   GET http://127.0.0.1:8000/accounts/doctor/patients/
   Header:
     Authorization: Bearer <ACCESS>

4) Patient treatment steps
   GET http://127.0.0.1:8000/accounts/patients/<patient_id>/treatment-steps/
   Header:
     Authorization: Bearer <ACCESS>

Notes
- Always include the trailing slash to avoid redirects before auth.
- You can also pass ?token=<ACCESS> for quick testing (enabled in CombinedJWTAuthentication).

curl examples
- Get token:
  curl -X POST http://127.0.0.1:8000/accounts/token/ ^
       -H "Content-Type: application/json" ^
       -d "{ \"email\": \"user@example.com\", \"password\": \"yourPassword\" }"

- Verify token:
  curl http://127.0.0.1:8000/accounts/me/ ^
       -H "Authorization: Bearer <ACCESS>"

- Refresh token:
  curl -X POST http://127.0.0.1:8000/accounts/token/refresh/ ^
       -H "Content-Type: application/json" ^
       -d "{ \"refresh\": \"<REFRESH>\" }"
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from django.contrib.auth import get_user_model
from .models import EmailVerification
from django.core.mail import send_mail
from django.http import HttpResponse
from django.views import View
from datetime import datetime
from .models import  Patient,   Treatment, PatientTreatment, TreatmentStep, TreatmentStepPhoto
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import PatientSerializer,TreatmentSerializer, TreatmentStepSerializer, TreatmentStepPhotoSerializer, PatientTreatmentSerializer
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()

class CombinedJWTAuthentication(JWTAuthentication):
    """
    Accept JWT from Authorization header:
      - Bearer <token>
      - JWT <token>
      - Token <token>
      - <token> (raw, no prefix)
    Or from query params (?token= / ?access=) to simplify Postman/local testing.
    """
    def authenticate(self, request):
        raw_token = None

        # Try Authorization header first
        header = self.get_header(request)
        if header:
            try:
                parts = header.decode("utf-8").split()
            except Exception:
                parts = []
            if len(parts) == 2 and parts[0].lower() in ("bearer", "jwt", "token"):
                raw_token = parts[1]
            elif len(parts) == 1:
                # header present but no scheme, assume it's the token itself
                raw_token = parts[0]

        # Fallback to query parameter
        if not raw_token:
            raw_token = request.query_params.get('token') or request.query_params.get('access')

        if not raw_token:
            return None

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)
        return (user, validated_token)

class RegisterView(APIView):
    def post(self, request):
        # Get user data from the request
        email = request.data.get('email')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')  # Confirm password
        username = request.data.get('username')

        # Validate password confirmation
        if password != confirm_password:
            return Response({"detail": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        # Create user instance
        user = User.objects.create_user(email=email, username=username, password=password)
        
        # Generate email verification code and save it
        verification = EmailVerification.objects.create(user=user)
        verification.generate_code()

        # Send the verification code to the user's email
        send_mail(
            'Your Verification Code',
            f'Your verification code is: {verification.code}',
            'from@example.com',  # Set a valid email here
            [email],
            fail_silently=False,
        )

        return Response({"detail": "User created. Check your email for a verification code."}, status=status.HTTP_201_CREATED)

from django.http import JsonResponse

class VerifyEmailCodeView(APIView):
    def post(self, request):
        code = request.data.get('code')
        print("Received code:", code)  # Debug log

        if not code:
            return JsonResponse({"detail": "Code is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            verification = EmailVerification.objects.get(code=code)
            user = verification.user
            if verification.code == code:
                user.is_active = True
                user.is_patient = True
                user.save()
                Patient.objects.create(user=user)

                verification.delete()

                return Response({"detail": "Email verified successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Invalid code."}, status=status.HTTP_400_BAD_REQUEST)
        except (User.DoesNotExist, EmailVerification.DoesNotExist):
            return Response({"detail": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CombinedJWTAuthentication, SessionAuthentication])
def doctor_patients(request):
    try:
        doctor = request.user.doctor  # assumes OneToOneField from User to Doctor
        patients = doctor.patients.all()  # related_name='patients' in Patient model
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)
    except:
        return Response({"error": "Doctor not found"}, status=404)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CombinedJWTAuthentication, SessionAuthentication])
def patient_detail(request, id):
    try:
        patient = Patient.objects.get(id=id, doctor__user=request.user)
        serializer = PatientSerializer(patient)
        return Response(serializer.data)
    except Patient.DoesNotExist:
        return Response({'error': 'Patient not found'}, status=404)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CombinedJWTAuthentication, SessionAuthentication])
def get_patient_treatment(request, id):
    try:
        patient = Patient.objects.get(id=id, doctor__user=request.user)
        treatment = Treatment.objects.get(patient=patient)
        serializer = TreatmentSerializer(treatment, context={'request': request})
        return Response(serializer.data)
    except (Patient.DoesNotExist, Treatment.DoesNotExist):
        return Response({'error': 'Not found'}, status=404)


class TreatmentDetailView(APIView):
    authentication_classes = [CombinedJWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, patient_id):
        try:
            # Fetch the treatment by patient_id
            treatment = Treatment.objects.get(patient__id=patient_id)
            serializer = TreatmentSerializer(treatment, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Treatment.DoesNotExist:
            return Response({'error': 'Treatment not found for this patient.'}, status=status.HTTP_404_NOT_FOUND)


from rest_framework import generics, permissions
from .models import Patient
from .serializers import PatientSerializer

class PatientTreatmentDetailView(generics.RetrieveAPIView):
    queryset = PatientTreatment.objects.all()
    serializer_class = PatientTreatmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CombinedJWTAuthentication, SessionAuthentication]

    def get_object(self):
        treatment = super().get_object()
        user = self.request.user
        # Allow patient or their doctor to view
        if hasattr(user, 'patient') and treatment.patient == user.patient:
            return treatment
        if hasattr(user, 'doctor') and treatment.patient.doctor == user.doctor:
            return treatment
        raise permissions.PermissionDenied("You do not have access to this patient's treatment.")


class TreatmentStepPhotoListCreate(generics.ListCreateAPIView):
    serializer_class = TreatmentStepPhotoSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CombinedJWTAuthentication, SessionAuthentication]

    def get_step(self):
        step_id = self.kwargs.get('step_id')
        return get_object_or_404(TreatmentStep, pk=step_id)

    def get_queryset(self):
        step = self.get_step()
        user = self.request.user
        # allow patient owner or the assigned doctor to view photos
        if hasattr(user, 'patient') and step.treatment.patient == user.patient:
            return TreatmentStepPhoto.objects.filter(step=step).order_by('-uploaded_at')
        if hasattr(user, 'doctor') and step.treatment.patient.doctor == user.doctor:
            return TreatmentStepPhoto.objects.filter(step=step).order_by('-uploaded_at')
        raise PermissionDenied("You do not have permission to view these photos.")

    def perform_create(self, serializer):
        step = self.get_step()
        user = self.request.user
        # only the patient who owns the step may upload photos
        if not (hasattr(user, 'patient') and step.treatment.patient == user.patient):
            raise PermissionDenied("Only the patient can upload photos for this step.")
        
        # Save the photo (optional documentation)
        photo = serializer.save(step=step, uploaded_by=user)
        
        # Photo upload is purely optional - no automatic progression triggered
        # Progression happens automatically via the scheduled notification system
    
    def send_next_step_notification(self, patient, next_step):
        """Send notification about starting the next step"""
        from django.core.mail import send_mail
        
        patient_email = patient.user.email
        patient_name = patient.user.first_name or patient.user.username
        
        subject = f"🎯 New Treatment Step Started: '{next_step.name}'"
        
        message = f"""
Hello {patient_name},

Great job completing your previous treatment step! 

🆕 Your new treatment step has started:
Step: "{next_step.name}"
Duration: {next_step.duration_days} days
Start Date: {next_step.start_date}

📋 Description:
{next_step.description}

📱 Remember to:
- Follow the step instructions carefully
- Take progress photos when needed
- Contact your doctor if you have questions

You'll receive another notification when this step is completed.

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
        except Exception as e:
            print(f"Failed to send next step notification to {patient_email}: {e}")


class TreatmentStepPhotoDetail(generics.RetrieveDestroyAPIView):
    serializer_class = TreatmentStepPhotoSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CombinedJWTAuthentication, SessionAuthentication]

    def get_queryset(self):
        user = self.request.user
        # allow patient owner or the assigned doctor to delete photos
        if hasattr(user, 'patient'):
            return TreatmentStepPhoto.objects.filter(step__treatment__patient=user.patient)
        if hasattr(user, 'doctor'):
            return TreatmentStepPhoto.objects.filter(step__treatment__patient__doctor=user.doctor)
        raise PermissionDenied("You do not have permission to access these photos.")

    def perform_destroy(self, instance):
        user = self.request.user
        # only the patient who owns the photo may delete it
        if not (hasattr(user, 'patient') and instance.step.treatment.patient == user.patient):
            raise PermissionDenied("Only the patient can delete their own photos.")
        
        try:
            instance.delete()
            # Note: The actual image file remains on ImgBB (permanent storage for medical records)
        except Exception as e:
            from rest_framework.exceptions import APIException
            raise APIException(f"Photo record deleted successfully. Note: Image files are permanently stored for medical record keeping.")


class PatientTreatmentStepsView(generics.ListAPIView):
    serializer_class = TreatmentStepSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CombinedJWTAuthentication, SessionAuthentication]

    def get_queryset(self):
        patient_id = self.kwargs.get('patient_id')
        patient = get_object_or_404(Patient, pk=patient_id)
        user = self.request.user

        # If no PatientTreatment assigned -> 404 with message
        try:
            treatment = patient.patient_treatment
        except PatientTreatment.DoesNotExist:
            raise NotFound(detail="This patient has no treatment assigned.")

        # allow the patient themself
        if hasattr(user, 'patient') and user.patient == patient:
            return TreatmentStep.objects.filter(treatment=treatment).order_by('start_date')

        # allow the patient's assigned doctor
        if hasattr(user, 'doctor') and patient.doctor == user.doctor:
            return TreatmentStep.objects.filter(treatment=treatment).order_by('start_date')

        raise PermissionDenied("You do not have permission to view this patient's treatment steps.")


class PatientsListView(generics.ListAPIView):
    """
    List patients visible to the requesting user:
      - if doctor: patients assigned to that doctor
      - if staff/superuser: all patients
      - if patient: only their own patient record
    """
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CombinedJWTAuthentication, SessionAuthentication]

    def get_queryset(self):
        user = self.request.user
        # doctor: patients assigned to this doctor OR if doctor is staff, show all patients
        if hasattr(user, 'doctor'):
            if user.is_staff or user.is_superuser:
                return Patient.objects.all()  # Staff doctors see all patients
            else:
                return Patient.objects.filter(doctor=user.doctor)  # Regular doctors see assigned patients
        # staff: all patients
        if user.is_staff or user.is_superuser:
            return Patient.objects.all()
        # patient: only their own record
        if hasattr(user, 'patient'):
            return Patient.objects.filter(pk=user.patient.pk)
        return Patient.objects.none()

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Accept 'email' + 'password' (or 'username' + 'password').
    If 'email' provided, map to username for parent validation.
    """
    def validate(self, attrs):
        if 'email' in attrs and 'username' not in attrs:
            try:
                user = get_user_model().objects.get(email=attrs['email'])
                attrs['username'] = getattr(user, 'username')
            except get_user_model().DoesNotExist:
                # let parent raise authentication error
                pass
        return super().validate(attrs)

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CombinedJWTAuthentication, SessionAuthentication])
def whoami(request):
    """
    Quick auth check: returns basic info about the authenticated user.
    Use this in Postman to verify your Authorization: Bearer <access> header.
    """
    u = request.user
    return Response({
        "id": getattr(u, "id", None),
        "email": getattr(u, "email", None),
        "username": getattr(u, "username", None),
        "is_patient": getattr(u, "is_patient", False),
        "is_doctor": hasattr(u, "doctor"),
        "patient_id": getattr(getattr(u, "patient", None), "id", None),
        "doctor_id": getattr(getattr(u, "doctor", None), "id", None),
        "is_staff": getattr(u, "is_staff", False),
        "is_superuser": getattr(u, "is_superuser", False),
        "authenticated": True,
    })


# PDF Report Views - Doctors view pre-generated reports
class DoctorPatientsReportsView(APIView):
    """Get list of patients with their available reports for doctors to view"""
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CombinedJWTAuthentication, SessionAuthentication]
    
    def get(self, request):
        try:
            # Check if user is a doctor
            if not hasattr(request.user, 'doctor'):
                return Response(
                    {"error": "Only doctors can access patient reports"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            doctor = request.user.doctor
            
            # Get patients accessible to this doctor
            if request.user.is_staff or request.user.is_superuser:
                patients = Patient.objects.all()
            else:
                patients = Patient.objects.filter(doctor=doctor)
            
            # Prepare patient data with available reports
            patients_data = []
            for patient in patients:
                try:
                    treatment = patient.patient_treatment
                    total_steps = treatment.steps.count()
                    completed_steps = treatment.steps.filter(is_completed=True).count()
                    progress = (completed_steps / total_steps * 100) if total_steps > 0 else 0
                except:
                    total_steps = 0
                    completed_steps = 0
                    progress = 0
                
                # Get available reports for this patient
                reports = patient.reports.filter(is_active=True).order_by('-generated_at')
                reports_data = []
                
                for report in reports:
                    reports_data.append({
                        'id': report.id,
                        'title': report.title,
                        'generated_at': report.generated_at.strftime('%Y-%m-%d %H:%M'),
                        'generated_by': report.generated_by.get_full_name() if report.generated_by else 'System',
                        'file_size': report.file_size,
                        'download_url': f'/accounts/reports/download/{report.id}/',
                        'notes': report.notes
                    })
                
                patients_data.append({
                    'id': patient.id,
                    'name': patient.user.get_full_name() or patient.user.username,
                    'email': patient.user.email,
                    'phone': patient.phone,
                    'total_steps': total_steps,
                    'completed_steps': completed_steps,
                    'progress_percentage': round(progress, 1),
                    'reports': reports_data,
                    'reports_count': len(reports_data),
                    'last_activity': patient.user.last_login.strftime('%Y-%m-%d') if patient.user.last_login else 'Never'
                })
            
            return Response({
                'doctor': {
                    'id': doctor.id,
                    'name': doctor.user.get_full_name(),
                    'specialization': doctor.specialization
                },
                'patients': patients_data,
                'total_patients': len(patients_data)
            })
            
        except Exception as e:
            return Response(
                {"error": f"Failed to fetch patients: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DownloadReportView(APIView):
    """Download a specific pre-generated report"""
    # No permission_classes or authentication_classes: handle manually for mobile/browser
    def get(self, request, report_id):
        import logging
        logger = logging.getLogger("django")
        try:
            # Always check for query parameter authentication for mobile
            auth_token = request.GET.get('auth')
            logger.info(f"DownloadReportView: Received auth_token: {auth_token}")
            if auth_token:
                from rest_framework_simplejwt.tokens import AccessToken
                try:
                    token = AccessToken(auth_token)
                    user_id = token['user_id']
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    request.user = User.objects.get(id=user_id)
                    logger.info(f"DownloadReportView: Authenticated user {request.user}")
                except Exception as e:
                    logger.error(f"DownloadReportView: Failed to authenticate with token: {e}")
                    return Response({"error": "Invalid or expired token."}, status=status.HTTP_401_UNAUTHORIZED)

            # Check if user is a doctor
            if not hasattr(request.user, 'doctor'):
                logger.warning("DownloadReportView: User is not a doctor.")
                return Response(
                    {"error": "Only doctors can view reports"}, 
                    status=status.HTTP_403_FORBIDDEN
                )

            doctor = request.user.doctor

            # Get the report
            try:
                from .models import PatientReport
                report = PatientReport.objects.select_related('patient__doctor').get(
                    id=report_id,
                    is_active=True
                )
            except PatientReport.DoesNotExist:
                logger.warning("DownloadReportView: Report not found.")
                return Response(
                    {"error": "Report not found or no longer available"}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check if doctor has permission to view this report
            if not (report.patient.doctor == doctor or request.user.is_staff or request.user.is_superuser):
                logger.warning("DownloadReportView: Doctor does not have permission to view this report.")
                return Response(
                    {"error": "You don't have permission to view this report"}, 
                    status=status.HTTP_403_FORBIDDEN
                )

            # Check if file exists
            if not report.report_file or not report.report_file.file:
                logger.warning("DownloadReportView: Report file not found.")
                return Response(
                    {"error": "Report file not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # Serve the file
            try:
                response = HttpResponse(
                    report.report_file.read(), 
                    content_type='application/pdf'
                )
                filename = f"patient_report_{report.patient.user.username}_{report.generated_at.strftime('%Y%m%d')}.pdf"
                # Always use inline display for mobile/browser
                response['Content-Disposition'] = f'inline; filename="{filename}"'
                response['Content-Length'] = report.report_file.size
                logger.info(f"DownloadReportView: Serving report {filename} to user {request.user}")
                return response
            except Exception as e:
                logger.error(f"DownloadReportView: Failed to read report file: {e}")
                return Response(
                    {"error": f"Failed to read report file: {str(e)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"DownloadReportView: General error: {e}")
            return Response(
                {"error": f"Failed to open report: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PatientReportsListView(APIView):
    """Get all reports for a specific patient"""
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CombinedJWTAuthentication, SessionAuthentication]
    
    def get(self, request, patient_id):
        try:
            # Check if user is a doctor
            if not hasattr(request.user, 'doctor'):
                return Response(
                    {"error": "Only doctors can access patient reports"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            doctor = request.user.doctor
            
            # Verify doctor has access to this patient
            try:
                patient = Patient.objects.get(id=patient_id)
                
                if not (patient.doctor == doctor or request.user.is_staff or request.user.is_superuser):
                    return Response(
                        {"error": "You don't have permission to view this patient's reports"}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
                
            except Patient.DoesNotExist:
                return Response(
                    {"error": "Patient not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get reports for this patient
            reports = patient.reports.filter(is_active=True).order_by('-generated_at')
            
            reports_data = []
            for report in reports:
                reports_data.append({
                    'id': report.id,
                    'title': report.title,
                    'generated_at': report.generated_at.strftime('%Y-%m-%d %H:%M'),
                    'generated_by': report.generated_by.get_full_name() if report.generated_by else 'System',
                    'file_size': report.file_size,
                    'download_url': f'/accounts/reports/download/{report.id}/',
                    'notes': report.notes,
                    'period_start': report.report_period_start.strftime('%Y-%m-%d') if report.report_period_start else None,
                    'period_end': report.report_period_end.strftime('%Y-%m-%d') if report.report_period_end else None,
                })
            
            return Response({
                'patient': {
                    'id': patient.id,
                    'name': patient.user.get_full_name() or patient.user.username,
                    'email': patient.user.email,
                },
                'reports': reports_data,
                'total_reports': len(reports_data)
            })
            
        except Exception as e:
            return Response(
                {"error": f"Failed to fetch reports: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SimpleReportView(View):
    """Simple PDF view without API authentication - for browser viewing"""
    
    def get(self, request, report_id):
        try:
            # Get the report
            from .models import PatientReport
            try:
                report = PatientReport.objects.select_related('patient__doctor').get(
                    id=report_id,
                    is_active=True
                )
            except PatientReport.DoesNotExist:
                return HttpResponse("Report not found", status=404)
            
            # Check if file exists
            if not report.report_file or not report.report_file.file:
                return HttpResponse("Report file not found", status=404)
            
            # Serve the PDF (without authentication for now - just for testing)
            try:
                response = HttpResponse(
                    report.report_file.read(), 
                    content_type='application/pdf'
                )
                filename = f"patient_report_{report.patient.user.username}_{report.generated_at.strftime('%Y%m%d')}.pdf"
                response['Content-Disposition'] = f'inline; filename="{filename}"'
                response['Content-Length'] = report.report_file.size
                
                return response
                
            except Exception as e:
                return HttpResponse(f"Failed to read report file: {str(e)}", status=500)
            
        except Exception as e:
            return HttpResponse(f"Failed to view report: {str(e)}", status=500)


class TreatmentStepPhotoListCreate(generics.ListCreateAPIView):
    """Create and list photos for a specific treatment step"""
    serializer_class = TreatmentStepPhotoSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CombinedJWTAuthentication, SessionAuthentication]

    def get_queryset(self):
        step_id = self.kwargs['step_id']
        user = self.request.user
        
        # Allow access if user is patient who owns the step or doctor assigned to patient
        if hasattr(user, 'patient'):
            return TreatmentStepPhoto.objects.filter(
                step_id=step_id,
                step__treatment__patient=user.patient
            ).order_by('-uploaded_at')
        elif hasattr(user, 'doctor'):
            return TreatmentStepPhoto.objects.filter(
                step_id=step_id,
                step__treatment__patient__doctor=user.doctor
            ).order_by('-uploaded_at')
        else:
            return TreatmentStepPhoto.objects.none()

    def perform_create(self, serializer):
        step_id = self.kwargs['step_id']
        user = self.request.user
        
        # Verify the step exists and user has permission
        try:
            if hasattr(user, 'patient'):
                step = TreatmentStep.objects.get(
                    id=step_id,
                    treatment__patient=user.patient
                )
            elif hasattr(user, 'doctor'):
                step = TreatmentStep.objects.get(
                    id=step_id,
                    treatment__patient__doctor=user.doctor
                )
            else:
                raise PermissionDenied("You do not have permission to upload photos for this step.")
        except TreatmentStep.DoesNotExist:
            raise PermissionDenied("Treatment step not found or you don't have permission.")
        
        # Save with the step and user
        serializer.save(step=step, uploaded_by=user)


class TreatmentStepPhotoDetail(generics.RetrieveDestroyAPIView):
    """Retrieve and delete a specific treatment step photo"""
    serializer_class = TreatmentStepPhotoSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CombinedJWTAuthentication, SessionAuthentication]

    def get_queryset(self):
        user = self.request.user
        # Allow patient owner or the assigned doctor to access photos
        if hasattr(user, 'patient'):
            return TreatmentStepPhoto.objects.filter(step__treatment__patient=user.patient)
        if hasattr(user, 'doctor'):
            return TreatmentStepPhoto.objects.filter(step__treatment__patient__doctor=user.doctor)
        raise PermissionDenied("You do not have permission to access these photos.")

    def perform_destroy(self, instance):
        user = self.request.user
        # Only the patient who owns the photo may delete it
        if not (hasattr(user, 'patient') and instance.step.treatment.patient == user.patient):
            raise PermissionDenied("Only the patient can delete their own photos.")
        
        try:
            instance.delete()
            # Note: The actual image file remains on ImgBB (permanent storage for medical records)
        except Exception as e:
            from rest_framework.exceptions import APIException
            raise APIException(f"Photo record deleted successfully. Note: Image files are permanently stored for medical record keeping.")