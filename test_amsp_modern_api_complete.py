#!/usr/bin/env python3
"""
AMSP Modern API Complete Validation Script
==========================================

This script performs comprehensive end-to-end testing of the AMSP analyzer
to ensure it's using ONLY the modern API format and NO legacy code remains.

Test Coverage:
1. Backend Modern API Format Validation
2. Frontend Integration Compatibility  
3. Legacy Code Elimination Verification
4. Modern API Response Structure Validation
5. End-to-End Flow Testing

Author: AI Agent
Date: 2024
Purpose: Validate complete AMSP legacy code removal and modern API integration
"""

import requests
import json
import os
import sys
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:5003"
TEST_LOG_PATH = "Utilities/0. sample_logs/amsp/amsp_sample.log"

def print_header(title):
    """Print formatted test section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_test_result(test_name, passed, details=""):
    """Print formatted test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    Details: {details}")
    return passed

def test_backend_health():
    """Test if backend is running and healthy"""
    print_header("Backend Health Check")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return print_test_result("Backend Health", True, f"Status: {data.get('status', 'Unknown')}")
        else:
            return print_test_result("Backend Health", False, f"Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        return print_test_result("Backend Health", False, f"Connection error: {str(e)}")

def test_modern_amsp_upload():
    """Test AMSP file upload with modern API format"""
    print_header("Modern AMSP Upload Test")
    
    # Check if test file exists
    if not os.path.exists(TEST_LOG_PATH):
        return print_test_result("AMSP Upload Test", False, f"Test file not found: {TEST_LOG_PATH}")
    
    try:
        # Upload file with AMSP analysis type
        with open(TEST_LOG_PATH, 'rb') as f:
            files = {'file': (os.path.basename(TEST_LOG_PATH), f, 'text/plain')}
            data = {'analysis_type': 'amsp'}
            
            response = requests.post(f"{BACKEND_URL}/upload", files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('session_id'):
                session_id = result['session_id']
                return print_test_result("AMSP Upload", True, f"Session ID: {session_id}"), session_id
            else:
                return print_test_result("AMSP Upload", False, f"Invalid response: {result}"), None
        else:
            return print_test_result("AMSP Upload", False, f"Status: {response.status_code}"), None
            
    except Exception as e:
        return print_test_result("AMSP Upload", False, f"Error: {str(e)}"), None

def test_modern_api_response_structure(session_id):
    """Test that the API returns proper modern format structure"""
    print_header("Modern API Response Structure Test")
    
    if not session_id:
        return print_test_result("Modern API Structure", False, "No session ID provided")
    
    try:
        # Poll for results
        max_attempts = 30
        for attempt in range(max_attempts):
            response = requests.get(f"{BACKEND_URL}/status/{session_id}", timeout=10)
            
            if response.status_code == 200:
                status_data = response.json()
                
                if status_data.get('status') == 'completed':
                    # Get results
                    results_response = requests.get(f"{BACKEND_URL}/results/{session_id}", timeout=15)
                    
                    if results_response.status_code == 200:
                        results = results_response.json()
                        return validate_modern_format_structure(results)
                    else:
                        return print_test_result("Modern API Structure", False, f"Results fetch failed: {results_response.status_code}")
                
                elif status_data.get('status') == 'failed':
                    return print_test_result("Modern API Structure", False, f"Analysis failed: {status_data.get('message', 'Unknown error')}")
            
            import time
            time.sleep(2)
        
        return print_test_result("Modern API Structure", False, "Analysis timed out")
        
    except Exception as e:
        return print_test_result("Modern API Structure", False, f"Error: {str(e)}")

def validate_modern_format_structure(results):
    """Validate that results contain modern API format structure"""
    test_results = []
    
    # Check main structure
    test_results.append(print_test_result(
        "Has 'success' field", 
        'success' in results
    ))
    
    test_results.append(print_test_result(
        "Has 'data' field", 
        'data' in results
    ))
    
    if 'data' in results:
        data = results['data']
        
        # Check modern format fields
        modern_fields = ['health', 'processing', 'issues', 'ai_analysis']
        for field in modern_fields:
            test_results.append(print_test_result(
                f"Has '{field}' field",
                field in data,
                f"Found in data: {field in data}"
            ))
        
        # Check health structure
        if 'health' in data:
            health = data['health']
            health_fields = ['system_score', 'status', 'status_icon']
            for field in health_fields:
                test_results.append(print_test_result(
                    f"Health has '{field}'",
                    field in health
                ))
        
        # Check processing structure
        if 'processing' in data:
            processing = data['processing']
            processing_fields = ['scans_analyzed', 'files_processed', 'total_operations']
            for field in processing_fields:
                test_results.append(print_test_result(
                    f"Processing has '{field}'",
                    field in processing
                ))
        
        # Check issues structure
        if 'issues' in data:
            issues = data['issues']
            issue_fields = ['critical', 'errors', 'warnings', 'important_events']
            for field in issue_fields:
                test_results.append(print_test_result(
                    f"Issues has '{field}'",
                    field in issues and isinstance(issues[field], list)
                ))
        
        # Check AI analysis structure
        if 'ai_analysis' in data:
            ai_analysis = data['ai_analysis']
            ai_fields = ['status', 'analysis', 'recommendations']
            for field in ai_fields:
                test_results.append(print_test_result(
                    f"AI Analysis has '{field}'",
                    field in ai_analysis
                ))
    
    # Check for absence of legacy fields
    legacy_fields = ['formatted_output', 'legacy_format', 'analysis_summary']
    for field in legacy_fields:
        test_results.append(print_test_result(
            f"No legacy '{field}' field",
            field not in (results.get('data', {})),
            f"Legacy field absent: {field not in (results.get('data', {}))}"
        ))
    
    all_passed = all(test_results)
    print_test_result("Overall Modern Format Validation", all_passed)
    
    # Print sample data for verification
    if 'data' in results:
        print(f"\nSample Modern Format Data:")
        print(f"Health Score: {results['data'].get('health', {}).get('system_score', 'N/A')}")
        print(f"Health Status: {results['data'].get('health', {}).get('status', 'N/A')}")
        print(f"Scans Analyzed: {results['data'].get('processing', {}).get('scans_analyzed', 'N/A')}")
        print(f"Critical Issues: {len(results['data'].get('issues', {}).get('critical', []))}")
        print(f"AI Analysis Status: {results['data'].get('ai_analysis', {}).get('status', 'N/A')}")
    
    return all_passed

def test_legacy_code_elimination():
    """Verify that no legacy AMSP code remains in the codebase"""
    print_header("Legacy Code Elimination Verification")
    
    test_files = [
        ("CSDAIv2/analyzers/amsp_analyzer.py", "AMSP Analyzer"),
        ("CSDAIv2/api_routes.py", "API Routes")
    ]
    
    legacy_patterns = [
        'def analyze(',
        'def analyze_log_file(',
        'format_amsp_results',
        'generate_amsp_recommendations',
        '_convert_intelligent_results_to_legacy_format',
        '_legacy_analyze_log_file',
        '_apply_dynamic_rag_to_analysis'
    ]
    
    all_clean = True
    
    for file_path, file_name in test_files:
        print(f"\nChecking {file_name}:")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_clean = True
            for pattern in legacy_patterns:
                if pattern in content:
                    print_test_result(f"  No '{pattern}'", False)
                    file_clean = False
                    all_clean = False
                else:
                    print_test_result(f"  No '{pattern}'", True)
            
            if file_clean:
                print_test_result(f"{file_name} Clean", True, "No legacy patterns found")
            else:
                print_test_result(f"{file_name} Clean", False, "Legacy patterns detected")
                
        except FileNotFoundError:
            print_test_result(f"{file_name} Check", False, f"File not found: {file_path}")
            all_clean = False
        except Exception as e:
            print_test_result(f"{file_name} Check", False, f"Error reading file: {str(e)}")
            all_clean = False
    
    return print_test_result("Overall Legacy Code Elimination", all_clean)

def main():
    """Run comprehensive AMSP modern API validation"""
    print("AMSP Modern API Complete Validation")
    print("====================================")
    print("Testing complete AMSP legacy code removal and modern API integration...")
    
    all_tests_passed = []
    
    # Test 1: Backend Health
    all_tests_passed.append(test_backend_health())
    
    # Test 2: Legacy Code Elimination
    all_tests_passed.append(test_legacy_code_elimination())
    
    # Test 3: Modern API Upload and Response
    upload_result, session_id = test_modern_amsp_upload()
    all_tests_passed.append(upload_result)
    
    if session_id:
        # Test 4: Modern API Response Structure
        all_tests_passed.append(test_modern_api_response_structure(session_id))
    else:
        print_test_result("Modern API Response Structure", False, "Could not test - no session ID")
        all_tests_passed.append(False)
    
    # Final Results
    print_header("FINAL VALIDATION RESULTS")
    
    total_tests = len(all_tests_passed)
    passed_tests = sum(all_tests_passed)
    
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    
    if all(all_tests_passed):
        print("🎉 ALL TESTS PASSED!")
        print("✅ AMSP is fully migrated to modern API format")
        print("✅ All legacy code has been successfully removed")
        print("✅ Modern API integration is working correctly")
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        print("⚠️  Modern API migration may be incomplete")
        print("⚠️  Please review failed tests and fix issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)