#!/usr/bin/env python3
"""
Comprehensive validation script for AMSP modern format
Tests the complete flow and identifies any remaining issues
"""
import sys
import os
import json
import requests
import time
from datetime import datetime

def validate_backend_health():
    """Validate backend is healthy and responding"""
    print("🏥 BACKEND HEALTH CHECK")
    print("-" * 30)
    
    try:
        # Test basic connection
        response = requests.get("http://localhost:5003", timeout=5)
        if response.status_code != 200:
            print(f"❌ Backend not responding: {response.status_code}")
            return False
        print("✅ Backend responding")
        
        # Test health endpoint
        health_response = requests.get("http://localhost:5003/api/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Health endpoint: {health_data}")
        else:
            print(f"⚠️ Health endpoint issue: {health_response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False

def validate_modern_amsp_format():
    """Validate the modern AMSP format is working correctly"""
    print("\n🧠 MODERN AMSP FORMAT VALIDATION")
    print("-" * 40)
    
    test_file = "../Utilities/0. sample_logs/AMSP-Inst_LocalDebugLog.log"
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    # Upload test
    try:
        with open(test_file, 'rb') as f:
            files = {'files': (os.path.basename(test_file), f, 'text/plain')}
            data = {'analysis_type': 'amsp'}
            
            upload_response = requests.post("http://localhost:5003/upload", files=files, data=data, timeout=30)
            
        if upload_response.status_code != 200:
            print(f"❌ Upload failed: {upload_response.status_code} - {upload_response.text}")
            return False
            
        upload_data = upload_response.json()
        session_id = upload_data.get('session_id')
        print(f"✅ Upload successful: {session_id}")
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False
    
    # Wait for completion
    print("⏳ Waiting for analysis completion...")
    max_attempts = 20
    for attempt in range(max_attempts):
        try:
            status_response = requests.get(f"http://localhost:5003/status/{session_id}", timeout=10)
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get('status', 'unknown')
                
                if status in ['completed', 'error']:
                    print(f"✅ Analysis {status}")
                    break
                    
                time.sleep(2)
            else:
                print(f"⚠️ Status check failed: {status_response.status_code}")
                break
                
        except Exception as e:
            print(f"❌ Status check error: {e}")
            break
    else:
        print("❌ Analysis timed out")
        return False
    
    # Get and validate results
    try:
        results_response = requests.get(f"http://localhost:5003/results/{session_id}", timeout=10)
        
        if results_response.status_code != 200:
            print(f"❌ Results failed: {results_response.status_code} - {results_response.text}")
            return False
        
        results_data = results_response.json()
        
        # Validate modern format structure
        analysis_result = results_data.get('analysis_result', {})
        
        # Check required modern format fields
        required_fields = ['health', 'processing', 'issues', 'ai_analysis']
        missing_fields = [field for field in required_fields if field not in analysis_result]
        
        if missing_fields:
            print(f"❌ Missing modern format fields: {missing_fields}")
            return False
        
        print("✅ Modern format structure validated")
        
        # Validate health data structure
        health_data = analysis_result.get('health', {})
        health_required = ['system_score', 'status', 'status_message']
        health_missing = [field for field in health_required if field not in health_data]
        
        if health_missing:
            print(f"❌ Missing health fields: {health_missing}")
            return False
        
        print(f"✅ Health data: Score={health_data.get('system_score')}, Status={health_data.get('status')}")
        
        # Validate processing data structure
        processing_data = analysis_result.get('processing', {})
        processing_required = ['total_lines', 'processed_lines', 'success_rate']
        processing_missing = [field for field in processing_required if field not in processing_data]
        
        if processing_missing:
            print(f"❌ Missing processing fields: {processing_missing}")
            return False
        
        print(f"✅ Processing data: {processing_data.get('processed_lines')}/{processing_data.get('total_lines')} lines ({processing_data.get('success_rate')}%)")
        
        # Validate AI analysis structure
        ai_analysis = analysis_result.get('ai_analysis', {})
        ai_required = ['applied', 'recommendations']
        ai_missing = [field for field in ai_required if field not in ai_analysis]
        
        if ai_missing:
            print(f"❌ Missing AI analysis fields: {ai_missing}")
            return False
        
        print(f"✅ AI Analysis: Applied={ai_analysis.get('applied')}, Recommendations={len(ai_analysis.get('recommendations', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Results validation error: {e}")
        return False

def validate_system_integrity():
    """Check for any system integrity issues"""
    print("\n🔍 SYSTEM INTEGRITY CHECK")
    print("-" * 30)
    
    # Check critical files exist
    critical_files = [
        "api_routes.py",
        "analyzers/amsp_analyzer.py", 
        "analyzers/modern_api_format.py",
        "app.py"
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            return False
    
    # Try importing key modules
    try:
        sys.path.append('.')
        from analyzers.amsp_analyzer import AMSPAnalyzer
        from analyzers.modern_api_format import ModernAMSPAnalysisResponse
        print("✅ Key modules importable")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True

def main():
    """Run comprehensive validation"""
    print("🔬 COMPREHENSIVE SYSTEM VALIDATION")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Run all validations
    results = []
    
    results.append(("Backend Health", validate_backend_health()))
    results.append(("System Integrity", validate_system_integrity()))
    results.append(("Modern AMSP Format", validate_modern_amsp_format()))
    
    # Summary
    print("\n📊 VALIDATION SUMMARY")
    print("=" * 30)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("✅ Modern AMSP format is working correctly")
        print("✅ System is ready for production use")
    else:
        print("⚠️ SOME VALIDATIONS FAILED")
        print("❌ Review failed tests and fix issues")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)