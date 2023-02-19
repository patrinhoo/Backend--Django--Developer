from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone

from sorl.thumbnail import get_thumbnail
import datetime
import os

from .serializers import ImageSerializer, ImageCreateSerializer, ImageUploadSerializer, TemporaryLinkSerializer
from .models import Image, TemporaryLink


# API VIEWS
class getRoutes(APIView):
    def get(self, request, format=None):
        routes = [
            '/api/token/',
            '/api/token/refresh/',

            '/api/images/',
            '/api/images/<int:pk>/',
            '/api/images/<int:pk>/<int:height>/',

            '/api/link/<int:pk>/<int:seconds>/',
            '/api/download/<int:pk>/',
        ]

        return Response(routes, status=status.HTTP_200_OK)


class ImageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        try:
            image = Image.objects.get(id=pk)
        except:
            error_data = {
                'message': 'There is no image with this id!'
            }
            return Response(error_data, status=status.HTTP_404_NOT_FOUND)

        if image.author != request.user:
            error_data = {
                'message': 'You are not an author of this image!'
            }
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)

        serializer = ImageSerializer(image, many=False)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ImagesView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ImageUploadSerializer

    def get(self, request, format=None):
        data = {}
        data['image_ids'] = [image.id for image in Image.objects.filter(author = request.user)]

        return Response(data, status=status.HTTP_200_OK)


    def post(self, request, format=None):
        try:
            image_file = request.data['image']
            serializer = ImageCreateSerializer(data={'author': request.user.id, 'image': image_file})
        except Exception:
            error_data = {
                'message': 'Error occured while uploading image!'
            }
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
        
        if serializer.is_valid():
            image = serializer.save()
        else:
            error_data = {
                'message': 'Error occured while uploading image! Check if your image\'s extension is .png or .jpg!'
            }
            return Response(error_data, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        response_data = {}

        for size in request.user.role.sizes.all():
            print(image.image.width)
            print(image.image.height)
            calc_width = int(size.height * image.image.width / image.image.height)
            print(calc_width)
            im = get_thumbnail(image.image, f'{calc_width}x{size.height}', crop='center', quality=99)

            response_data[f'thumbnail_{size.height}'] = im.url

        if request.user.role.link_to_original:
            response_data['original'] = image.image.url

        return Response(response_data, status=status.HTTP_201_CREATED)


class getThumbnailURL(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, height, format=None):
        try:
            image = Image.objects.get(id=pk)
        except:
            error_data = {
                'message': 'There is no image with this id!'
            }
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
        
        if image.author != request.user:
            error_data = {
                'message': 'You are not an author of this image!'
            }
            return Response(error_data, status=status.HTTP_403_FORBIDDEN)

        try:
            image.author.role.sizes.get(height=height)

            calc_width = int(height * image.image.width / image.image.height)
            im = get_thumbnail(image.image, f'{calc_width}x{height}', crop='center', quality=99)
            
            return Response({'id': image.id, f'thumbnail_{height}': im.url}, status=status.HTTP_200_OK)
        except:
            error_data = {
                'message': 'You are not allowed to get Thumbnail of this size!'
            }
            return Response(error_data, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class getTemporaryLink(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, seconds, format=None):
        if seconds < 300 or seconds > 30000:
            error_data = {
                'message': 'Seconds must be between 300 and 30 000!'
            }
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            image = Image.objects.get(id=pk)
        except:
            error_data = {
                'message': 'There is no image with this id!'
            }
            return Response(error_data, status=status.HTTP_404_NOT_FOUND)
        
        if image.author != request.user:
            error_data = {
                'message': 'You are not an author of this image!'
            }
            return Response(error_data, status=status.HTTP_403_FORBIDDEN)
        
        try:        
            expiration_datetime = timezone.now() + datetime.timedelta(seconds=seconds)
            serializer = TemporaryLinkSerializer(data={'expiration_datetime': expiration_datetime, 'image': image.pk})
        except Exception:
            error_data = {
                'message': 'Error occured while creating link!'
            }
            return Response(error_data, status=status.HTTP_404_NOT_FOUND)
        
        if serializer.is_valid():
            temporary_link = serializer.save()
        else:
            print(serializer.errors)
            error_data = {
                'message': 'Error occured while creating link!'
            }
            return Response(error_data, status=status.HTTP_404_NOT_FOUND)
        
        link = f'/api/download/{temporary_link.id}/'
        
        return Response({'link': link}, status=status.HTTP_201_CREATED)


class useTemporaryLink(APIView):
    def get(self, request, pk):
        try:
            temp_link = TemporaryLink.objects.get(id=pk)
        except:
            error_data = {
                'message': 'This link doesn\'t exist!'
            }
            return Response(error_data, status=status.HTTP_404_NOT_FOUND)

        now = timezone.now()
        if now > temp_link.expiration_datetime:
            error_data = {
                'message': 'This link has expired!'
            }
            return Response(error_data, status=status.HTTP_410_GONE)

        try:
            image = temp_link.image
            image_url = os.path.join(settings.BASE_DIR, image.image.url[1:])

            image_file = open(image_url, 'rb')
            response = HttpResponse(image_file)

            extension = image_file.name.split('.')[-1]
            response['Content-Disposition'] = f"attachment; filename=image.{extension}"
            return response
        except:
            error_data = {
                    'message': 'Error occured while creating link1!'
            }
            return Response(error_data, status=status.HTTP_404_NOT_FOUND)
