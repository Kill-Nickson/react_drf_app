from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('definitely-not-admin-page/', admin.site.urls),
    path('api/', include(('users.routers', 'users'), namespace='api')),
]
