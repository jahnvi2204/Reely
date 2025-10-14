# Reely Deployment Guide

This guide covers deploying the Reely Video Captioning Platform to production environments.

## 🚀 Deployment Options

### 1. Docker Deployment (Recommended)

#### Prerequisites
- Docker and Docker Compose installed
- Domain name and SSL certificate
- MongoDB Atlas account (or self-hosted MongoDB)
- Redis Cloud account (or self-hosted Redis)

#### Steps

1. **Clone and configure**
   ```bash
   git clone <repository-url>
   cd reely
   ```

2. **Configure environment variables**
   ```bash
   # Backend
   cp backend/env.example backend/.env
   # Edit backend/.env with production values
   
   # Frontend
   cp frontend/env.example frontend/.env.local
   # Edit frontend/.env.local with production values
   ```

3. **Deploy with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Verify deployment**
   ```bash
   docker-compose ps
   curl http://localhost:8000/health
   ```

### 2. Cloud Platform Deployment

#### AWS Deployment

**Backend (ECS/Fargate)**
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  api:
    image: reely-backend:latest
    environment:
      - MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/reely
      - REDIS_URL=redis://redis-cluster.cache.amazonaws.com:6379
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - S3_BUCKET_NAME=reely-videos-prod
    ports:
      - "8000:8000"
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

**Frontend (S3 + CloudFront)**
```bash
# Build frontend
cd frontend
npm run build

# Deploy to S3
aws s3 sync dist/ s3://reely-frontend-bucket --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id DISTRIBUTION_ID --paths "/*"
```

#### Google Cloud Platform

**Backend (Cloud Run)**
```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/reely-backend', './backend']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/reely-backend']
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['run', 'deploy', 'reely-backend', '--image', 'gcr.io/$PROJECT_ID/reely-backend', '--platform', 'managed', '--region', 'us-central1']
```

**Frontend (Firebase Hosting)**
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Initialize Firebase
firebase init hosting

# Deploy
npm run build
firebase deploy
```

#### DigitalOcean App Platform

**app.yaml**
```yaml
name: reely-platform
services:
- name: backend
  source_dir: backend
  github:
    repo: your-username/reely
    branch: main
  run_command: uvicorn app.main:app --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_count: 2
  instance_size_slug: basic-xxs
  envs:
  - key: MONGODB_URL
    value: ${MONGODB_URL}
  - key: REDIS_URL
    value: ${REDIS_URL}

- name: frontend
  source_dir: frontend
  github:
    repo: your-username/reely
    branch: main
  run_command: npm run build && npx serve -s dist -l 3000
  environment_slug: node-js
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: VITE_API_BASE_URL
    value: ${BACKEND_URL}

workers:
- name: celery-worker
  source_dir: backend
  github:
    repo: your-username/reely
    branch: main
  run_command: celery -A app.tasks.worker worker --loglevel=info
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: MONGODB_URL
    value: ${MONGODB_URL}
  - key: REDIS_URL
    value: ${REDIS_URL}
```

### 3. Self-Hosted Deployment

#### VPS Deployment (Ubuntu 20.04+)

1. **Server setup**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install dependencies
   sudo apt install -y python3.9 python3.9-venv nodejs npm nginx redis-server mongodb
   
   # Install FFmpeg
   sudo apt install -y ffmpeg
   ```

2. **Application deployment**
   ```bash
   # Clone repository
   git clone <repository-url> /opt/reely
   cd /opt/reely
   
   # Setup backend
   cd backend
   python3.9 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Setup frontend
   cd ../frontend
   npm install
   npm run build
   ```

3. **Systemd services**
   ```bash
   # /etc/systemd/system/reely-backend.service
   [Unit]
   Description=Reely Backend API
   After=network.target
   
   [Service]
   Type=exec
   User=www-data
   WorkingDirectory=/opt/reely/backend
   Environment=PATH=/opt/reely/backend/venv/bin
   ExecStart=/opt/reely/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   
   # /etc/systemd/system/reely-worker.service
   [Unit]
   Description=Reely Celery Worker
   After=network.target
   
   [Service]
   Type=exec
   User=www-data
   WorkingDirectory=/opt/reely/backend
   Environment=PATH=/opt/reely/backend/venv/bin
   ExecStart=/opt/reely/backend/venv/bin/celery -A app.tasks.worker worker --loglevel=info
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Nginx configuration**
   ```nginx
   # /etc/nginx/sites-available/reely
   server {
       listen 80;
       server_name your-domain.com;
       
       # Frontend
       location / {
           root /opt/reely/frontend/dist;
           try_files $uri $uri/ /index.html;
       }
       
       # Backend API
       location /api/ {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
       
       # WebSocket support (if needed)
       location /ws/ {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }
   }
   ```

## 🔧 Production Configuration

### Environment Variables

**Backend (.env)**
```env
# Production settings
DEBUG=False
SECRET_KEY=your-super-secret-key-here

# Database
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/reely_prod
DATABASE_NAME=reely_prod

# Redis
REDIS_URL=redis://redis-cluster.cache.amazonaws.com:6379

# AWS S3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=reely-videos-prod

# File storage
UPLOAD_DIR=/app/uploads
PROCESSED_DIR=/app/processed
MAX_FILE_SIZE_MB=500

# CORS
CORS_ORIGINS=["https://your-domain.com"]

# Celery
CELERY_BROKER_URL=redis://redis-cluster.cache.amazonaws.com:6379
CELERY_RESULT_BACKEND=redis://redis-cluster.cache.amazonaws.com:6379
```

**Frontend (.env.local)**
```env
# Production API
VITE_API_BASE_URL=https://api.your-domain.com

# Firebase (production)
VITE_FIREBASE_API_KEY=your-production-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id

# Production settings
VITE_DEBUG=false
```

### Security Considerations

1. **SSL/TLS Certificates**
   ```bash
   # Using Let's Encrypt
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

2. **Firewall Configuration**
   ```bash
   # UFW setup
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

3. **Database Security**
   - Use MongoDB Atlas with IP whitelisting
   - Enable authentication
   - Use connection strings with credentials

4. **API Security**
   - Implement rate limiting
   - Use API keys for external access
   - Validate all inputs
   - Enable CORS properly

## 📊 Monitoring and Logging

### Application Monitoring

**Backend Logging**
```python
# app/core/logging.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    logHandler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)
```

**Health Checks**
```python
# app/api/health.py
@router.get("/health/detailed")
async def detailed_health_check():
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "storage": await check_storage(),
        "celery": await check_celery()
    }
    return {"status": "healthy", "checks": checks}
```

### Infrastructure Monitoring

**Prometheus + Grafana**
```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: ./run_tests.sh all
  
  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to AWS ECS
        run: |
          aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
          docker build -t $ECR_REGISTRY/reely-backend ./backend
          docker push $ECR_REGISTRY/reely-backend
          aws ecs update-service --cluster reely-cluster --service reely-backend --force-new-deployment
  
  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to S3
        run: |
          cd frontend
          npm install
          npm run build
          aws s3 sync dist/ s3://reely-frontend-bucket --delete
          aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*"
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check MongoDB connection
   mongosh "mongodb+srv://cluster.mongodb.net/reely" --username user --password pass
   
   # Check Redis connection
   redis-cli -h redis-cluster.cache.amazonaws.com -p 6379 ping
   ```

2. **File Upload Issues**
   ```bash
   # Check file permissions
   ls -la /app/uploads/
   chown -R www-data:www-data /app/uploads/
   ```

3. **Celery Worker Issues**
   ```bash
   # Check worker status
   celery -A app.tasks.worker inspect active
   
   # Restart workers
   sudo systemctl restart reely-worker
   ```

### Performance Optimization

1. **Database Optimization**
   ```python
   # Add indexes
   db.videos.create_index("video_id", unique=True)
   db.videos.create_index("created_at")
   db.videos.create_index("status")
   ```

2. **Caching Strategy**
   ```python
   # Redis caching
   @cache.memoize(timeout=3600)
   def get_video_metadata(video_id):
       return db.videos.find_one({"video_id": video_id})
   ```

3. **CDN Configuration**
   ```bash
   # CloudFront settings
   - Cache static assets for 1 year
   - Cache API responses for 5 minutes
   - Enable compression
   ```

## 📈 Scaling Considerations

### Horizontal Scaling

1. **Load Balancer Configuration**
   ```nginx
   upstream backend {
       server backend1:8000;
       server backend2:8000;
       server backend3:8000;
   }
   ```

2. **Database Scaling**
   - Use MongoDB sharding
   - Implement read replicas
   - Use connection pooling

3. **Worker Scaling**
   ```bash
   # Scale Celery workers
   docker-compose up --scale worker=5
   ```

### Vertical Scaling

1. **Resource Allocation**
   - Increase memory for video processing
   - Use GPU instances for Whisper
   - Optimize database queries

2. **Storage Scaling**
   - Use S3 lifecycle policies
   - Implement file compression
   - Use CDN for video delivery

This deployment guide provides comprehensive instructions for deploying Reely to various production environments. Choose the deployment method that best fits your infrastructure and requirements.
