# 🐳 Docker Setup Complete!

## What Was Created

### Docker Configuration Files
✅ `backend/Dockerfile` - Python backend container  
✅ `frontend/Dockerfile` - Next.js frontend container (production)  
✅ `frontend/Dockerfile.dev` - Next.js with hot reload (development)  
✅ `docker-compose.yml` - Main orchestration file  
✅ `docker-compose.dev.yml` - Development overrides  
✅ `backend/.dockerignore` - Exclude files from backend image  
✅ `frontend/.dockerignore` - Exclude files from frontend image  

### Helper Files
✅ `docker-start.bat` - Windows: One-click start  
✅ `docker-stop.bat` - Windows: One-click stop  
✅ `.env.example` - Environment variables template  
✅ `DOCKER.md` - Comprehensive Docker documentation  
✅ `DOCKER_SETUP.md` - Quick setup guide  

### Updated Files
✅ `backend/app.py` - Added Docker-friendly configuration  
✅ `README.md` - Added Docker quick start section  
✅ `.gitignore` - Added Docker-related exclusions  

## 🚀 Quick Start Commands

### Using Docker Compose (Cross-platform)

```bash
# Build and start everything
docker-compose up --build

# Run in background (detached mode)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop everything
docker-compose down
```

### Using Batch Files (Windows)

```bash
# Double-click or run:
docker-start.bat    # Starts the app
docker-stop.bat     # Stops the app
```

### Development Mode (Hot Reload)

```bash
# Start with auto-reload on code changes
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## 📦 What's Running

Once started, you'll have:

| Service | URL | Port |
|---------|-----|------|
| Frontend | http://localhost:3000 | 3000 |
| Backend API | http://localhost:5000 | 5000 |
| Health Check | http://localhost:5000/api/health | 5000 |

## 🔧 Key Features

### 1. Data Persistence
- **Database folder** (`./backend/database`) is mounted as volume
- Registered faces persist across container restarts
- Easy backup: just copy the database folder

### 2. Model Caching
- DeepFace models cached in Docker volume
- No re-download needed after first use
- Saves ~580MB download each time

### 3. Health Checks
- Both services have automatic health monitoring
- Docker restarts unhealthy containers
- Check status: `docker-compose ps`

### 4. Networking
- Services communicate via internal network
- Only exposed ports are accessible from host
- Secure by default

## 📊 Container Architecture

```
┌─────────────────────────────────────────┐
│           Docker Host                    │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │   Frontend Container (Node.js)     │ │
│  │   Port: 3000                       │ │
│  │   Image: node:18-alpine            │ │
│  └──────────────┬─────────────────────┘ │
│                 │                        │
│                 │ HTTP Requests          │
│                 ▼                        │
│  ┌────────────────────────────────────┐ │
│  │   Backend Container (Python)       │ │
│  │   Port: 5000                       │ │
│  │   Image: python:3.11-slim          │ │
│  └──────────────┬─────────────────────┘ │
│                 │                        │
│                 ▼                        │
│  ┌────────────────────────────────────┐ │
│  │   Volume: ./backend/database       │ │
│  │   (Persisted face images)          │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │   Volume: model-cache              │ │
│  │   (DeepFace model weights)         │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## 🎯 Common Commands

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend

# Last 50 lines
docker-compose logs --tail=50
```

### Restarting Services
```bash
# Restart everything
docker-compose restart

# Restart backend only
docker-compose restart backend
```

### Rebuilding After Changes
```bash
# Rebuild all images
docker-compose up --build

# Rebuild specific service
docker-compose build backend
docker-compose up -d backend
```

### Accessing Container Shell
```bash
# Backend
docker-compose exec backend bash

# Frontend
docker-compose exec frontend sh
```

### Cleaning Up
```bash
# Stop and remove containers
docker-compose down

# Remove volumes too (deletes database!)
docker-compose down -v

# Remove images as well
docker-compose down --rmi all
```

## 💡 Tips & Best Practices

### 1. First Run
- First recognition will download VGG-Face model (~580MB)
- This takes 2-5 minutes depending on internet speed
- Subsequent runs are instant (model is cached)

### 2. Development
- Use `docker-compose.dev.yml` for hot reload
- Code changes reflect immediately
- No need to rebuild containers

### 3. Production
- Use standard `docker-compose.yml`
- Images are optimized for size
- Enable HTTPS with reverse proxy (Nginx/Caddy)

### 4. Resource Requirements
- **Minimum**: 4GB RAM
- **Recommended**: 8GB RAM
- **Disk**: ~2GB for images + database
- Adjust in Docker Desktop: Settings → Resources

### 5. Backup Strategy
```bash
# Automatic daily backup (Linux/Mac)
# Add to crontab:
0 2 * * * cp -r /path/to/facerec/backend/database /backup/facerec-$(date +\%Y\%m\%d)

# Windows Task Scheduler:
# xcopy C:\path\to\facerec\backend\database C:\backup\facerec-%date% /E /I
```

## 🔍 Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :5000
netstat -ano | findstr :3000

# Change port in docker-compose.yml if needed
```

### Container Won't Start
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Verify Docker is running
docker info
```

### Can't Access Application
```bash
# Check if containers are running
docker-compose ps

# Verify ports are exposed
docker port facerec-frontend
docker port facerec-backend
```

### Out of Memory
```bash
# Increase Docker memory:
# Docker Desktop → Settings → Resources → Memory
# Set to at least 4GB (8GB recommended)
```

## 📚 Documentation

- **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - This file (quick reference)
- **[DOCKER.md](DOCKER.md)** - Comprehensive Docker guide
- **[README.md](README.md)** - Main project documentation
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Problem solutions

## 🎉 You're Ready!

1. Make sure Docker Desktop is running
2. Run: `docker-compose up -d`
3. Open: http://localhost:3000
4. Start recognizing faces!

### Production Deployment?
See **DOCKER.md** for:
- Reverse proxy setup (Nginx)
- SSL/HTTPS configuration
- Environment variables
- Security best practices
- Monitoring and logging

---

**Questions?** Check **DOCKER.md** for detailed documentation!
