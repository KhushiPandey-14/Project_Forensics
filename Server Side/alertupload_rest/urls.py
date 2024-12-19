from . import views
from django.urls import path
from rest_framework.authtoken import views as rest_framework_views
#from django.conf.urls import url
from django.urls import re_path


urlpatterns = [
    # Alert POST
    path('images/', views.post_alert, name='post_alert'),

     # Authentication
    re_path(r'^get_auth_token/$', rest_framework_views.obtain_auth_token, name='get_auth_token'),
]