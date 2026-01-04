#!/usr/bin/env python3
"""
Test script to verify face_recognition installation and basic functionality
"""

import sys
import os

def test_imports():
    """Test if all required libraries can be imported"""
    print("Testing imports...")
    
    try:
        import face_recognition
        print("✓ face_recognition imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import face_recognition: {e}")
        return False
    
    try:
        import cv2
        print("✓ opencv-python imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import cv2: {e}")
        return False
    
    try:
        import numpy as np
        print("✓ numpy imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import numpy: {e}")
        return False
    
    try:
        from PIL import Image
        print("✓ Pillow imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Pillow: {e}")
        return False
    
    try:
        import flask
        print("✓ Flask imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Flask: {e}")
        return False
    
    return True

def test_face_detection():
    """Test basic face detection functionality"""
    print("\nTesting face detection...")
    
    try:
        import face_recognition
        import numpy as np
        
        # Create a simple test image (dummy face)
        # This won't detect a face, but tests if the API works
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Try detection
        face_locations = face_recognition.face_locations(test_img, model='hog')
        print(f"✓ Face detection API works (found {len(face_locations)} faces in test image)")
        
        return True
    except Exception as e:
        print(f"✗ Face detection test failed: {e}")
        return False

def test_face_encoding():
    """Test face encoding functionality"""
    print("\nTesting face encoding...")
    
    try:
        import face_recognition
        import numpy as np
        
        # Create a dummy encoding
        test_encoding = np.random.rand(128)
        
        # Test encoding comparison
        test_encoding2 = np.random.rand(128)
        distance = face_recognition.face_distance([test_encoding], test_encoding2)
        
        print(f"✓ Face encoding API works (distance: {distance[0]:.2f})")
        return True
    except Exception as e:
        print(f"✗ Face encoding test failed: {e}")
        return False

def test_directories():
    """Test if database directories exist"""
    print("\nChecking database directories...")
    
    db_dirs = [
        'database',
        'database/faces',
        'database/images',
        'database/encodings'
    ]
    
    all_exist = True
    for dir_path in db_dirs:
        if os.path.exists(dir_path):
            print(f"✓ {dir_path} exists")
        else:
            print(f"✗ {dir_path} does not exist")
            all_exist = False
    
    return all_exist

def check_system_info():
    """Display system information"""
    print("\n" + "="*50)
    print("System Information")
    print("="*50)
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    try:
        import face_recognition
        print(f"face_recognition version: {face_recognition.__version__ if hasattr(face_recognition, '__version__') else 'unknown'}")
    except:
        pass
    
    try:
        import cv2
        print(f"OpenCV version: {cv2.__version__}")
    except:
        pass
    
    try:
        import numpy as np
        print(f"NumPy version: {np.__version__}")
    except:
        pass

def main():
    print("="*50)
    print("Face Recognition Backend - Installation Test")
    print("="*50)
    print()
    
    check_system_info()
    print()
    
    tests = [
        ("Import Test", test_imports),
        ("Face Detection Test", test_face_detection),
        ("Face Encoding Test", test_face_encoding),
        ("Directory Test", test_directories)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*50)
    print("Test Results Summary")
    print("="*50)
    
    all_passed = True
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All tests passed! Backend is ready to use.")
        print("\nTo start the backend, run:")
        print("  python app.py")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nTo fix issues:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
