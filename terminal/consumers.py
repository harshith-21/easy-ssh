import json
import asyncio
import os
import tempfile
import subprocess
import threading
import select
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Host, Credential
import paramiko


class TerminalConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.host_id = self.scope['url_route']['kwargs']['host_id']
        self.credential_id = self.scope['url_route']['kwargs']['credential_id']
        self.session_num = self.scope['url_route']['kwargs']['session_num']
        
        await self.accept()
        
        # Get host and credential from database
        try:
            host, credential = await self.get_host_and_credential()
            
            if host.host_type == 'baremetal':
                await self.start_ssh_connection(host, credential)
            elif host.host_type == 'k8s_pod':
                await self.start_kubectl_exec(host, credential)
            else:
                await self.send(text_data=json.dumps({
                    'error': 'Unknown host type'
                }))
                await self.close()
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))
            await self.close()

    async def disconnect(self, close_code):
        # Clean up connections
        if hasattr(self, 'ssh_client'):
            self.ssh_client.close()
        if hasattr(self, 'process'):
            self.process.terminate()
            
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            command = data.get('data', '')
            
            if hasattr(self, 'channel'):
                # SSH connection
                self.channel.send(command)
            elif hasattr(self, 'process'):
                # kubectl exec connection
                self.process.stdin.write(command.encode())
                self.process.stdin.flush()
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))

    @database_sync_to_async
    def get_host_and_credential(self):
        host = Host.objects.get(id=self.host_id)
        credential = Credential.objects.get(id=self.credential_id)
        return host, credential

    async def start_ssh_connection(self, host, credential):
        """Start SSH connection using paramiko"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._connect_ssh, host, credential)
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': f'SSH connection failed: {str(e)}'
            }))
            await self.close()

    def _connect_ssh(self, host, credential):
        """Blocking SSH connection"""
        try:
            # Create SSH client
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Write private key to temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pem') as key_file:
                key_file.write(credential.content)
                key_file_path = key_file.name
            
            try:
                # Set proper permissions
                os.chmod(key_file_path, 0o600)
                
                # Connect
                pkey = paramiko.RSAKey.from_private_key_file(key_file_path)
                self.ssh_client.connect(
                    hostname=host.hostname,
                    port=host.port,
                    username=credential.username,
                    pkey=pkey,
                    timeout=10
                )
                
                # Start interactive shell
                self.channel = self.ssh_client.invoke_shell(term='xterm', width=120, height=40)
                
                # Start reading thread
                threading.Thread(target=self._read_ssh_output, daemon=True).start()
                
            finally:
                # Clean up key file
                os.unlink(key_file_path)
                
        except Exception as e:
            raise Exception(f"SSH connection error: {str(e)}")

    def _read_ssh_output(self):
        """Read SSH output in background thread"""
        try:
            while True:
                if self.channel.recv_ready():
                    data = self.channel.recv(1024).decode('utf-8', errors='ignore')
                    asyncio.run(self.send(text_data=json.dumps({'data': data})))
                else:
                    asyncio.run(asyncio.sleep(0.1))
        except:
            pass

    async def start_kubectl_exec(self, host, credential):
        """Start kubectl exec connection"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._connect_kubectl, host, credential)
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': f'Kubectl exec failed: {str(e)}'
            }))
            await self.close()

    def _connect_kubectl(self, host, credential):
        """Blocking kubectl exec connection"""
        try:
            # Write kubeconfig to temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as kube_file:
                kube_file.write(credential.content)
                kube_file_path = kube_file.name
            
            try:
                # Build kubectl command
                cmd = [
                    'kubectl',
                    '--kubeconfig', kube_file_path,
                    'exec',
                    '-i',
                    '-t',
                    '-n', host.namespace or 'default',
                    host.hostname
                ]
                
                if host.container:
                    cmd.extend(['-c', host.container])
                
                cmd.append('--')
                cmd.extend(['/bin/bash', '-i'])
                
                # Start process
                self.process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    bufsize=0
                )
                
                # Start reading thread
                threading.Thread(target=self._read_kubectl_output, daemon=True).start()
                
            finally:
                # Clean up kubeconfig file
                os.unlink(kube_file_path)
                
        except Exception as e:
            raise Exception(f"Kubectl exec error: {str(e)}")

    def _read_kubectl_output(self):
        """Read kubectl output in background thread"""
        try:
            while True:
                # Use select to check if data is available
                ready, _, _ = select.select([self.process.stdout], [], [], 0.1)
                if ready:
                    data = self.process.stdout.read(1024).decode('utf-8', errors='ignore')
                    if data:
                        asyncio.run(self.send(text_data=json.dumps({'data': data})))
                else:
                    if self.process.poll() is not None:
                        break
        except:
            pass

