from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Host, Credential
import json


def home(request):
    """Home page with credential and host management"""
    credentials = Credential.objects.all().order_by('-created_at')
    hosts = Host.objects.all().order_by('-created_at')
    
    context = {
        'credentials': credentials,
        'hosts': hosts,
    }
    return render(request, 'terminal/home.html', context)


def terminal(request, host_id, credential_id, session_num):
    """Terminal page for SSH/kubectl exec"""
    host = get_object_or_404(Host, id=host_id)
    credential = get_object_or_404(Credential, id=credential_id)
    
    context = {
        'host': host,
        'credential': credential,
        'session_num': session_num,
    }
    return render(request, 'terminal/terminal.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def add_credential(request):
    """Add new credential"""
    try:
        data = json.loads(request.body)
        credential = Credential.objects.create(
            name=data['name'],
            credential_type=data['credential_type'],
            content=data['content'],
            username=data.get('username', '')
        )
        return JsonResponse({'success': True, 'id': credential.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def add_host(request):
    """Add new host"""
    try:
        data = json.loads(request.body)
        host = Host.objects.create(
            name=data['name'],
            host_type=data['host_type'],
            hostname=data['hostname'],
            port=data.get('port', 22),
            namespace=data.get('namespace', ''),
            container=data.get('container', ''),
            default_credential_id=data.get('default_credential_id')
        )
        return JsonResponse({'success': True, 'id': host.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def delete_credential(request, credential_id):
    """Delete credential"""
    try:
        credential = get_object_or_404(Credential, id=credential_id)
        credential.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def delete_host(request, host_id):
    """Delete host"""
    try:
        host = get_object_or_404(Host, id=host_id)
        host.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def update_host_credential(request, host_id):
    """Update host's default credential"""
    try:
        data = json.loads(request.body)
        host = get_object_or_404(Host, id=host_id)
        host.default_credential_id = data.get('credential_id')
        host.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def open_connection(request, host_id):
    """Show credential selection and redirect to terminal"""
    host = get_object_or_404(Host, id=host_id)
    
    # Determine compatible credentials
    if host.host_type == 'baremetal':
        credentials = Credential.objects.filter(credential_type='ssh_key')
    else:
        credentials = Credential.objects.filter(credential_type='kubeconfig')
    
    if request.method == 'POST':
        credential_id = request.POST.get('credential_id')
        session_num = request.POST.get('session_num', '1')
        return redirect('terminal', host_id=host_id, credential_id=credential_id, session_num=session_num)
    
    context = {
        'host': host,
        'credentials': credentials,
    }
    return render(request, 'terminal/open_connection.html', context)
