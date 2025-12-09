# Docker Deployment Guide

## 🐳 What's Included

- **Backend Dockerfile**: Python Flask API with DeepFace
- **Frontend Dockerfile**: Next.js application
- **docker-compose.yml**: Production setup
- **docker-compose.dev.yml**: Development with hot reload
- **Batch scripts**: Easy Windows deployment

## 📦 Files Created

```
facerec/
├── docker-compose.yml          # Main Docker Compose config
├── docker-compose.dev.yml      # Development override
├── docker-start.bat            # Windows: Start containers
├── docker-stop.bat             # Windows: Stop containers
├── .env.example                # Environment variables template
├── DOCKER.md                   # Detailed Docker guide
│
├── backend/
│   ├── Dockerfile              # Backend container config
│   └── .dockerignore          # Files to exclude
│
└── frontend/
    ├── Dockerfile              # Frontend production config
    ├── Dockerfile.dev          # Frontend development config
    └── .dockerignore          # Files to exclude
```

## 🚀 Quick Start

### Option 1: Windows Batch Files (Easiest)

```bash
# Start the app
docker-start.bat

# Stop the app
docker-stop.bat
```

### Option 2: Command Line

```bash
# Build and start (first time)
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

### Option 3: Development Mode (Hot Reload)

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## 🌐 Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

## 📊 Container Overview

### Backend Container
- **Base Image**: `python:3.11-slim`
- **Port**: 5000
- **Volumes**: 
  - `./backend/database` → Persists registered faces
  - `model-cache` → Caches DeepFace models
- **Healthcheck**: Pings `/api/health` every 30s

### Frontend Container
- **Base Image**: `node:18-alpine`
- **Port**: 3000
- **Depends on**: Backend service
- **Healthcheck**: Checks port 3000 availability

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```env
# Backend
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:5000
```

### Using .env file

```bash
docker-compose --env-file .env up
```

## 📂 Data Persistence

### Database Volume
- **Location**: `./backend/database`
- **Contains**: Face images and people.json
- **Persistence**: Survives container restarts
- **Backup**: `docker cp facerec-backend:/app/database ./backup`

### Model Cache Volume
- **Volume Name**: `facerec_model-cache`
- **Contains**: VGG-Face model weights (~580MB)
- **Purpose**: Avoid re-downloading on container restart
- **Location**: `/root/.deepface` in container

## 🔨 Common Tasks

### View Running Containers
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only  
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart backend
docker-compose restart backend

# Restart frontend
docker-compose restart frontend
```

### Rebuild After Code Changes
```bash
# Rebuild everything
docker-compose up --build

# Rebuild specific service
docker-compose up --build backend
```

### Access Container Shell
```bash
# Backend bash
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend sh
```

### Clean Up Everything
```bash
# Stop and remove containers
docker-compose down

# Also remove volumes (deletes database!)
docker-compose down -v

# Also remove images
docker-compose down --rmi all
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find what's using the port
netstat -ano | findstr :5000
netstat -ano | findstr :3000

# Kill the process or change ports in docker-compose.yml
```

### Backend Fails to Start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Port 5000 occupied
# - Insufficient memory (need 4GB+)
# - Firewall blocking
```

### Frontend Can't Connect to Backend
```bash
# Verify backend is running
docker-compose ps

# Check backend health
curl http://localhost:5000/api/health

# Check environment variable
docker-compose exec frontend printenv NEXT_PUBLIC_API_URL
```

### Model Download Slow/Fails
The VGG-Face model (~580MB) downloads on first recognition:
- **Be patient**: First recognition takes 2-5 minutes
- **Check internet**: Ensure stable connection
- **Manual download**: See DOCKER.md for manual steps

### Out of Memory
```bash
# Increase Docker memory:
# Docker Desktop → Settings → Resources → Memory
# Recommended: 6-8GB
```

### Permission Denied (Linux)
```bash
# Fix ownership
sudo chown -R $USER:$USER ./backend/database

# Or run with user
docker-compose run --user $(id -u):$(id -g) backend
```

## 🔄 Development Workflow

### Development Mode (Hot Reload)
```bash
# Start with dev config
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Code changes auto-reload (both frontend and backend)
```

### Production Mode
```bash
# Build optimized images
docker-compose up --build

# Or use production env
FLASK_ENV=production docker-compose up
```

## 📈 Performance Optimization

### Pre-download Model Weights
```bash
# Start backend and trigger first recognition
# Model will be cached for future uses

# Or manually download to volume:
docker volume inspect facerec_model-cache
# Copy vgg_face_weights.h5 to the mountpoint
```

### Resource Limits
Edit `docker-compose.yml`:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

## 🚢 Production Deployment

### On a Server

1. **Copy files to server**
```bash
scp -r facerec user@server:/path/to/app
```

2. **Update API URL**
Edit `.env`:
```env
NEXT_PUBLIC_API_URL=http://your-domain.com:5000
```

3. **Start containers**
```bash
docker-compose up -d
```

### Behind Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/facerec
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### With SSL (Let's Encrypt)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renew
sudo certbot renew --dry-run
```

## 🏷️ Docker Hub Deployment

### Build and Push
```bash
# Login
docker login

# Tag images
docker tag facerec-backend yourusername/facerec-backend:v1.0
docker tag facerec-frontend yourusername/facerec-frontend:v1.0

# Push
docker push yourusername/facerec-backend:v1.0
docker push yourusername/facerec-frontend:v1.0
```

### Use Pre-built Images
Update `docker-compose.yml`:
```yaml
services:
  backend:
    image: yourusername/facerec-backend:v1.0
    # Remove 'build' section

  frontend:
    image: yourusername/facerec-frontend:v1.0
    # Remove 'build' section
```

## 📊 Monitoring

### Check Resource Usage
```bash
docker stats
```

### Health Checks
```bash
# Backend
curl http://localhost:5000/api/health

# Frontend
curl http://localhost:3000

# Container health status
docker-compose ps
```

## 🔐 Security Best Practices

1. **Don't expose backend port publicly** in production
2. **Use environment variables** for sensitive config
3. **Enable HTTPS** with reverse proxy
4. **Run as non-root user** (add to Dockerfile)
5. **Scan images** for vulnerabilities:
   ```bash
   docker scan facerec-backend
   ```

## 📦 Backup & Restore

### Backup Database
```bash
# Create backup directory
mkdir -p ./backups/$(date +%Y%m%d)

# Copy database
docker cp facerec-backend:/app/database ./backups/$(date +%Y%m%d)/
```

### Restore Database
```bash
# Stop containers
docker-compose down

# Restore files
cp -r ./backups/20251130/database ./backend/

# Restart
docker-compose up -d
```

### Automated Backups (Linux)
```bash
# Add to crontab
0 2 * * * docker cp facerec-backend:/app/database /backup/facerec-$(date +\%Y\%m\%d)
```

## 🎯 Next Steps

1. ✅ Start containers: `docker-compose up -d`
2. ✅ Test the app: http://localhost:3000
3. ✅ Register faces and test recognition
4. ✅ Check logs: `docker-compose logs -f`
5. ✅ Set up backups
6. ✅ Configure reverse proxy (production)
7. ✅ Enable HTTPS (production)

## 📚 Additional Resources

- [DOCKER.md](DOCKER.md) - Comprehensive Docker guide
- [README.md](README.md) - Main project documentation
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Problem solutions
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

---

**Happy Dockerizing! 🐳**
