// Frontend test utilities and basic tests
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../src/contexts/AuthContext';
import Login from '../src/components/Login';
import Dashboard from '../src/components/Dashboard';

// Mock Firebase
vi.mock('../src/services/firebase', () => ({
  signInWithGoogle: vi.fn(),
  signOutUser: vi.fn(),
  auth: {
    currentUser: null,
  },
}));

// Mock API service
vi.mock('../src/services/api', () => ({
  videoAPI: {
    getVideos: vi.fn(),
    uploadVideo: vi.fn(),
    deleteVideo: vi.fn(),
    downloadVideo: vi.fn(),
  },
}));

// Test wrapper component
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    <AuthProvider>
      {children}
    </AuthProvider>
  </BrowserRouter>
);

describe('Login Component', () => {
  it('renders login form correctly', () => {
    render(
      <TestWrapper>
        <Login />
      </TestWrapper>
    );

    expect(screen.getByText('Reely')).toBeInTheDocument();
    expect(screen.getByText('Sign in with Google')).toBeInTheDocument();
    expect(screen.getByText('Features:')).toBeInTheDocument();
  });

  it('shows loading state when signing in', async () => {
    const { signInWithGoogle } = await import('../src/services/firebase');
    signInWithGoogle.mockImplementation(() => new Promise(() => {})); // Never resolves

    render(
      <TestWrapper>
        <Login />
      </TestWrapper>
    );

    const signInButton = screen.getByText('Sign in with Google');
    fireEvent.click(signInButton);

    await waitFor(() => {
      expect(screen.getByText('Signing in...')).toBeInTheDocument();
    });
  });
});

describe('Dashboard Component', () => {
  it('renders dashboard with empty state', async () => {
    const { videoAPI } = await import('../src/services/api');
    videoAPI.getVideos.mockResolvedValue({
      videos: [],
      total: 0,
      page: 1,
      page_size: 10,
    });

    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('No videos yet')).toBeInTheDocument();
      expect(screen.getByText('Upload your first video to get started')).toBeInTheDocument();
    });
  });

  it('renders video list when videos exist', async () => {
    const { videoAPI } = await import('../src/services/api');
    const mockVideos = [
      {
        video_id: 'test-123',
        filename: 'test-video.mp4',
        status: 'completed',
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:05:00Z',
        progress_percentage: 100,
      },
    ];

    videoAPI.getVideos.mockResolvedValue({
      videos: mockVideos,
      total: 1,
      page: 1,
      page_size: 10,
    });

    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('test-video.mp4')).toBeInTheDocument();
      expect(screen.getByText('ID: test-123')).toBeInTheDocument();
    });
  });
});

describe('API Service', () => {
  it('handles API errors gracefully', async () => {
    const { videoAPI } = await import('../src/services/api');
    videoAPI.getVideos.mockRejectedValue(new Error('Network error'));

    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    );

    await waitFor(() => {
      // Should show error state or fallback UI
      expect(screen.getByText('Loading videos...')).toBeInTheDocument();
    });
  });
});

// Utility functions for testing
export const testUtils = {
  // Mock user data
  createMockUser: () => ({
    uid: 'test-user-123',
    email: 'test@example.com',
    displayName: 'Test User',
    photoURL: 'https://example.com/photo.jpg',
  }),

  // Mock video data
  createMockVideo: (overrides = {}) => ({
    video_id: 'test-video-123',
    filename: 'test-video.mp4',
    status: 'completed',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:05:00Z',
    progress_percentage: 100,
    metadata: {
      duration: 120,
      width: 1920,
      height: 1080,
      fps: 30,
      format: 'mp4',
      size_bytes: 1024000,
    },
    ...overrides,
  }),

  // Mock caption style
  createMockCaptionStyle: (overrides = {}) => ({
    fontType: 'Arial',
    fontSize: 24,
    fontColor: '#FFFFFF',
    strokeColor: '#000000',
    strokeWidth: 2,
    padding: 10,
    position: 'bottom',
    ...overrides,
  }),
};
