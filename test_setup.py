#!/usr/bin/env python3
"""
Test script to verify SignPop dependencies and setup
"""

def test_imports():
    """Test if all required packages can be imported"""
    try:
        print("Testing core dependencies...")
        
        # Test computer vision libraries
        import cv2
        print("✅ OpenCV imported successfully")
        
        import numpy as np
        print("✅ NumPy imported successfully")
        
        # Test machine learning libraries
        import tensorflow as tf
        print(f"✅ TensorFlow {tf.__version__} imported successfully")
        
        # Test MediaPipe
        import mediapipe
        print("✅ MediaPipe imported successfully")
        
        # Test CVZone
        import cvzone
        print("✅ CVZone imported successfully")
        
        # Test other dependencies
        import matplotlib
        print("✅ Matplotlib imported successfully")
        
        import requests
        print("✅ Requests imported successfully")
        
        print("\n🎉 All dependencies imported successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_model_files():
    """Test if model files exist"""
    import os
    
    print("\nTesting model files...")
    
    model_path = "Model/keras_model.h5"
    labels_path = "Model/labels.txt"
    
    if os.path.exists(model_path):
        print(f"✅ Model file found: {model_path}")
    else:
        print(f"❌ Model file missing: {model_path}")
        return False
    
    if os.path.exists(labels_path):
        print(f"✅ Labels file found: {labels_path}")
    else:
        print(f"❌ Labels file missing: {labels_path}")
        return False
    
    return True

def test_hand_detector():
    """Test if hand detector can be initialized"""
    try:
        print("\nTesting hand detector...")
        from hand_detector import HandSignDetector
        
        detector = HandSignDetector('Model/keras_model.h5', 'Model/labels.txt')
        print("✅ Hand detector initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Hand detector error: {e}")
        return False

if __name__ == "__main__":
    print("SignPop Dependency Test")
    print("=" * 30)
    
    all_tests_passed = True
    
    # Run tests
    all_tests_passed &= test_imports()
    all_tests_passed &= test_model_files()
    all_tests_passed &= test_hand_detector()
    
    print("\n" + "=" * 30)
    if all_tests_passed:
        print("🎉 All tests passed! SignPop is ready to run.")
        print("\nTo run the Streamlit app:")
        print("streamlit run streamlit_app.py")
    else:
        print("❌ Some tests failed. Please check the requirements and model files.")
