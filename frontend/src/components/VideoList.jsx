// VideoList component for displaying videos in a list format
import React from 'react';
import { 
  Play, 
  Download, 
  Trash2, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Loader2 
} from 'lucide-react';

const VideoList = ({ videos, onDelete, onDownload, loading = false }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
        <span className="ml-2 text-gray-600">Loading videos...</span>
      </div>
    );
  }

  if (!videos || videos.length === 0) {
    return (
      <div className="text-center p-8">
        <Play className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No videos found</h3>
        <p className="text-gray-600">
          Upload your first video to get started with automatic captioning
        </p>
      </div>
    );
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'processing':
        return <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-600" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-600" />;
      default:
        return <Clock className="w-5 h-5 text-gray-600" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'Unknown';
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="space-y-4">
      {videos.map((video) => (
        <div
          key={video.video_id}
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-3 mb-2">
                {getStatusIcon(video.status)}
                <div>
                  <h3 className="text-lg font-medium text-gray-900 truncate">
                    {video.filename}
                  </h3>
                  <p className="text-sm text-gray-500">
                    ID: {video.video_id}
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
                <span>Created: {formatDate(video.created_at)}</span>
                {video.updated_at && (
                  <span>Updated: {formatDate(video.updated_at)}</span>
                )}
                {video.metadata && (
                  <>
                    <span>Duration: {Math.round(video.metadata.duration)}s</span>
                    <span>Size: {formatFileSize(video.metadata.size_bytes)}</span>
                  </>
                )}
              </div>

              <div className="flex items-center space-x-2 mb-3">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(video.status)}`}>
                  {video.status.charAt(0).toUpperCase() + video.status.slice(1)}
                </span>
                {video.progress_percentage > 0 && video.status === 'processing' && (
                  <span className="text-sm text-gray-600">
                    {video.progress_percentage}% complete
                  </span>
                )}
              </div>

              {video.status === 'processing' && video.progress_percentage > 0 && (
                <div className="mb-3">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${video.progress_percentage}%` }}
                    />
                  </div>
                </div>
              )}

              {video.error_message && (
                <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-sm text-red-700">
                    <strong>Error:</strong> {video.error_message}
                  </p>
                </div>
              )}

              {video.transcription && video.transcription.length > 0 && (
                <div className="mt-3">
                  <p className="text-sm text-gray-600 mb-1">
                    <strong>Transcription preview:</strong>
                  </p>
                  <p className="text-sm text-gray-800 bg-gray-50 p-2 rounded">
                    {video.transcription[0]?.text || 'No preview available'}
                    {video.transcription.length > 1 && '...'}
                  </p>
                </div>
              )}
            </div>

            <div className="flex items-center space-x-2 ml-4">
              {video.status === 'completed' && (
                <button
                  onClick={() => onDownload(video.video_id, video.filename)}
                  className="flex items-center space-x-1 px-3 py-2 text-sm text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 rounded-lg transition-colors"
                  title="Download captioned video"
                >
                  <Download className="w-4 h-4" />
                  <span>Download</span>
                </button>
              )}

              <button
                onClick={() => onDelete(video.video_id)}
                className="flex items-center space-x-1 px-3 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                title="Delete video"
              >
                <Trash2 className="w-4 h-4" />
                <span>Delete</span>
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default VideoList;
