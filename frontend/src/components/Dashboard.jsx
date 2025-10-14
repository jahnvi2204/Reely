// Dashboard component showing video list and status
import React, { useState, useEffect } from 'react';
import { videoAPI } from '../services/api';
import { 
  Play, 
  Download, 
  Trash2, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Loader2,
  RefreshCw,
  Plus
} from 'lucide-react';
import toast from 'react-hot-toast';
import VideoUpload from './VideoUpload';

const Dashboard = () => {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 10,
    total: 0
  });

  // Fetch videos from API
  const fetchVideos = async (page = 1) => {
    try {
      const response = await videoAPI.getVideos(page, pagination.pageSize);
      setVideos(response.videos);
      setPagination({
        page: response.page,
        pageSize: response.page_size,
        total: response.total
      });
    } catch (error) {
      console.error('Error fetching videos:', error);
      toast.error('Failed to load videos');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchVideos();
  }, []);

  // Auto-refresh for processing videos
  useEffect(() => {
    const hasProcessingVideos = videos.some(video => 
      video.status === 'processing' || video.status === 'pending'
    );

    if (hasProcessingVideos) {
      const interval = setInterval(() => {
        fetchVideos(pagination.page);
      }, 5000); // Refresh every 5 seconds

      return () => clearInterval(interval);
    }
  }, [videos, pagination.page]);

  // Handle refresh
  const handleRefresh = () => {
    setRefreshing(true);
    fetchVideos(pagination.page);
  };

  // Handle video deletion
  const handleDeleteVideo = async (videoId) => {
    if (!confirm('Are you sure you want to delete this video?')) {
      return;
    }

    try {
      await videoAPI.deleteVideo(videoId);
      toast.success('Video deleted successfully');
      fetchVideos(pagination.page);
    } catch (error) {
      console.error('Error deleting video:', error);
      toast.error('Failed to delete video');
    }
  };

  // Handle video download
  const handleDownloadVideo = async (videoId, filename) => {
    try {
      const blob = await videoAPI.downloadVideo(videoId, 'processed');
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename || `captioned_video_${videoId}.mp4`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('Video downloaded successfully');
    } catch (error) {
      console.error('Error downloading video:', error);
      toast.error('Failed to download video');
    }
  };

  // Get status icon and color
  const getStatusInfo = (status) => {
    switch (status) {
      case 'completed':
        return { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-100' };
      case 'processing':
        return { icon: Loader2, color: 'text-blue-600', bg: 'bg-blue-100' };
      case 'pending':
        return { icon: Clock, color: 'text-yellow-600', bg: 'bg-yellow-100' };
      case 'failed':
        return { icon: XCircle, color: 'text-red-600', bg: 'bg-red-100' };
      default:
        return { icon: Clock, color: 'text-gray-600', bg: 'bg-gray-100' };
    }
  };

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (showUploadForm) {
    return (
      <VideoUpload 
        onClose={() => setShowUploadForm(false)}
        onSuccess={() => {
          setShowUploadForm(false);
          fetchVideos();
        }}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 mt-1">
              Manage your video captioning projects
            </p>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center space-x-2 px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
            
            <button
              onClick={() => setShowUploadForm(true)}
              className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              <Plus className="w-4 h-4" />
              <span>New Video</span>
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Play className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Videos</p>
                <p className="text-2xl font-bold text-gray-900">{pagination.total}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Completed</p>
                <p className="text-2xl font-bold text-gray-900">
                  {videos.filter(v => v.status === 'completed').length}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Loader2 className="w-6 h-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Processing</p>
                <p className="text-2xl font-bold text-gray-900">
                  {videos.filter(v => v.status === 'processing' || v.status === 'pending').length}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 rounded-lg">
                <XCircle className="w-6 h-6 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Failed</p>
                <p className="text-2xl font-bold text-gray-900">
                  {videos.filter(v => v.status === 'failed').length}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Video List */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Your Videos</h2>
          </div>
          
          {loading ? (
            <div className="p-8 text-center">
              <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-indigo-600" />
              <p className="text-gray-600">Loading videos...</p>
            </div>
          ) : videos.length === 0 ? (
            <div className="p-8 text-center">
              <Play className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No videos yet</h3>
              <p className="text-gray-600 mb-4">
                Upload your first video to get started with automatic captioning
              </p>
              <button
                onClick={() => setShowUploadForm(true)}
                className="inline-flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                <Plus className="w-4 h-4" />
                <span>Upload Video</span>
              </button>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {videos.map((video) => {
                const statusInfo = getStatusInfo(video.status);
                const StatusIcon = statusInfo.icon;
                
                return (
                  <div key={video.video_id} className="p-6 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-3 mb-2">
                          <div className={`p-2 rounded-lg ${statusInfo.bg}`}>
                            <StatusIcon className={`w-5 h-5 ${statusInfo.color} ${video.status === 'processing' ? 'animate-spin' : ''}`} />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-gray-900 truncate">
                              {video.filename}
                            </h3>
                            <p className="text-sm text-gray-500">
                              ID: {video.video_id}
                            </p>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-6 text-sm text-gray-500">
                          <span>Created: {formatDate(video.created_at)}</span>
                          {video.updated_at && (
                            <span>Updated: {formatDate(video.updated_at)}</span>
                          )}
                          {video.metadata && (
                            <span>Duration: {Math.round(video.metadata.duration)}s</span>
                          )}
                        </div>
                        
                        {video.status === 'processing' && video.progress_percentage > 0 && (
                          <div className="mt-3">
                            <div className="flex justify-between text-sm text-gray-600 mb-1">
                              <span>Processing...</span>
                              <span>{video.progress_percentage}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                                style={{ width: `${video.progress_percentage}%` }}
                              />
                            </div>
                          </div>
                        )}
                        
                        {video.error_message && (
                          <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                            Error: {video.error_message}
                          </div>
                        )}
                      </div>
                      
                      <div className="flex items-center space-x-2 ml-4">
                        {video.status === 'completed' && (
                          <button
                            onClick={() => handleDownloadVideo(video.video_id, video.filename)}
                            className="flex items-center space-x-1 px-3 py-2 text-sm text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 rounded-lg transition-colors"
                          >
                            <Download className="w-4 h-4" />
                            <span>Download</span>
                          </button>
                        )}
                        
                        <button
                          onClick={() => handleDeleteVideo(video.video_id)}
                          className="flex items-center space-x-1 px-3 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                          <span>Delete</span>
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
