"""BookingService URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from django.views.static import serve
from filebrowser.sites import site

from django.conf import settings


def protected_files_serve(request, path, path2, document_root=None, show_indexes=False):
    """Function for access settings on user files"""
    if path == 'qrs':
        return serve(request, str(path) + '/' + str(path2), document_root, show_indexes)
    if request.user.role.lower() == 'admin':
        return serve(request, str(path) + '/' + str(path2), document_root, show_indexes)
    return HttpResponse('404')


urlpatterns = [
    path('admin/filebrowser/', site.urls),
    path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls),
    path('', include('myauth.urls'), name='myauth'),
    path('', include('booking.urls'), name='bookings'),
    path('buses/', include('buses.urls'), name='buses'),
    path(r'user_files/<path>/<path2>', protected_files_serve, {'document_root': settings.FILEBROWSER_DIRECTORY}),
    path("select2/", include("django_select2.urls")),
]
