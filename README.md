# Reely - Automatic Video Captioning Platform

A full-stack application that automatically generates captions for videos using AI-powered speech recognition and provides customizable caption styling options.

## 🎬 Features

### Backend API (Python/FastAPI)
- **Video Processing**: Support for file uploads and public video URLs
- **AI Transcription**: OpenAI Whisper integration for speech-to-text
- **Caption Rendering**: Customizable styling (font, color, size, position)
- **Asynchronous Processing**: Celery-based background task processing
- **Real-time Status**: Live processing status updates
- **File Management**: Local and cloud storage support
- **RESTful API**: Comprehensive REST endpoints

### Frontend Web App (React)
- **Google Authentication**: Secure login using Firebase
- **Interactive Dashboard**: Real-time video processing status
- **Video Upload**: File upload and URL-based processing
- **Caption Customization**: Live preview of styling options
- **Responsive Design**: Mobile-friendly interface
- **Error Handling**: Comprehensive user feedback

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │   FastAPI       │    │   Celery        │
│   (Port 5173)   │◄──►│   Backend       │◄──►│   Workers       │
│   Firebase Auth │    │   (Port 8000)   │    │   (Background)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   MongoDB       │    │   Redis         │
                       │   Database      │    │   Message Queue │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   File Storage  │
                       │   (Local/S3)    │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- FFmpeg
- MongoDB
- Redis
- Firebase project (for authentication)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install FFmpeg**
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt update && sudo apt install ffmpeg
   ```
   
   **macOS:**
   ```bash
   brew install ffmpeg
   ```
   
   **Windows:**
   - Download from https://ffmpeg.org/download.html
   - Add to PATH environment variable

5. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

6. **Start services**
   ```bash
   # Start MongoDB and Redis
   mongod
   redis-server
   
   # Start Celery worker (in new terminal)
   celery -A app.tasks.worker worker --loglevel=info
   
   # Start FastAPI server (in new terminal)
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure Firebase**
   ```bash
   cp env.example .env.local
   # Edit .env.local with your Firebase configuration
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Open in browser**
   Navigate to `http://localhost:5173`

## 📚 Documentation

- [Backend API Documentation](backend/README.md)
- [Frontend Documentation](frontend/README.md)
- [System Design](backend/DESIGN.md)
- [API Reference](http://localhost:8000/docs) (when backend is running)

## 🔧 Configuration

### Backend Environment Variables

```env
# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=reely_db

# Redis
REDIS_URL=redis://localhost:6379/0

# File Storage
UPLOAD_DIR=./uploads
PROCESSED_DIR=./processed
MAX_FILE_SIZE_MB=500

# Whisper Model
WHISPER_MODEL=base

# AWS S3 (optional)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET_NAME=reely-videos
```

### Frontend Environment Variables

```env
# Firebase Configuration
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id

# API Configuration
VITE_API_BASE_URL=http://localhost:8000
```

## 🎯 API Endpoints

### Video Management
- `POST /api/upload` - Upload video file or URL
- `POST /api/caption` - Create captions for existing video
- `GET /api/videos` - List all videos (paginated)
- `GET /api/video/{video_id}` - Get video details
- `GET /api/video/{video_id}/download` - Download video file
- `GET /api/video/{video_id}/status` - Get processing status
- `DELETE /api/video/{video_id}` - Delete video

### System
- `GET /api/health` - Health check
- `GET /health` - Application health check

## 🎨 Caption Styling Options

| Option | Description | Default | Range |
|--------|-------------|---------|-------|
| `font_type` | Font family name | `Arial` | Any system font |
| `font_size` | Font size in pixels | `24` | 8-72 |
| `font_color` | Font color (hex) | `#FFFFFF` | Any hex color |
| `stroke_color` | Outline color (hex) | `#000000` | Any hex color |
| `stroke_width` | Outline width in pixels | `2` | 0-10 |
| `padding` | Padding around text | `10` | 0-50 |
| `position` | Caption position | `bottom` | `top`, `center`, `bottom` |

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Docker Build

```bash
# Build backend image
cd backend
docker build -t reely-backend .

# Build frontend image
cd frontend
docker build -t reely-frontend .
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Frontend Tests

```bash
cd frontend
npm test
```

### API Testing

```bash
cd backend
python test_api.py
```

## 📊 Performance

### Backend Optimizations
- Asynchronous processing with Celery
- Transcription result caching
- Efficient video processing with MoviePy
- Database indexing and query optimization

### Frontend Optimizations
- Code splitting and lazy loading
- API response caching
- Optimistic UI updates
- Responsive image loading

## 🔒 Security

### Authentication
- Firebase Authentication with Google Sign-In
- JWT token validation
- Protected API endpoints
- Secure token storage

### Data Protection
- Input validation and sanitization
- File type and size restrictions
- CORS configuration
- HTTPS enforcement in production

## 🚀 Deployment

### Production Checklist

1. **Backend**
   - Set up MongoDB cluster
   - Configure Redis cluster
   - Set up S3 bucket for file storage
   - Configure environment variables
   - Set up SSL certificates

2. **Frontend**
   - Configure Firebase project
   - Set up production environment variables
   - Build and deploy to hosting service
   - Configure domain and SSL

3. **Infrastructure**
   - Set up load balancer
   - Configure auto-scaling
   - Set up monitoring and logging
   - Configure backup strategies

### Hosting Recommendations

- **Backend**: AWS ECS, Google Cloud Run, or DigitalOcean App Platform
- **Frontend**: Vercel, Netlify, or Firebase Hosting
- **Database**: MongoDB Atlas
- **Storage**: AWS S3 or Google Cloud Storage
- **CDN**: CloudFront or CloudFlare

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow existing code style and conventions
- Add tests for new features
- Update documentation as needed
- Ensure responsive design
- Test on multiple devices and browsers

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for speech recognition
- [MoviePy](https://zulko.github.io/moviepy/) for video processing
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [React](https://reactjs.org/) for the frontend framework
- [Firebase](https://firebase.google.com/) for authentication
- [Tailwind CSS](https://tailwindcss.com/) for styling

## 📞 Support

For support and questions:

- Create an issue in the GitHub repository
- Check the documentation in the `backend/` and `frontend/` directories
- Review the API documentation at `/docs` when the backend is running

## 🔮 Future Enhancements

- **Real-time Processing**: WebSocket-based live updates
- **Batch Processing**: Multiple video processing
- **Custom Models**: User-specific Whisper model training
- **Multi-language Support**: Language detection and translation
- **Advanced Styling**: Shadow effects, animations, and transitions
- **Video Analytics**: Processing statistics and insights
- **API Versioning**: Backward compatibility and feature flags
- **Mobile App**: React Native or Flutter mobile application
#   R e e l y  
 