from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_json, name='upload'),
    path('table/', views.show_table, name='table'),
]