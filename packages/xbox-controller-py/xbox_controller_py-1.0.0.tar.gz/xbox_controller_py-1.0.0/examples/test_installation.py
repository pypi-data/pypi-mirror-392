#!/usr/bin/env python3
"""
Test Installation Script

This script tests if the XboxControllerPy package is properly installed and working.
"""

import sys

def test_import():
    """Test if all modules can be imported"""
    print("Testing imports...")
    
    try:
        from xbox_controller import XboxController
        print("✅ XboxController import successful")
        
        from xbox_controller.utils import (
            format_axis_value, 
            get_controller_state, 
            get_button_name, 
            get_pressed_button_names
        )
        print("✅ Utils import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_controller_creation():
    """Test controller object creation"""
    print("\nTesting controller creation...")
    
    try:
        from xbox_controller import XboxController
        
        controller = XboxController()
        print("✅ Controller object created successfully")
        
        # Test basic properties
        print(f"   Connected: {controller.connected}")
        
        return True
        
    except Exception as e:
        print(f"❌ Controller creation error: {e}")
        return False

def test_controller_info():
    """Test controller info method"""
    print("\nTesting controller info...")
    
    try:
        from xbox_controller import XboxController
        
        controller = XboxController()
        info = controller.get_controller_info()
        
        print(f"✅ Controller info method works")
        print(f"   Info: {info}")
        
        return True
        
    except Exception as e:
        print(f"❌ Controller info error: {e}")
        return False

def test_connection():
    """Test actual controller connection"""
    print("\nTesting controller connection...")
    
    try:
        from xbox_controller import XboxController
        
        controller = XboxController()
        
        try:
            controller.connect()
            print("✅ Controller connected successfully")
            
            # Test getting state
            state = controller.get_state()
            print(f"   State keys: {list(state.keys())}")
            
            controller.disconnect()
            print("✅ Controller disconnected successfully")
            
            return True
            
        except SystemExit as e:
            print(f"⚠️  No controller detected: {e}")
            print("   This is normal if no Xbox controller is connected")
            return True  # This is expected behavior
            
    except Exception as e:
        print(f"❌ Connection test error: {e}")
        return False

def main():
    """Main test function"""
    print("🎮 XboxControllerPy Installation Test")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_import),
        ("Controller Creation", test_controller_creation),
        ("Controller Info", test_controller_info),
        ("Connection Test", test_connection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! XboxControllerPy is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())