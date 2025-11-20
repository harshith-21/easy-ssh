from django.contrib import admin
from .models import Credential, Host


@admin.register(Credential)
class CredentialAdmin(admin.ModelAdmin):
    list_display = ['name', 'credential_type', 'username', 'created_at']
    list_filter = ['credential_type']
    search_fields = ['name', 'username']


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ['name', 'host_type', 'hostname', 'port', 'namespace', 'default_credential', 'created_at']
    list_filter = ['host_type']
    search_fields = ['name', 'hostname']
