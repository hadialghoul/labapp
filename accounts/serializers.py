from rest_framework import serializers
from .models import CustomUser, Patient, Treatment, PatientTreatment, TreatmentStep, TreatmentStepPhoto

class UserCreateSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'password', 'confirm_password')

    def validate(self, data):
        # Check if password and confirm_password match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords must match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # Remove confirm_password field
        user = CustomUser.objects.create_user(**validated_data)
        user.is_active = False  # Set user as inactive initially
        user.is_patient = True  # Assume patient registration, can be adjusted for doctors
        user.save()

        # Create patient profile
        Patient.objects.create(user=user)
        return user


# Define the UserSerializer that is required by Djoser
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'is_patient', 'is_doctor')

class PatientSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = Patient
        fields = ['id', 'username', 'phone', 'email']




class TreatmentSerializer(serializers.ModelSerializer):
    qr_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Treatment
        fields = ['id', 'patient', 'current_stage', 'qr_image_url']

    def get_qr_image_url(self, obj):
        # Always use the permanent ImgBB URL if available
        if obj.qr_image_url:
            return obj.qr_image_url
        request = self.context.get('request')
        if obj.qr_image and hasattr(obj.qr_image, 'url'):
            return request.build_absolute_uri(obj.qr_image.url) if request else obj.qr_image.url
        return None


class TreatmentStepPhotoSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    uploaded_by = serializers.StringRelatedField(read_only=True)
    uploaded_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = TreatmentStepPhoto
        fields = ['id', 'image', 'image_url', 'uploaded_by', 'uploaded_at']
        read_only_fields = ['uploaded_by', 'uploaded_at']

    def get_image_url(self, obj):
        # Always use the permanent ImgBB URL if available
        if obj.image_url:
            return obj.image_url
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

class TreatmentStepSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    photos = TreatmentStepPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = TreatmentStep
        fields = ['id', 'name', 'description', 'image', 'image_url', 'photos', 'duration_days', 'start_date']

    def get_image_url(self, obj):
        # Always use the permanent ImgBB URL if available
        if obj.image_url:
            return obj.image_url
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

class PatientTreatmentSerializer(serializers.ModelSerializer):
    steps = TreatmentStepSerializer(many=True, read_only=True)

    class Meta:
        model = PatientTreatment
        fields = ['id', 'patient', 'steps']