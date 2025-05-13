from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreateSerializer(UserCreateSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    document_number = serializers.CharField(required=True)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone_number', 'document_number']

    def validate_document_number(self, value):
        if User.objects.filter(document_number=value).exists():
            raise serializers.ValidationError('Ya existe un usuario con este número de documento')
        return value

    def validate_phone_number(self, value):
        # Eliminar espacios y caracteres no numéricos
        cleaned_number = ''.join(filter(str.isdigit, value))
        if not cleaned_number:
            raise serializers.ValidationError('El número de teléfono debe contener al menos un dígito')
        return cleaned_number

    def perform_create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number'],
            document_number=validated_data['document_number']
        )
        return user

class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number', 'document_number', 'role', 'company', 'is_active', 'date_joined']
        read_only_fields = ['id', 'is_active', 'date_joined']
