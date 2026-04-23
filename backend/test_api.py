"""
API Test Script
Test the disease detection API with sample images
"""
import requests
import os
import json
from datetime import datetime

# API configuration
API_URL = 'http://localhost:5000'

def test_health_check():
    """Test the health check endpoint"""
    print("\n" + "=" * 50)
    print("TEST 1: Health Check")
    print("=" * 50)
    
    try:
        response = requests.get(f'{API_URL}/health')
        result = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if result.get('status') == 'healthy':
            print("✓ PASS: API is healthy")
            return True
        else:
            print("✗ FAIL: API is not healthy")
            return False
    
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def test_analyze_leaf(image_path):
    """Test the analyze-leaf endpoint"""
    print("\n" + "=" * 50)
    print("TEST 2: Analyze Leaf Image")
    print("=" * 50)
    
    if not os.path.exists(image_path):
        print(f"✗ FAIL: Image not found: {image_path}")
        return False
    
    try:
        print(f"Uploading image: {image_path}")
        
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(f'{API_URL}/analyze-leaf', files=files)
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("\n✓ PASS: Analysis successful")
            print(f"  Crop:      {result['crop']}")
            print(f"  Disease:   {result['disease']}")
            print(f"  Severity:  {result['severity']}%")
            print(f"  Confidence: {result['confidence']:.2%}")
            return True
        else:
            print(f"✗ FAIL: {result.get('error', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def test_history():
    """Test the history endpoint"""
    print("\n" + "=" * 50)
    print("TEST 3: Get Analysis History")
    print("=" * 50)
    
    try:
        response = requests.get(f'{API_URL}/history?limit=5')
        result = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Record Count: {result.get('count', 0)}")
        
        if result.get('success'):
            print("✓ PASS: History retrieved")
            if result.get('history'):
                print("\nRecent Records:")
                for record in result['history'][:3]:
                    print(f"  - {record['crop']} | {record['disease']} | {record['severity']}% | {record['timestamp']}")
            return True
        else:
            print(f"✗ FAIL: {result.get('error', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def test_statistics():
    """Test the statistics endpoint"""
    print("\n" + "=" * 50)
    print("TEST 4: Get Statistics")
    print("=" * 50)
    
    try:
        response = requests.get(f'{API_URL}/stats')
        result = response.json()
        
        print(f"Status Code: {response.status_code}")
        
        if result.get('success'):
            stats = result['statistics']
            print("✓ PASS: Statistics retrieved")
            print(f"\n  Total Analyses:  {stats['total_analyses']}")
            print(f"  Healthy Count:   {stats['healthy_count']}")
            print(f"  Diseased Count:  {stats['diseased_count']}")
            print(f"  Avg Severity:    {stats['average_severity']}%")
            return True
        else:
            print(f"✗ FAIL: {result.get('error', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def run_all_tests(test_image=None):
    """Run all API tests"""
    print("\n" + "=" * 70)
    print("BIOLOGICAL SPRINKLER - API TEST SUITE")
    print("=" * 70)
    print(f"API URL: {API_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    results = []
    
    # Test 1: Health Check
    results.append(test_health_check())
    
    # Test 2: Analyze Image (if provided)
    if test_image:
        results.append(test_analyze_leaf(test_image))
    else:
        print("\n⚠ Skipping image analysis test (no test image provided)")
    
    # Test 3: History
    results.append(test_history())
    
    # Test 4: Statistics
    results.append(test_statistics())
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ ALL TESTS PASSED")
    else:
        print(f"✗ {total - passed} TEST(S) FAILED")
    
    print("=" * 70)

if __name__ == '__main__':
    import sys
    
    # Check if test image is provided
    test_image = sys.argv[1] if len(sys.argv) > 1 else None
    
    if test_image and not os.path.exists(test_image):
        print(f"Error: Test image not found: {test_image}")
        print("\nUsage:")
        print("  python test_api.py                    # Run tests without image")
        print("  python test_api.py path/to/image.jpg  # Run tests with image")
        sys.exit(1)
    
    # Run tests
    run_all_tests(test_image)
