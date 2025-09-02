#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Diagnostic Package Analyzer
"""

import zipfile
import os
import tempfile
import sys

def test_diagnostic_package():
    print('Creating test diagnostic package...')

    # Create a test ZIP file with sample logs
    test_zip_path = 'test_diagnostic_package.zip'
    sample_logs_dir = '../sample_logs'

    try:
        with zipfile.ZipFile(test_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add some sample log files
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
                    print(f'Added: {log_file}')
            
            print(f'Created test ZIP with {len(added_files)} files: {test_zip_path}')
            
        # Test the diagnostic package analyzer
        print('\nTesting DiagnosticPackageAnalyzer...')
        from analyzers import DiagnosticPackageAnalyzer
        
        analyzer = DiagnosticPackageAnalyzer()
        
        # Test extraction
        print('Testing extract_zip_contents...')
        result = analyzer.extract_zip_contents(test_zip_path)
        
        if result.get('success'):
            print('✅ ZIP extraction successful')
            file_count = result.get('file_count', 0)
            extract_path = result.get('extract_path', 'Unknown')
            print(f'Files extracted: {file_count}')
            print(f'Extract path: {extract_path}')
        else:
            error = result.get('error', 'Unknown error')
            print(f'❌ ZIP extraction failed: {error}')
            return False
            
        # Test full analysis (this might take a while)
        print('\nTesting full diagnostic package analysis...')
        try:
            analysis_result = analyzer.analyze(test_zip_path)
            print('✅ Full analysis completed')
            
            # Check key result components
            if 'package_summary' in analysis_result:
                summary = analysis_result['package_summary']
                total_files = summary.get('total_files_analyzed', 0)
                print(f'Package Summary - Files analyzed: {total_files}')
                
            if 'individual_analyses' in analysis_result:
                analyses = analysis_result['individual_analyses']
                print(f'Individual Analyses: {list(analyses.keys())}')
                
            if 'executive_summary' in analysis_result:
                exec_summary = analysis_result['executive_summary']
                print(f'Executive Summary available: {bool(exec_summary)}')
                
            return True
                
        except Exception as e:
            print(f'❌ Full analysis failed: {str(e)}')
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f'❌ Test failed: {str(e)}')
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        try:
            if os.path.exists(test_zip_path):
                os.remove(test_zip_path)
                print(f'\nCleaned up test file: {test_zip_path}')
        except:
            pass

def test_api_integration():
    """Test API integration for diagnostic packages"""
    print('\n' + '='*50)
    print('Testing API Integration...')
    
    try:
        # Test that the analyzer is properly imported in api_routes
        import api_routes
        
        if hasattr(api_routes, 'DiagnosticPackageAnalyzer'):
            print('✅ DiagnosticPackageAnalyzer available in api_routes')
        else:
            print('❌ DiagnosticPackageAnalyzer not available in api_routes')
            return False
            
        # Test format function
        from routes import format_diagnostic_package_results
        print('✅ format_diagnostic_package_results imported successfully')
        
        # Test a mock result formatting
        mock_result = {
            'package_summary': {
                'total_files_analyzed': 4,
                'analysis_timestamp': '2025-08-28 10:00:00'
            },
            'executive_summary': {
                'overview': 'Test executive summary',
                'key_findings': ['Finding 1', 'Finding 2']
            },
            'individual_analyses': {
                'ds_agent': {'summary': 'DS Agent analysis'},
                'amsp': {'summary': 'AMSP analysis'}
            }
        }
        
        formatted = format_diagnostic_package_results(mock_result)
        if formatted and len(formatted) > 100:
            print('✅ Format function working correctly')
            return True
        else:
            print('❌ Format function returned unexpected result')
            return False
            
    except Exception as e:
        print(f'❌ API integration test failed: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print('Diagnostic Package Analyzer Test Suite')
    print('='*50)
    
    # Test 1: Basic functionality
    success1 = test_diagnostic_package()
    
    # Test 2: API integration
    success2 = test_api_integration()
    
    print('\n' + '='*50)
    print('TEST RESULTS:')
    print(f'Basic Functionality: {"✅ PASS" if success1 else "❌ FAIL"}')
    print(f'API Integration: {"✅ PASS" if success2 else "❌ FAIL"}')
    
    if success1 and success2:
        print('\n🎉 All tests passed! Diagnostic Package Analyzer is working correctly.')
        sys.exit(0)
    else:
        print('\n❌ Some tests failed. Please check the implementation.')
        sys.exit(1)
