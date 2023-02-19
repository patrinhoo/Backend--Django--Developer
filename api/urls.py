from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from . import views


urlpatterns = [
    path('', views.getRoutes.as_view(), name='get-routes'),

    path('token/', TokenObtainPairView.as_view(), name='obtain-token-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh-token'),

    path('images/', views.ImagesView.as_view(), name='images'),
    path('images/<int:pk>/', views.ImageView.as_view(), name='get-original-image'),
    path('images/<int:pk>/<int:height>/', views.getThumbnailURL.as_view(), name='get-thumbnail'),

    path('link/<int:pk>/<int:seconds>/', views.getTemporaryLink.as_view(), name='get-link'),
    path('download/<int:pk>/', views.useTemporaryLink.as_view(), name='download'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
