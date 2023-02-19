from django.contrib import admin
from .models import MyUser, Role, Size, Image, TemporaryLink

# Register your models here.
admin.site.register(MyUser)
admin.site.register(Role)
admin.site.register(Size)
admin.site.register(Image)
admin.site.register(TemporaryLink)