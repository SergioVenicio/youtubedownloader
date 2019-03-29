from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home_page'),
    path('get', views.get, name='get_page'),
]
