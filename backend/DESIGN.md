# Reely Video Captioning API - Design Document

## Architecture Overview

The Reely Video Captioning API is a FastAPI-based backend service that provides automatic video captioning capabilities. The system processes video files by extracting audio, transcribing it using OpenAI Whisper, and overlaying customizable captions onto the video.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Celery        │
│   (React/Vue)   │◄──►│   Application   │◄──►│   Workers       │
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
                       │   File Storage   │
                       │   (Local/S3)     │
                       └─────────────────┘
```

## Core Components

### 1. FastAPI Application (`app/main.py`)
- **Purpose**: Main web application server
- **Features**:
  - RESTful API endpoints
  - CORS middleware for frontend integration
  - Global exception handling
  - Health check endpoints

### 2. API Routes (`app/api/routes.py`)
- **Video Upload**: Accept file uploads or video URLs
- **Caption Processing**: Initiate caption generation
- **Video Management**: List, retrieve, and delete videos
- **Status Tracking**: Real-time processing status
- **File Download**: Download original or processed videos

### 3. Services Layer

#### Storage Service (`app/services/storage.py`)
- **File Management**: Local file storage with S3 support
- **URL Download**: Download videos from public URLs
- **File Operations**: Hash calculation, size validation, cleanup
- **Cloud Integration**: AWS S3 upload/download capabilities

#### Transcription Service (`app/services/transcription.py`)
- **Whisper Integration**: OpenAI Whisper model for speech-to-text
- **Caching**: Transcription result caching to avoid reprocessing
- **Async Processing**: Non-blocking transcription operations
- **Model Management**: Dynamic model switching and configuration

#### Caption Renderer (`app/services/caption_renderer.py`)
- **Text Rendering**: PIL-based caption image generation
- **Style Customization**: Font, color, size, position options
- **Word Highlighting**: Optional word-level highlighting
- **Font Management**: System font detection and caching

#### Video Processor (`app/services/video_processor.py`)
- **Audio Extraction**: Extract audio from video files
- **Caption Overlay**: Composite captions onto video
- **Metadata Extraction**: Video properties and statistics
- **Format Support**: Multiple video format handling

### 4. Asynchronous Processing (`app/tasks/worker.py`)
- **Celery Integration**: Distributed task processing
- **Task Types**:
  - Full video processing pipeline
  - Audio-only transcription
  - Caption-only generation
  - File cleanup operations
- **Progress Tracking**: Real-time task status updates
- **Error Handling**: Comprehensive error management

### 5. Data Models (`app/models/`)
- **Pydantic Schemas**: API request/response models
- **MongoDB Documents**: Database document models
- **Validation**: Input validation and type safety

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

## Data Flow

### 1. Video Upload Process
```
1. Client uploads video file or provides URL
2. FastAPI validates input and generates unique video ID
3. File is saved to local storage or downloaded from URL
4. Video document is created in MongoDB
5. Celery task is queued for processing
6. API returns immediate response with video ID
```

### 2. Processing Pipeline
```
1. Celery worker picks up processing task
2. Audio is extracted from video file
3. Audio is transcribed using Whisper
4. Caption images are generated with custom styling
5. Captions are overlaid onto video
6. Processed video is saved
7. Database is updated with results
8. Client can poll for status updates
```

### 3. Status Tracking
```
1. Client polls status endpoint
2. API checks Celery task status
3. Database document is updated with progress
4. Real-time status is returned to client
```

## Scalability Considerations

### Horizontal Scaling

#### 1. Application Layer
- **Load Balancer**: Deploy multiple FastAPI instances behind a load balancer
- **Stateless Design**: No server-side session storage
- **Container Orchestration**: Use Docker with Kubernetes for auto-scaling

#### 2. Worker Layer
- **Multiple Celery Workers**: Scale workers based on processing demand
- **Worker Specialization**: Dedicated workers for different task types
- **Auto-scaling**: Dynamic worker scaling based on queue length

#### 3. Database Layer
- **MongoDB Sharding**: Distribute data across multiple shards
- **Read Replicas**: Separate read and write operations
- **Connection Pooling**: Optimize database connections

#### 4. Storage Layer
- **S3 Integration**: Move to cloud storage for better scalability
- **CDN**: Use CloudFront or similar for video delivery
- **Storage Tiers**: Implement lifecycle policies for cost optimization

### Performance Optimizations

#### 1. Caching Strategy
- **Transcription Cache**: Avoid reprocessing identical audio
- **Redis Caching**: Cache frequently accessed data
- **CDN Caching**: Cache static assets and processed videos

#### 2. Processing Optimization
- **GPU Acceleration**: Use GPU-enabled Whisper models
- **Batch Processing**: Process multiple videos in batches
- **Parallel Processing**: Concurrent audio extraction and transcription

#### 3. Database Optimization
- **Indexing**: Proper indexes on frequently queried fields
- **Aggregation Pipelines**: Optimize complex queries
- **Connection Pooling**: Efficient connection management

### Monitoring and Observability

#### 1. Metrics Collection
- **Application Metrics**: Request rates, response times, error rates
- **Processing Metrics**: Task completion times, queue lengths
- **Resource Metrics**: CPU, memory, disk usage

#### 2. Logging
- **Structured Logging**: JSON-formatted logs for easy parsing
- **Log Aggregation**: Centralized logging with ELK stack
- **Error Tracking**: Detailed error logging and alerting

#### 3. Health Checks
- **Application Health**: API endpoint availability
- **Dependency Health**: Database, Redis, storage connectivity
- **Processing Health**: Worker availability and performance

## Security Considerations

### 1. Input Validation
- **File Type Validation**: Strict video format checking
- **File Size Limits**: Prevent large file uploads
- **URL Validation**: Validate external video URLs

### 2. Authentication & Authorization
- **API Keys**: Implement API key authentication
- **Rate Limiting**: Prevent abuse and DoS attacks
- **User Isolation**: Separate user data and processing

### 3. Data Protection
- **Encryption**: Encrypt sensitive data at rest
- **Secure Transmission**: HTTPS for all communications
- **Access Control**: Proper file access permissions

## Deployment Architecture

### Development Environment
```
┌─────────────────┐
│   Local Machine │
│   - FastAPI     │
│   - MongoDB     │
│   - Redis       │
│   - Celery      │
└─────────────────┘
```

### Production Environment
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   App Servers   │    │   Worker Nodes  │
│   (nginx/ALB)   │◄──►│   (FastAPI)     │    │   (Celery)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   MongoDB       │    │   Redis         │
                       │   Cluster       │    │   Cluster       │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   S3 Storage     │
                       │   + CloudFront   │
                       └─────────────────┘
```

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Celery**: Distributed task queue
- **Redis**: Message broker and caching
- **MongoDB**: Document database
- **OpenAI Whisper**: Speech-to-text model
- **MoviePy**: Video processing library
- **PIL/Pillow**: Image processing

### Infrastructure
- **Docker**: Containerization
- **Kubernetes**: Container orchestration
- **AWS S3**: Object storage
- **CloudFront**: CDN
- **MongoDB Atlas**: Managed database
- **Redis Cloud**: Managed Redis

## Future Enhancements

### 1. Advanced Features
- **Real-time Processing**: WebSocket-based live updates
- **Batch Processing**: Multiple video processing
- **Custom Models**: User-specific Whisper model training
- **Multi-language Support**: Language detection and translation

### 2. Performance Improvements
- **Edge Processing**: Process videos closer to users
- **Streaming**: Real-time video streaming with captions
- **Compression**: Advanced video compression techniques
- **Caching**: Intelligent caching strategies

### 3. Integration Features
- **Webhook Support**: Notify external systems of completion
- **API Versioning**: Backward compatibility
- **SDK Development**: Client libraries for popular languages
- **Analytics**: Usage analytics and reporting

## Conclusion

The Reely Video Captioning API is designed with scalability, performance, and maintainability in mind. The modular architecture allows for easy scaling of individual components, while the asynchronous processing model ensures responsive user experience. The system can handle both small-scale deployments and large-scale production environments with appropriate infrastructure scaling.
