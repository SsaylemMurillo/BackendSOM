from rest_framework import serializers
from .models import KohonenConfig, Image

class KohonenConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = KohonenConfig
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image', 'name', 'upload_date']
