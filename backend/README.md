# Reely Video Captioning API

A FastAPI-based backend service for automatic video captioning using OpenAI Whisper.

## Features

- **Video Upload**: Support for file uploads and public video URLs
- **Audio Transcription**: OpenAI Whisper integration for speech-to-text
- **Caption Rendering**: Customizable caption styling (font, color, size, position)
- **Asynchronous Processing**: Celery-based background task processing
- **Real-time Status**: Live processing status updates
- **File Management**: Local and cloud storage support
- **RESTful API**: Complete REST API with comprehensive endpoints

## Quick Start

### Prerequisites

- Python 3.9+
- FFmpeg (for video processing)
- MongoDB
- Redis
- OpenAI Whisper dependencies

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd reely/backend
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
   sudo apt update
   sudo apt install ffmpeg
   ```
   
   **macOS:**
   ```bash
   brew install ffmpeg
   ```
   
   **Windows:**
   - Download from https://ffmpeg.org/download.html
   - Add to PATH environment variable

5. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

6. **Start services**
   ```bash
   # Start MongoDB and Redis
   # MongoDB: mongod
   # Redis: redis-server
   
   # Start Celery worker
   celery -A app.tasks.worker worker --loglevel=info
   
   # Start FastAPI server
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

Once the server is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `DATABASE_NAME` | Database name | `reely_db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `UPLOAD_DIR` | Local upload directory | `./uploads` |
| `PROCESSED_DIR` | Processed files directory | `./processed` |
| `MAX_FILE_SIZE_MB` | Maximum file size in MB | `500` |
| `WHISPER_MODEL` | Whisper model to use | `base` |

## API Endpoints

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

## Usage Examples

### Upload Video File
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "video_file=@example.mp4" \
  -F "font_type=Arial" \
  -F "font_size=24" \
  -F "font_color=#FFFFFF" \
  -F "stroke_color=#000000" \
  -F "stroke_width=2" \
  -F "padding=10" \
  -F "position=bottom"
```

### Upload Video URL
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "video_url=https://example.com/video.mp4" \
  -F "font_type=Arial" \
  -F "font_size=24"
```

### Check Processing Status
```bash
curl "http://localhost:8000/api/video/{video_id}/status"
```

### Download Processed Video
```bash
curl "http://localhost:8000/api/video/{video_id}/download?type=processed" \
  --output captioned_video.mp4
```

## Caption Styling Options

| Option | Description | Default | Range |
|--------|-------------|---------|-------|
| `font_type` | Font family name | `Arial` | Any system font |
| `font_size` | Font size in pixels | `24` | 8-72 |
| `font_color` | Font color (hex) | `#FFFFFF` | Any hex color |
| `stroke_color` | Outline color (hex) | `#000000` | Any hex color |
| `stroke_width` | Outline width in pixels | `2` | 0-10 |
| `padding` | Padding around text | `10` | 0-50 |
| `position` | Caption position | `bottom` | `top`, `center`, `bottom` |

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black app/
isort app/
```

### Type Checking
```bash
mypy app/
```

## Production Deployment

### Docker Deployment
```bash
# Build image
docker build -t reely-api .

# Run with docker-compose
docker-compose up -d
```

### Environment Setup
1. Set up MongoDB cluster
2. Configure Redis cluster
3. Set up S3 bucket for file storage
4. Configure load balancer
5. Set up monitoring and logging

## Troubleshooting

### Common Issues

1. **FFmpeg not found**
   - Ensure FFmpeg is installed and in PATH
   - Check installation with `ffmpeg -version`

2. **Whisper model download issues**
   - Check internet connection
   - Verify model name is correct
   - Clear cache and retry

3. **MongoDB connection errors**
   - Verify MongoDB is running
   - Check connection string
   - Ensure database permissions

4. **Redis connection errors**
   - Verify Redis is running
   - Check connection string
   - Ensure Redis configuration

### Logs
- Application logs: Check console output
- Celery logs: Check worker output
- Database logs: Check MongoDB logs
- Redis logs: Check Redis logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
