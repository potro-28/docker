from django.urls import path
from .views import DashboardUsuarioView

app_name = 'usuarios'

urlpatterns = [
    path('dashboard/', DashboardUsuarioView.as_view(), name='dashboard_usuario'),
]