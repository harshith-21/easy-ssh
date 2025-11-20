from django.db import models


class Credential(models.Model):
    CREDENTIAL_TYPES = [
        ('ssh_key', 'SSH Key'),
        ('kubeconfig', 'Kubeconfig'),
    ]
    
    name = models.CharField(max_length=255, unique=True)
    credential_type = models.CharField(max_length=20, choices=CREDENTIAL_TYPES)
    content = models.TextField(help_text="SSH private key or kubeconfig content")
    username = models.CharField(max_length=255, blank=True, null=True, help_text="SSH username (only for SSH keys)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_credential_type_display()})"


class Host(models.Model):
    HOST_TYPES = [
        ('baremetal', 'Baremetal/VM'),
        ('k8s_pod', 'Kubernetes Pod'),
    ]
    
    name = models.CharField(max_length=255, unique=True)
    host_type = models.CharField(max_length=20, choices=HOST_TYPES)
    hostname = models.CharField(max_length=255, help_text="IP/hostname for baremetal, pod name for K8s")
    port = models.IntegerField(default=22, help_text="SSH port (only for baremetal)")
    namespace = models.CharField(max_length=255, blank=True, null=True, help_text="K8s namespace (only for pods)")
    container = models.CharField(max_length=255, blank=True, null=True, help_text="K8s container name (optional)")
    default_credential = models.ForeignKey(
        Credential, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Default credential for this host"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.hostname})"
