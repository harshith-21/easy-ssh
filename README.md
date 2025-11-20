# Easy SSH

Web-based SSH client + Kubernetes exec via browser. Fully Dockerized. Runs on `localhost:9000`.

## Stack
Python, Django, Django Channels (WebSockets), SQLite, paramiko (SSH), kubectl (K8s), xterm.js, Redis, Docker

## Quick Start

```bash
# Start everything
docker-compose up --build

# Or use the helper script
./start.sh
```

Access: **http://localhost:9000/home**

## Usage

### 1. Add Credentials
Home → **+ Add Credential**
- **SSH Key**: Paste private key + username (for baremetal/VMs)
- **Kubeconfig**: Paste kubeconfig content (for K8s pods)

### 2. Add Hosts
Home → **+ Add Host**
- **Baremetal/VM**: hostname/IP + port (default 22)
- **K8s Pod**: pod name + namespace + container (optional)
- Set default credential (optional)

### 3. Connect
Click **Connect** on any host → Select credential → Choose session # → Opens terminal in new tab

**Multiple sessions**: Use different session numbers (e.g., `/terminal/1/1/1`, `/terminal/1/1/2`)

## Project Structure

```
easy-ssh/
├── easy_ssh/          # Django project (settings, urls, asgi)
├── terminal/          # Main app (models, views, consumers, templates)
├── Dockerfile         # Python 3.11 + kubectl
├── docker-compose.yml # Web + Redis
├── requirements.txt   # Django, Channels, paramiko
└── README.md
```

## How It Works

```
Browser (xterm.js) ←→ WebSocket ←→ Django Channels Consumer
                                    ├─→ paramiko (SSH) → Baremetal
                                    └─→ kubectl exec → K8s Pod
```

- **Home page**: CRUD for credentials/hosts (SQLite)
- **Terminal page**: WebSocket connection for real-time I/O
- **SSH**: paramiko creates interactive shell
- **K8s**: kubectl exec subprocess with stdin/stdout streaming

## Development (Local)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start Redis
docker run -p 6379:6379 redis:7-alpine

# Run migrations
python manage.py migrate

# Start server
daphne -b 0.0.0.0 -p 9000 easy_ssh.asgi:application
```

## Database Models

**Credential**: name, type (ssh_key/kubeconfig), content, username  
**Host**: name, type (baremetal/k8s_pod), hostname, port, namespace, container, default_credential

## URL Routes

- `/home/` - Main dashboard
- `/open-connection/{host_id}/` - Select credential
- `/terminal/{host_id}/{credential_id}/{session_num}/` - Terminal
- `/ws/terminal/{host_id}/{credential_id}/{session_num}/` - WebSocket

## API Endpoints

- `POST /api/credential/add/` - Add credential
- `POST /api/credential/delete/{id}/` - Delete credential
- `POST /api/host/add/` - Add host
- `POST /api/host/delete/{id}/` - Delete host
- `POST /api/host/{id}/update-credential/` - Update default credential

## Commands

```bash
# Start
docker-compose up --build

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Rebuild after code changes
docker-compose up --build

# Access Django admin (create superuser first)
docker-compose exec web python manage.py createsuperuser
# Then go to: http://localhost:9000/admin
```

## Troubleshooting

**Port 9000 in use**: `lsof -ti:9000 | xargs kill -9` or edit `docker-compose.yml`  
**SSH fails**: Check key format (PEM), username, host allows key auth  
**kubectl fails**: Verify kubeconfig, pod name, namespace  
**WebSocket fails**: Check Redis running (`docker-compose ps`), browser console  

## Security ⚠️

**For personal/local use only** - No authentication, no encryption at rest, HTTP only.  
- Don't expose port 9000 to public networks
- Use firewall rules to restrict access
- Production: add auth + HTTPS + credential encryption

## Phase 2 Ideas

Session persistence on refresh, PostgreSQL, multi-user auth, credential encryption, SCP/SFTP file transfer, command history, session recording, themes

## License

MIT

