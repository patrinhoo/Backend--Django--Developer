from rest_framework.serializers import ModelSerializer
from .models import Image, TemporaryLink


class ImageSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']


class ImageCreateSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = ['image', 'author']


class ImageUploadSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = ['image',]


class TemporaryLinkSerializer(ModelSerializer):
    class Meta:
        model = TemporaryLink
        fields = '__all__'
