from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('credit.urls')),  # Include the URLs from your app
    # Add the following line to handle the root path
    path('', include('credit.urls')),  # Redirect to your app's URLs for the root path
]
