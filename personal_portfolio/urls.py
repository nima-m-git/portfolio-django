from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello_world/', include('hello_world.urls')),
    path('projects/', include('projects.urls')),
    path('parking_spot/', include('parking_spot.urls')),
]
