from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('terminal/<int:host_id>/<int:credential_id>/<int:session_num>/', views.terminal, name='terminal'),
    path('open-connection/<int:host_id>/', views.open_connection, name='open_connection'),
    path('api/credential/add/', views.add_credential, name='add_credential'),
    path('api/credential/delete/<int:credential_id>/', views.delete_credential, name='delete_credential'),
    path('api/host/add/', views.add_host, name='add_host'),
    path('api/host/delete/<int:host_id>/', views.delete_host, name='delete_host'),
    path('api/host/<int:host_id>/update-credential/', views.update_host_credential, name='update_host_credential'),
]

