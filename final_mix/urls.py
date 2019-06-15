"""final_mix URL Configuration

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
from django.contrib import admin
from django.urls import path

from final_mix import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.show_index,name='index'),
    path('keywordVideo/',views.show_keywordVideo,name='keywordVideo'),
    path('api_cat_streamer/', views.api_cat_streamer),
    path('api_streamer_videos/', views.api_streamer_videos),
    path('keywordVideo/api_get_keywordVideo/',views.api_get_keywordVideo),
    path('show_result/',views.show_result),
]
