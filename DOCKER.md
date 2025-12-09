# Face Recognition App - Docker Setup

## Quick Start with Docker

### Prerequisites
- Docker Desktop installed
- Docker Compose installed (comes with Docker Desktop)

### Run the Application

1. **Build and start all services:**
```bash
docker-compose up --build
```

2. **Start in detached mode (background):**
```bash
docker-compose up -d
```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

4. **Stop the services:**
```bash
docker-compose down
```

5. **Stop and remove volumes (deletes database):**
```bash
docker-compose down -v
```

## Docker Commands

### View logs
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Restart services
```bash
# Restart all
docker-compose restart

# Restart backend only
docker-compose restart backend

# Restart frontend only
docker-compose restart frontend
```

### Rebuild after code changes
```bash
# Rebuild all
docker-compose up --build

# Rebuild specific service
docker-compose up --build backend
docker-compose up --build frontend
```

### Check service status
```bash
docker-compose ps
```

### Execute commands in containers
```bash
# Backend shell
docker-compose exec backend /bin/bash

# Frontend shell
docker-compose exec frontend /bin/sh

# Run Python in backend
docker-compose exec backend python
```

## Volume Management

### Database Persistence
The database folder is mounted as a volume, so your registered faces persist even when containers are stopped:
- Location: `./backend/database`

### Model Cache
DeepFace models are cached in a Docker volume to avoid re-downloading:
- Volume name: `facerec_model-cache`

### Backup Database
```bash
# Create backup
docker cp facerec-backend:/app/database ./database-backup

# Restore backup
docker cp ./database-backup/. facerec-backend:/app/database
```

## Production Deployment

### Environment Variables

Create `.env` file in root directory:
```env
# Backend
FLASK_ENV=production

# Frontend
NEXT_PUBLIC_API_URL=http://your-domain.com:5000
```

### Using .env file
```bash
docker-compose --env-file .env up -d
```

### Behind Reverse Proxy (Nginx)

If deploying behind Nginx or similar:

1. Update `docker-compose.yml` to not expose ports:
```yaml
services:
  backend:
    # Remove or comment out ports section
    # ports:
    #   - "5000:5000"
```

2. Configure Nginx to proxy to containers

## Troubleshooting

### Backend fails to start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Port 5000 already in use
# - Insufficient memory for TensorFlow
```

### Frontend can't connect to backend
```bash
# Check if backend is running
docker-compose ps

# Check backend health
curl http://localhost:5000/api/health

# Verify network
docker network inspect facerec_facerec-network
```

### Model download fails
```bash
# The model downloads on first recognition
# If it fails, check internet connection

# Manually download and place in volume:
docker-compose exec backend bash
cd /root/.deepface/weights
# Download vgg_face_weights.h5 manually
```

### Out of memory
```bash
# Increase Docker memory in Docker Desktop settings
# Minimum recommended: 4GB
# Optimal: 8GB
```

### Permission issues (Linux)
```bash
# Fix permissions on database folder
sudo chown -R $USER:$USER ./backend/database

# Run with proper user
docker-compose run --user $(id -u):$(id -g) backend
```

## Development with Docker

### Hot Reload (Development Mode)

Modify `docker-compose.yml` for development:

```yaml
services:
  backend:
    command: python app.py
    volumes:
      - ./backend:/app
      - ./backend/database:/app/database
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1

  frontend:
    command: npm run dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
```

### Development compose file
```bash
# Use override file
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## Optimization

### Reduce Image Size
Images are already optimized with:
- Multi-stage builds (frontend)
- Slim Python image (backend)
- .dockerignore files

### Build cache
Docker caches layers. To clear:
```bash
# Clear build cache
docker builder prune

# Clear everything
docker system prune -a
```

## Security Notes

For production:
1. Don't run as root user
2. Use secrets for sensitive data
3. Enable HTTPS
4. Use specific image tags (not `latest`)
5. Scan images for vulnerabilities:
```bash
docker scan facerec-backend
docker scan facerec-frontend
```

## Performance

### Resource Limits

Add to `docker-compose.yml`:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          memory: 2G
```

## Multi-Platform Builds

For ARM64 (Apple Silicon) and AMD64:
```bash
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 -t facerec-backend ./backend
```

## Docker Hub Deployment

```bash
# Tag images
docker tag facerec-backend yourusername/facerec-backend:latest
docker tag facerec-frontend yourusername/facerec-frontend:latest

# Push to Docker Hub
docker push yourusername/facerec-backend:latest
docker push yourusername/facerec-frontend:latest
```

## Quick Commands Cheat Sheet

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Rebuild
docker-compose up --build

# Logs
docker-compose logs -f

# Shell access
docker-compose exec backend bash
docker-compose exec frontend sh

# Remove everything
docker-compose down -v --rmi all
```
