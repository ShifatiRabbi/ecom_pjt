from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('admin/login/', views.admin_login, name='admin_login'),
]