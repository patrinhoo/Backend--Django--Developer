from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from django.core.files.base import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone

from io import BytesIO, StringIO
from PIL import Image as PIL_Image
import datetime

from .models import MyUser, TemporaryLink, Role, Size, Image


def get_image_file(name='test.png', ext='png', size=(50, 50), color=(256, 0, 0)):
    file_obj = BytesIO()
    image = PIL_Image.new("RGB", size=size, color=color)
    image.save(file_obj, ext)
    file_obj.seek(0)
    return File(file_obj, name=name)


def get_temporary_text_file(name='test.txt', content='test'):
    io = StringIO()
    io.write(content)
    text_file = InMemoryUploadedFile(io, None, name, 'text', io, None)
    text_file.seek(0)
    return text_file


# TESTS
class GetRoutesTestCase(APITestCase):
    def test_get_routes(self):
        url = reverse('get-routes')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ImageViewTestCase(APITestCase):
    def setUp(self):
        self.role = Role.objects.create(name='Basic', link_to_original=False, fetch_binary=False)
        self.test_user1 = MyUser.objects.create(username='testuser1', password='testpassword1', role=self.role)
        self.test_user2 = MyUser.objects.create(username='testuser2', password='testpassword2', role=self.role)
        self.image1 = Image.objects.create(image=get_image_file(), author=self.test_user1)
        self.image2 = Image.objects.create(image=get_image_file(), author=self.test_user2)
        self.client.force_authenticate(self.test_user1)

    def test_get_original_allowed(self):
        response = self.client.get(reverse('get-original-image', kwargs={'pk': self.image1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_original_not_allowed(self):
        response = self.client.get(reverse('get-original-image', kwargs={'pk': self.image2.id}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_original_wrong_id(self):
        response = self.client.get(reverse('get-original-image', kwargs={'pk': self.image2.id + 1}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ImagesViewTestCase(APITestCase):
    def setUp(self):
        self.role = Role.objects.create(name='Basic', link_to_original=False, fetch_binary=False)
        self.test_user = MyUser.objects.create(username='testuser1', password='testpassword1', role=self.role)
        self.image = Image.objects.create(image=get_image_file(), author=self.test_user)
        self.client.force_authenticate(self.test_user)

    def test_get_my_images(self):
        response = self.client.get(reverse('images'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('image_ids'), [self.image.id])

    def test_post_image_no_file(self):
        response = self.client.post(reverse('images'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_invalid_extension(self):
        response = self.client.post(reverse('images'), {'image': get_temporary_text_file()})
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_post_image_created(self):
        response = self.client.post(reverse('images'), {'image': get_image_file()})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class getThumbnailURLTestCase(APITestCase):
    def setUp(self):
        self.size = Size.objects.create(height=200)
        self.role = Role.objects.create(name='Basic', link_to_original=False, fetch_binary=False)
        self.role.sizes.add(self.size)
        self.test_user1 = MyUser.objects.create(username='testuser1', password='testpassword1', role=self.role)
        self.test_user2 = MyUser.objects.create(username='testuser2', password='testpassword2', role=self.role)
        self.image1 = Image.objects.create(image=get_image_file(), author=self.test_user1)
        self.image2 = Image.objects.create(image=get_image_file(), author=self.test_user2)
        self.client.force_authenticate(self.test_user1)

    def test_get_thumbnail_wrong_id(self):
        response = self.client.get(reverse('get-thumbnail', kwargs={'pk': self.image2.id + 1, 'height': 200}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_thumbnail_not_author(self):
        response = self.client.get(reverse('get-thumbnail', kwargs={'pk': self.image2.id, 'height': 200}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_thumbnail_size_not_allowed(self):
        response = self.client.get(reverse('get-thumbnail', kwargs={'pk': self.image1.id, 'height': 500}))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_thumbnail_ok(self):
        response = self.client.get(reverse('get-thumbnail', kwargs={'pk': self.image1.id, 'height': 200}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class getTemporaryLinkTestCase(APITestCase):
    def setUp(self):
        self.role = Role.objects.create(name='Basic', link_to_original=False, fetch_binary=False)
        self.test_user1 = MyUser.objects.create(username='testuser1', password='testpassword1', role=self.role)
        self.test_user2 = MyUser.objects.create(username='testuser2', password='testpassword2', role=self.role)
        self.image1 = Image.objects.create(image=get_image_file(), author=self.test_user1)
        self.image2 = Image.objects.create(image=get_image_file(), author=self.test_user2)
        self.client.force_authenticate(self.test_user1)
     
    def test_get_link_wrong_id(self):
        response = self.client.get(reverse('get-link', kwargs={'pk': self.image2.id + 1, 'seconds': 500}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_link_wrong_seconds(self):
        response1 = self.client.get(reverse('get-link', kwargs={'pk': self.image1.id , 'seconds': 200}))
        response2 = self.client.get(reverse('get-link', kwargs={'pk': self.image1.id , 'seconds': 40000}))
        
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_link_not_author(self):
        response = self.client.get(reverse('get-link', kwargs={'pk': self.image2.id, 'seconds': 500}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_link_ok(self):
        response = self.client.get(reverse('get-link', kwargs={'pk': self.image1.id, 'seconds': 500}))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class useTemporaryLinkTestCase(APITestCase):
    def setUp(self):
        self.role = Role.objects.create(name='Basic', link_to_original=False, fetch_binary=False)
        self.test_user = MyUser.objects.create(username='testuser1', password='testpassword1', role=self.role)
        self.image = Image.objects.create(image=get_image_file(), author=self.test_user)
        self.correct_link = TemporaryLink.objects.create(image=self.image, expiration_datetime=timezone.now() + datetime.timedelta(seconds=500))
        self.expired_link = TemporaryLink.objects.create(image=self.image, expiration_datetime=timezone.now() - datetime.timedelta(seconds=500))

    def test_use_link_wrong_id(self):
        response = self.client.get(reverse('download', kwargs={'pk': self.expired_link.id+1}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_use_link_expired(self):
        response = self.client.get(reverse('download', kwargs={'pk': self.expired_link.id}))
        self.assertEqual(response.status_code, status.HTTP_410_GONE)

    def test_use_link_ok(self):
        response = self.client.get(reverse('download', kwargs={'pk': self.correct_link.id}))
        self.assertEqual(response.get('Content-Disposition'), "attachment; filename=image.png")