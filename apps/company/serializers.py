from rest_framework import serializers
from django.conf import settings
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ["id", "name", "description", "address", "phone", "email", 
                "logo", "logo_url", "created_at", "updated_at", "user"]

    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return f"{settings.MEDIA_URL}{obj.logo}"
        return None
