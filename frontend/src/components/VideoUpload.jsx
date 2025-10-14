// Video upload form component with styling options
import React, { useState } from 'react';
import { videoAPI } from '../services/api';
import { 
  Upload, 
  Link, 
  X, 
  Loader2, 
  Palette, 
  Type, 
  AlignLeft,
  AlignCenter,
  AlignRight
} from 'lucide-react';
import toast from 'react-hot-toast';

const VideoUpload = ({ onClose, onSuccess }) => {
  const [uploadType, setUploadType] = useState('file'); // 'file' or 'url'
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [videoUrl, setVideoUrl] = useState('');
  
  // Caption styling options
  const [captionStyle, setCaptionStyle] = useState({
    fontType: 'Arial',
    fontSize: 24,
    fontColor: '#FFFFFF',
    strokeColor: '#000000',
    strokeWidth: 2,
    padding: 10,
    position: 'bottom'
  });

  // Font options
  const fontOptions = [
    'Arial', 'Helvetica', 'Times New Roman', 'Georgia', 'Verdana',
    'Courier New', 'Impact', 'Comic Sans MS', 'Trebuchet MS', 'Arial Black'
  ];

  // Position options
  const positionOptions = [
    { value: 'top', label: 'Top', icon: AlignLeft },
    { value: 'center', label: 'Center', icon: AlignCenter },
    { value: 'bottom', label: 'Bottom', icon: AlignRight }
  ];

  // Handle file selection
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      const validTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv', 'video/webm'];
      if (!validTypes.includes(file.type)) {
        toast.error('Please select a valid video file (MP4, AVI, MOV, MKV, WebM)');
        return;
      }
      
      // Validate file size (500MB limit)
      if (file.size > 500 * 1024 * 1024) {
        toast.error('File size must be less than 500MB');
        return;
      }
      
      setSelectedFile(file);
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (uploadType === 'file' && !selectedFile) {
      toast.error('Please select a video file');
      return;
    }
    
    if (uploadType === 'url' && !videoUrl.trim()) {
      toast.error('Please enter a video URL');
      return;
    }

    setLoading(true);

    try {
      let response;
      
      if (uploadType === 'file') {
        // Upload file
        const formData = new FormData();
        formData.append('video_file', selectedFile);
        formData.append('font_type', captionStyle.fontType);
        formData.append('font_size', captionStyle.fontSize.toString());
        formData.append('font_color', captionStyle.fontColor);
        formData.append('stroke_color', captionStyle.strokeColor);
        formData.append('stroke_width', captionStyle.strokeWidth.toString());
        formData.append('padding', captionStyle.padding.toString());
        formData.append('position', captionStyle.position);
        
        response = await videoAPI.uploadVideo(formData);
      } else {
        // Upload from URL
        response = await videoAPI.uploadVideoFromURL(videoUrl, captionStyle);
      }
      
      toast.success('Video uploaded successfully! Processing started.');
      onSuccess && onSuccess(response);
      
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to upload video. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Preview caption style
  const previewStyle = {
    fontFamily: captionStyle.fontType,
    fontSize: `${Math.min(captionStyle.fontSize, 16)}px`,
    color: captionStyle.fontColor,
    textShadow: `${captionStyle.strokeWidth}px ${captionStyle.strokeWidth}px 0 ${captionStyle.strokeColor}`,
    padding: `${captionStyle.padding}px`,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    borderRadius: '4px',
    display: 'inline-block',
    margin: '10px 0'
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Upload Video</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Upload Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Upload Method
            </label>
            <div className="flex space-x-4">
              <button
                type="button"
                onClick={() => setUploadType('file')}
                className={`flex items-center space-x-2 px-4 py-3 border rounded-lg transition-colors ${
                  uploadType === 'file'
                    ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                    : 'border-gray-300 hover:bg-gray-50'
                }`}
              >
                <Upload className="w-5 h-5" />
                <span>Upload File</span>
              </button>
              
              <button
                type="button"
                onClick={() => setUploadType('url')}
                className={`flex items-center space-x-2 px-4 py-3 border rounded-lg transition-colors ${
                  uploadType === 'url'
                    ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                    : 'border-gray-300 hover:bg-gray-50'
                }`}
              >
                <Link className="w-5 h-5" />
                <span>Video URL</span>
              </button>
            </div>
          </div>

          {/* File Upload */}
          {uploadType === 'file' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Video File
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
                <input
                  type="file"
                  accept="video/*"
                  onChange={handleFileChange}
                  className="hidden"
                  id="video-file"
                />
                <label
                  htmlFor="video-file"
                  className="cursor-pointer flex flex-col items-center space-y-2"
                >
                  <Upload className="w-8 h-8 text-gray-400" />
                  <span className="text-sm text-gray-600">
                    {selectedFile ? selectedFile.name : 'Click to select video file'}
                  </span>
                  <span className="text-xs text-gray-500">
                    MP4, AVI, MOV, MKV, WebM (max 500MB)
                  </span>
                </label>
              </div>
            </div>
          )}

          {/* URL Input */}
          {uploadType === 'url' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Video URL
              </label>
              <input
                type="url"
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                placeholder="https://example.com/video.mp4"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                Enter a public video URL (MP4, AVI, MOV, MKV, WebM)
              </p>
            </div>
          )}

          {/* Caption Styling */}
          <div className="border-t border-gray-200 pt-6">
            <div className="flex items-center space-x-2 mb-4">
              <Palette className="w-5 h-5 text-gray-600" />
              <h3 className="text-lg font-medium text-gray-900">Caption Styling</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Font Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Font Type
                </label>
                <select
                  value={captionStyle.fontType}
                  onChange={(e) => setCaptionStyle({...captionStyle, fontType: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  {fontOptions.map(font => (
                    <option key={font} value={font}>{font}</option>
                  ))}
                </select>
              </div>

              {/* Font Size */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Font Size: {captionStyle.fontSize}px
                </label>
                <input
                  type="range"
                  min="8"
                  max="72"
                  value={captionStyle.fontSize}
                  onChange={(e) => setCaptionStyle({...captionStyle, fontSize: parseInt(e.target.value)})}
                  className="w-full"
                />
              </div>

              {/* Font Color */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Font Color
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="color"
                    value={captionStyle.fontColor}
                    onChange={(e) => setCaptionStyle({...captionStyle, fontColor: e.target.value})}
                    className="w-10 h-10 border border-gray-300 rounded"
                  />
                  <input
                    type="text"
                    value={captionStyle.fontColor}
                    onChange={(e) => setCaptionStyle({...captionStyle, fontColor: e.target.value})}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
              </div>

              {/* Stroke Color */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Stroke Color
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="color"
                    value={captionStyle.strokeColor}
                    onChange={(e) => setCaptionStyle({...captionStyle, strokeColor: e.target.value})}
                    className="w-10 h-10 border border-gray-300 rounded"
                  />
                  <input
                    type="text"
                    value={captionStyle.strokeColor}
                    onChange={(e) => setCaptionStyle({...captionStyle, strokeColor: e.target.value})}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
              </div>

              {/* Stroke Width */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Stroke Width: {captionStyle.strokeWidth}px
                </label>
                <input
                  type="range"
                  min="0"
                  max="10"
                  value={captionStyle.strokeWidth}
                  onChange={(e) => setCaptionStyle({...captionStyle, strokeWidth: parseInt(e.target.value)})}
                  className="w-full"
                />
              </div>

              {/* Padding */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Padding: {captionStyle.padding}px
                </label>
                <input
                  type="range"
                  min="0"
                  max="50"
                  value={captionStyle.padding}
                  onChange={(e) => setCaptionStyle({...captionStyle, padding: parseInt(e.target.value)})}
                  className="w-full"
                />
              </div>

              {/* Position */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Position
                </label>
                <div className="flex space-x-4">
                  {positionOptions.map(option => {
                    const Icon = option.icon;
                    return (
                      <button
                        key={option.value}
                        type="button"
                        onClick={() => setCaptionStyle({...captionStyle, position: option.value})}
                        className={`flex items-center space-x-2 px-4 py-2 border rounded-lg transition-colors ${
                          captionStyle.position === option.value
                            ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                            : 'border-gray-300 hover:bg-gray-50'
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                        <span>{option.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Preview */}
            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Preview
              </label>
              <div className="bg-gray-800 p-4 rounded-lg text-center">
                <span style={previewStyle}>
                  Sample Caption Text
                </span>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
            
            <button
              type="submit"
              disabled={loading}
              className="flex items-center space-x-2 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Upload className="w-4 h-4" />
              )}
              <span>{loading ? 'Uploading...' : 'Upload Video'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default VideoUpload;
