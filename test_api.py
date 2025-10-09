#!/usr/bin/env python3
"""
Test script for PDF417 Driver License Generator API
Tests ANSI compliance, state-specific generation, and error handling
"""

import requests
import json
import base64
from datetime import datetime, timedelta
from PIL import Image
import io

# Test configuration
API_BASE_URL = "https://dl-pdf417-app.vercel.app"  # Update with your deployed URL
LOCAL_URL = "http://localhost:8000"  # For local testing

# Use deployed URL by default, fallback to local
BASE_URL = API_BASE_URL

def test_api_health():
    """Test if the API is responding"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ API Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ API Health Check Failed: {e}")
        return False

def test_validation_endpoints():
    """Test validation info endpoints"""
    try:
        # Test states endpoint
        response = requests.get(f"{BASE_URL}/states")
        states_data = response.json()
        print(f"✅ States Endpoint: {response.status_code}")
        print(f"   States: {len(states_data.get('supported_states', []))} supported")
        
        # Test validation endpoint
        response = requests.get(f"{BASE_URL}/validation")
        validation_data = response.json()
        print(f"✅ Validation Endpoint: {response.status_code}")
        print(f"   Eye Colors: {len(validation_data.get('eye_colors', []))}")
        return True
    except Exception as e:
        print(f"❌ Validation Endpoints Failed: {e}")
        return False

def create_test_license_data(state="TN"):
    """Create valid test driver license data"""
    today = datetime.now()
    birth_date = today - timedelta(days=365*25)  # 25 years ago
    issue_date = today - timedelta(days=30)  # Issued 30 days ago
    expiry_date = today + timedelta(days=365*5)  # Expires in 5 years
    
    return {
        "dl_number": "091076664",
        "first_name": "JOHN",
        "last_name": "DOE",
        "middle_name": "DAVID",
        "address": "123 MAIN ST",
        "city": "NASHVILLE",
        "state": state,
        "zip_code": "37203",
        "sex": "M",
        "donor": "Y",
        "height_inches": "72",
        "weight_lbs": "180",
        "birth_date": birth_date.strftime("%m%d%Y"),
        "issue_date": issue_date.strftime("%m%d%Y"),
        "expiry_date": expiry_date.strftime("%m%d%Y"),
        "eye_color": "BRO",
        "hair_color": "BRO",
        "dl_class": "D",
        "restrictions": "",
        "endorsements": "",
        "is_real_id": "Y"
    }

def test_pdf417_generation():
    """Test PDF417 barcode generation with valid data"""
    try:
        test_data = create_test_license_data()
        response = requests.post(f"{BASE_URL}/generate", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ PDF417 Generation: SUCCESS")
            print(f"   ANSI Data Length: {result['validation']['data_length']} chars")
            print(f"   Barcode Size: {result['validation']['barcode_size']}")
            print(f"   State IIN: {result['validation']['state_iin']}")
            print(f"   Compliance: {result['validation']['compliant']}")
            
            # Test image decoding
            if result.get('barcode'):
                image_data = result['barcode'].split(',')[1]  # Remove data:image/png;base64,
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                print(f"   Image Format: {image.format}, Size: {image.size}")
                
            return True
        else:
            print(f"❌ PDF417 Generation Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ PDF417 Generation Exception: {e}")
        return False

def test_multiple_states():
    """Test PDF417 generation for multiple states"""
    test_states = ['TN', 'TX', 'CA', 'FL', 'NY']
    success_count = 0
    
    print(f"\n🧪 Testing Multiple States ({len(test_states)} states)...")
    
    for state in test_states:
        try:
            test_data = create_test_license_data(state)
            response = requests.post(f"{BASE_URL}/generate", json=test_data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {state}: IIN {result['validation']['state_iin']}")
                success_count += 1
            else:
                print(f"   ❌ {state}: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {state}: Exception - {e}")
    
    print(f"\n📊 Multi-State Results: {success_count}/{len(test_states)} states successful")
    return success_count == len(test_states)

def test_error_handling():
    """Test error handling with invalid data"""
    print(f"\n🧪 Testing Error Handling...")
    
    # Test cases with expected errors
    test_cases = [
        {"name": "Missing DL Number", "data": {"first_name": "John", "last_name": "Doe"}},
        {"name": "Invalid State", "data": create_test_license_data("XX")},
        {"name": "Invalid Date Format", "data": {**create_test_license_data(), "birth_date": "invalid"}},
        {"name": "Invalid Eye Color", "data": {**create_test_license_data(), "eye_color": "INVALID"}}
    ]
    
    success_count = 0
    for test_case in test_cases:
        try:
            response = requests.post(f"{BASE_URL}/generate", json=test_case["data"])
            if response.status_code in [400, 422]:  # Expected error codes
                print(f"   ✅ {test_case['name']}: Properly rejected ({response.status_code})")
                success_count += 1
            else:
                print(f"   ❌ {test_case['name']}: Unexpected response ({response.status_code})")
        except Exception as e:
            print(f"   ❌ {test_case['name']}: Exception - {e}")
    
    print(f"\n📊 Error Handling Results: {success_count}/{len(test_cases)} tests passed")
    return success_count == len(test_cases)

def test_ansi_compliance():
    """Test ANSI data format compliance"""
    print(f"\n🧪 Testing ANSI Compliance...")
    
    try:
        test_data = create_test_license_data()
        response = requests.post(f"{BASE_URL}/generate", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            ansi_data = result.get('ansi_data', '')
            
            # Check ANSI format requirements
            checks = [
                ("Starts with @", ansi_data.startswith('@')),
                ("Contains ANSI header", 'ANSI 636053' in ansi_data),
                ("Contains DL subfile", 'DL' in ansi_data),
                ("Has DAQ (DL Number)", 'DAQ' in ansi_data),
                ("Has DCS (Last Name)", 'DCS' in ansi_data),
                ("Has DAC (First Name)", 'DAC' in ansi_data),
                ("Has DBB (Birth Date)", 'DBB' in ansi_data),
                ("Has DBA (Expiry Date)", 'DBA' in ansi_data),
                ("Has DAG (Address)", 'DAG' in ansi_data),
                ("Has DCF (ICN)", 'DCF' in ansi_data)
            ]
            
            passed_checks = sum(1 for _, passed in checks if passed)
            
            for check_name, passed in checks:
                status = "✅" if passed else "❌"
                print(f"   {status} {check_name}")
            
            print(f"\n📊 ANSI Compliance: {passed_checks}/{len(checks)} checks passed")
            return passed_checks == len(checks)
        else:
            print(f"   ❌ Failed to generate test data: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ ANSI Compliance Test Exception: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting PDF417 Driver License Generator Tests\n")
    print(f"🔗 Testing API at: {BASE_URL}")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("API Health Check", test_api_health),
        ("Validation Endpoints", test_validation_endpoints),
        ("PDF417 Generation", test_pdf417_generation),
        ("Multi-State Support", test_multiple_states),
        ("Error Handling", test_error_handling),
        ("ANSI Compliance", test_ansi_compliance)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Final report
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The API is working correctly.")
    else:
        print(f"\n⚠️  {total-passed} tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)