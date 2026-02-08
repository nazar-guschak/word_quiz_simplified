from django.contrib.auth.views import LogoutView
from django.urls import path, include
from . import views

app_name = 'users'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('register', views.register, name='register'),
]