"""
Simple test script for the Reely API
"""
import requests
import time
import json

API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_api_health():
    """Test API health endpoint"""
    print("🔍 Testing API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ API health check passed")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check error: {e}")
        return False

def test_video_list():
    """Test video list endpoint"""
    print("🔍 Testing video list...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/videos")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Video list retrieved: {data['total']} videos")
            return True
        else:
            print(f"❌ Video list failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Video list error: {e}")
        return False

def test_video_upload_url():
    """Test video upload with URL"""
    print("🔍 Testing video upload with URL...")
    try:
        # Use a sample video URL (you can replace this with a real video URL)
        test_url = "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4"
        
        data = {
            "video_url": test_url,
            "font_type": "Arial",
            "font_size": 24,
            "font_color": "#FFFFFF",
            "stroke_color": "#000000",
            "stroke_width": 2,
            "padding": 10,
            "position": "bottom"
        }
        
        response = requests.post(f"{API_BASE_URL}/api/upload", data=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Video upload initiated: {result['video_id']}")
            return result['video_id']
        else:
            print(f"❌ Video upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Video upload error: {e}")
        return None

def test_video_status(video_id):
    """Test video status endpoint"""
    print(f"🔍 Testing video status for {video_id}...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/video/{video_id}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Video status: {data['status']} ({data['progress_percentage']}%)")
            return data
        else:
            print(f"❌ Video status failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Video status error: {e}")
        return None

def test_video_details(video_id):
    """Test video details endpoint"""
    print(f"🔍 Testing video details for {video_id}...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/video/{video_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Video details retrieved: {data['filename']}")
            return data
        else:
            print(f"❌ Video details failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Video details error: {e}")
        return None

def main():
    """Run all tests"""
    print("🧪 Starting Reely API Tests...")
    print("=" * 50)
    
    # Test basic connectivity
    if not test_health_check():
        print("❌ Basic health check failed. Is the server running?")
        return
    
    if not test_api_health():
        print("❌ API health check failed. Check database connections.")
        return
    
    # Test video list
    test_video_list()
    
    # Test video upload
    video_id = test_video_upload_url()
    if video_id:
        # Test video details
        test_video_details(video_id)
        
        # Test status (poll a few times)
        print("\n⏳ Polling video status...")
        for i in range(5):
            status = test_video_status(video_id)
            if status and status['status'] in ['completed', 'failed']:
                break
            time.sleep(2)
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed!")
    print("\n📚 API Documentation:")
    print(f"   - Interactive docs: {API_BASE_URL}/docs")
    print(f"   - ReDoc: {API_BASE_URL}/redoc")

if __name__ == "__main__":
    main()
