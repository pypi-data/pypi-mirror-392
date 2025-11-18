from django.urls import path
from .views import vladik_select2_api

urlpatterns = [
    path("api/", vladik_select2_api, name="vladik_select2_api"),
    
]
