"""
URL configuration for webapps project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from write_on_cue import views
from write_on_cue.views import upload_audio, convert_midi
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage_action, name='home'),
    path('homepage', views.homepage_action, name='homepage'),
    path('profile', views.profile_action, name='profile'),
    path('transcriptions', views.transcriptions_action, name='transcriptions'),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('logout', auth_views.logout_then_login, name='logout'),
    path("upload-audio/", upload_audio, name="upload_audio"),
    path('run-script/', views.run_script, name='run_script'),
    path("convert-midi/", convert_midi, name="convert_midi"),
    #path('fashion_marketplace/get-my-items', views.get_my_items, name='get-my-items'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)