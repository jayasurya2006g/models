import requests
import numpy as np
import cv2
import json
from io import BytesIO

# Deployed API endpoint
API_URL = "https://models-3m2h.onrender.com/anpr/image"

def test_with_sample_image():
    """Test the deployed API with a sample image"""
    print("=" * 60)
    print("Testing Deployed ANPR Model at:", API_URL)
    print("=" * 60)
    
    # Create a simple test image (100x100 blue image)
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    test_image[:, :] = [255, 0, 0]  # Blue image
    
    # Encode image to bytes
    is_success, buffer = cv2.imencode(".jpg", test_image)
    image_bytes = BytesIO(buffer)
    
    # Prepare multipart form data
    files = {
        'file': ('test.jpg', image_bytes, 'image/jpeg')
    }
    data = {
        'timestamp': 1234567890.0,
        'camera_id': 'test-camera-1',
        'lat': 40.7128,
        'lng': -74.0060
    }
    
    try:
        print("\nSending request to API...")
        print(f"File: test.jpg (100x100 sample image)")
        print(f"Metadata: camera_id={data['camera_id']}, lat={data['lat']}, lng={data['lng']}")
        
        response = requests.post(API_URL, files=files, data=data, timeout=30)
        
        print(f"\nResponse Status Code: {response.status_code}")
        print("\n--- Response Body ---")
        
        if response.status_code == 200:
            result = response.json()
            print(json.dumps(result, indent=2))
            
            if result.get('success'):
                print("\n✓ API is working!")
                vehicles = result.get('vehicles', [])
                print(f"Vehicles detected: {len(vehicles)}")
                for i, vehicle in enumerate(vehicles, 1):
                    print(f"\n  Vehicle {i}:")
                    print(f"    - Model: {vehicle.get('vehicle_model', 'N/A')}")
                    print(f"    - Plate: {vehicle.get('plate_number', 'Not detected')}")
            else:
                print("\n⚠ API returned false for success")
        else:
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out. The API might be cold-starting (Render free tier).")
        print("   Try again in a few seconds...")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print("   Check if the API is deployed and running.")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_with_sample_image()
