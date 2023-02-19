from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator

from django.db.models.signals import post_save
from django.dispatch import receiver

from .utils import rotate_image

from sorl.thumbnail import ImageField
import os


# Create your models here.
class Size(models.Model):
    height = models.IntegerField()

    def __str__(self):
        return str(self.id) + '. ' + str(self.height)
    

class Role(models.Model):
    name = models.TextField(max_length=50)
    link_to_original = models.BooleanField()
    fetch_binary = models.BooleanField()
    sizes = models.ManyToManyField(Size)

    def __str__(self):
        return str(self.id) + '. ' + self.name
    

class MyUser(AbstractUser):
    """User model."""

    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.id) + '. ' + self.username
    

class Image(models.Model):
    image = ImageField(upload_to='images', validators=[FileExtensionValidator( ['png', 'jpg'] ) ])
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)


@receiver(post_save, sender=Image, dispatch_uid="update_image")
def update_image(sender, instance, **kwargs):
  if instance.image:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fullpath = BASE_DIR + instance.image.url
    rotate_image(fullpath)


class TemporaryLink(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    expiration_datetime = models.DateTimeField()
    