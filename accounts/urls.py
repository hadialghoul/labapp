from django.urls import path
from .views import RegisterView, VerifyEmailCodeView
from .views import doctor_patients,patient_detail
from .views import TreatmentDetailView, PatientTreatmentDetailView
from .views import TreatmentStepPhotoListCreate, TreatmentStepPhotoDetail, PatientTreatmentStepsView
from .views import PatientsListView
from .views import EmailTokenObtainPairView
from .views import get_patient_treatment
from .views import whoami
from .views import PatientReportsListView, DoctorPatientsReportsView, DownloadReportView, SimpleReportView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-code/', VerifyEmailCodeView.as_view(), name='verify_code'),
    path('doctor/patients/', doctor_patients),
    path('doctor/patients/<int:id>/', patient_detail),
    path('doctor/patients/<int:id>/treatment/', get_patient_treatment),
    path('doctor/patients/<int:patient_id>/treatment/', TreatmentDetailView.as_view(), name='treatment-detail'),
    path('patient-treatment/<int:pk>/', PatientTreatmentDetailView.as_view(), name='patient-treatment-detail'),
    path('steps/<int:step_id>/photos/', TreatmentStepPhotoListCreate.as_view(), name='step-photos'),
    path('photos/<int:pk>/', TreatmentStepPhotoDetail.as_view(), name='photo-detail'),
    path('patients/<int:patient_id>/treatment-steps/', PatientTreatmentStepsView.as_view(), name='patient-treatment-steps'),
    path('patients/', PatientsListView.as_view(), name='patients-list'),
    path('token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),  # POST JSON: {"email": "...", "password": "..."}
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', whoami, name='whoami'),
    
    # PDF Reports
    path('reports/patients/', DoctorPatientsReportsView.as_view(), name='doctor-patients-reports'),
    path('reports/download/<int:report_id>/', DownloadReportView.as_view(), name='download-report'),
    path('reports/patient/<int:patient_id>/', PatientReportsListView.as_view(), name='patient-reports-list'),
    path('reports/view/<int:report_id>/', SimpleReportView.as_view(), name='simple-report-view'),
]