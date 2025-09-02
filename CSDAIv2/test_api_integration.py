#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for API route integration with diagnostic packages
"""

import zipfile
import os
import tempfile
import requests
import time

def create_test_diagnostic_package():
    """Create a test diagnostic package for API testing"""
    test_zip_path = 'api_test_diagnostic_package.zip'
    sample_logs_dir = '../sample_logs'

    try:
        with zipfile.ZipFile(test_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            log_files = [
                'ds_agent.log',
                'AMSP-Inst_LocalDebugLog.log', 
                'RunningProcesses.xml',
                'TopNBusyProcess.txt'
            ]
            
            added_files = []
            for log_file in log_files:
                source_path = os.path.join(sample_logs_dir, log_file)
                if os.path.exists(source_path):
                    zipf.write(source_path, log_file)
                    added_files.append(log_file)
            
        return test_zip_path, len(added_files)
    except Exception as e:
        print(f"Failed to create test package: {e}")
        return None, 0

def test_api_upload_and_analysis():
    """Test the full API workflow"""
    print("Testing API Upload and Analysis Workflow...")
    
    # Create test package
    test_zip, file_count = create_test_diagnostic_package()
    if not test_zip:
        print("❌ Failed to create test package")
        return False
    
    print(f"✅ Created test package with {file_count} files: {test_zip}")
    
    try:
        # Test 1: Upload
        print("\n1. Testing upload endpoint...")
        upload_url = "http://localhost:5003/upload"
        
        with open(test_zip, 'rb') as f:
            files = {'file_0': f}
            data = {'analysis_type': 'diagnostic_package'}
            
            response = requests.post(upload_url, files=files, data=data, timeout=30)
            
        if response.status_code == 200:
            upload_result = response.json()
            if upload_result.get('success'):
                session_id = upload_result.get('session_id')
                print(f"✅ Upload successful. Session ID: {session_id}")
            else:
                print(f"❌ Upload failed: {upload_result.get('error')}")
                return False
        else:
            print(f"❌ Upload request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        # Test 2: Status polling
        print(f"\n2. Testing status endpoint for session: {session_id}")
        status_url = f"http://localhost:5003/status/{session_id}"
        
        max_attempts = 30  # 30 attempts * 10 seconds = 5 minutes max
        for attempt in range(max_attempts):
            status_response = requests.get(status_url, timeout=10)
            
            if status_response.status_code == 200:
                status_result = status_response.json()
                print(f"Status attempt {attempt + 1}: {status_result.get('status', 'unknown')}")
                
                if status_result.get('analysis_complete'):
                    if status_result.get('status') == 'completed':
                        print("✅ Analysis completed successfully")
                        break
                    elif status_result.get('status') == 'error':
                        print(f"❌ Analysis failed: {status_result.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"⏳ Analysis in progress... (attempt {attempt + 1})")
                    time.sleep(10)  # Wait 10 seconds before next check
            else:
                print(f"❌ Status request failed with status {status_response.status_code}")
                return False
        else:
            print("❌ Analysis timed out after 5 minutes")
            return False
        
        # Test 3: Get results
        print(f"\n3. Testing results endpoint for session: {session_id}")
        results_url = f"http://localhost:5003/results/{session_id}"
        
        results_response = requests.get(results_url, timeout=30)
        
        if results_response.status_code == 200:
            results_data = results_response.json()
            if results_data.get('success'):
                results = results_data.get('results', '')
                if len(results) > 1000:  # Should have substantial content
                    print(f"✅ Results retrieved successfully ({len(results)} characters)")
                    
                    # Check for expected content
                    if 'Diagnostic Package' in results and 'Executive Summary' in results:
                        print("✅ Results contain expected diagnostic package content")
                        return True
                    else:
                        print("⚠️  Results missing expected content sections")
                        return False
                else:
                    print(f"⚠️  Results seem too short: {len(results)} characters")
                    return False
            else:
                print(f"❌ Results request failed: {results_data.get('error')}")
                return False
        else:
            print(f"❌ Results request failed with status {results_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server. Make sure app.py is running on localhost:5003")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False
    finally:
        # Cleanup
        try:
            if os.path.exists(test_zip):
                os.remove(test_zip)
                print(f"\n🧹 Cleaned up test file: {test_zip}")
        except:
            pass

if __name__ == '__main__':
    print("API Integration Test for Diagnostic Package Analysis")
    print("="*60)
    
    # Test the API workflow
    success = test_api_upload_and_analysis()
    
    print("\n" + "="*60)
    print("API INTEGRATION TEST RESULT:")
    print(f"{'✅ PASS' if success else '❌ FAIL'}")
    
    if success:
        print("\n🎉 All API integration tests passed!")
        print("The diagnostic package analyzer is fully operational via API.")
    else:
        print("\n❌ API integration test failed.")
        print("Please check the backend server and fix any issues.")
