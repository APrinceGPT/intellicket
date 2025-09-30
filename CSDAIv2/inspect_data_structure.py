#!/usr/bin/env python3
"""
Detailed Data Structure Analysis
===============================

This script inspects the exact data structure returned by the backend
to understand what the frontend is receiving vs what it expects.
"""

import requests
import json

BACKEND_URL = "http://localhost:5003"

def analyze_data_structure():
    """Analyze the exact data structure returned by the backend"""
    print("🔍 DETAILED DATA STRUCTURE ANALYSIS")
    print("=" * 70)
    
    # Upload and get session ID
    log_file_path = "../Utilities/0. sample_logs/AMSP-Inst_LocalDebugLog.log"
    
    with open(log_file_path, 'rb') as f:
        files = {'file': ('AMSP-Inst_LocalDebugLog.log', f, 'text/plain')}
        data = {'analysis_type': 'amsp'}
        response = requests.post(f"{BACKEND_URL}/upload", files=files, data=data, timeout=30)
    
    session_id = response.json()['session_id']
    print(f"📋 Session ID: {session_id}")
    
    # Get results
    response = requests.get(f"{BACKEND_URL}/results/{session_id}", timeout=10)
    full_data = response.json()
    
    print(f"\n📊 TOP-LEVEL STRUCTURE:")
    print(f"Keys: {list(full_data.keys())}")
    
    results = full_data.get('results', {})
    print(f"\n📊 RESULTS STRUCTURE:")
    print(f"Type: {type(results)}")
    print(f"Keys: {list(results.keys()) if isinstance(results, dict) else 'Not a dict'}")
    
    # Check what the frontend expects vs what we have
    print(f"\n🔍 FRONTEND EXPECTATION ANALYSIS:")
    
    # Frontend expects: analysis_result.metadata.system_health_score
    if 'analysis_result' in results:
        analysis_result = results['analysis_result']
        print(f"✅ analysis_result found: {type(analysis_result)}")
        
        if isinstance(analysis_result, dict) and 'metadata' in analysis_result:
            metadata = analysis_result['metadata']
            print(f"✅ metadata found: {type(metadata)}")
            print(f"✅ metadata keys: {list(metadata.keys()) if isinstance(metadata, dict) else 'Not a dict'}")
            
            # Check for expected fields
            expected_metadata_fields = [
                'system_health_score', 'total_lines', 'errors_found', 'warnings_found',
                'ai_analysis_applied', 'ml_analysis_applied', 'rag_analysis_applied', 'fallback_mode'
            ]
            
            for field in expected_metadata_fields:
                if isinstance(metadata, dict) and field in metadata:
                    print(f"✅ {field}: {metadata[field]}")
                else:
                    print(f"❌ {field}: NOT FOUND")
        else:
            print(f"❌ metadata not found in analysis_result")
    else:
        print(f"❌ analysis_result not found")
    
    # Frontend expects: analysis_result.intelligent_analysis
    if 'analysis_result' in results:
        analysis_result = results['analysis_result']
        if isinstance(analysis_result, dict) and 'intelligent_analysis' in analysis_result:
            intelligent_analysis = analysis_result['intelligent_analysis']
            print(f"✅ intelligent_analysis found: {type(intelligent_analysis)}")
            print(f"✅ intelligent_analysis keys: {list(intelligent_analysis.keys()) if isinstance(intelligent_analysis, dict) else 'Not a dict'}")
        else:
            print(f"❌ intelligent_analysis not found in analysis_result")
    
    # Check what modern data we actually have
    print(f"\n🆕 MODERN FORMAT DATA ANALYSIS:")
    
    # Look for modern fields directly in results
    modern_fields = ['health', 'processing', 'issues', 'ai_analysis']
    for field in modern_fields:
        if field in results:
            field_data = results[field]
            print(f"✅ {field} found: {type(field_data)}")
            if isinstance(field_data, dict):
                print(f"   Keys: {list(field_data.keys())}")
        else:
            print(f"❌ {field}: NOT FOUND")
    
    # Check intelligent_analysis (legacy location)
    if 'intelligent_analysis' in results:
        intelligent_analysis = results['intelligent_analysis']
        print(f"✅ intelligent_analysis (top-level) found: {type(intelligent_analysis)}")
        if isinstance(intelligent_analysis, dict):
            print(f"   Keys: {list(intelligent_analysis.keys())}")
            
            # Check for ai_insights
            if 'ai_insights' in intelligent_analysis:
                ai_insights = intelligent_analysis['ai_insights']
                print(f"✅ ai_insights found: {type(ai_insights)}")
                if isinstance(ai_insights, dict):
                    print(f"   Keys: {list(ai_insights.keys())}")
                    
                    # Check for system_health_score
                    if 'system_health_score' in ai_insights:
                        print(f"✅ system_health_score: {ai_insights['system_health_score']}")
    
    # Print a sample of the actual data structure
    print(f"\n📄 SAMPLE DATA STRUCTURE:")
    print("=" * 50)
    
    # Show the structure the frontend is looking for
    sample_data = {}
    if 'analysis_result' in results:
        sample_data['analysis_result'] = {}
        analysis_result = results['analysis_result']
        
        if isinstance(analysis_result, dict):
            if 'metadata' in analysis_result:
                sample_data['analysis_result']['metadata'] = analysis_result['metadata']
            if 'intelligent_analysis' in analysis_result:
                sample_data['analysis_result']['intelligent_analysis'] = analysis_result['intelligent_analysis']
    
    if 'intelligent_analysis' in results:
        sample_data['intelligent_analysis'] = results['intelligent_analysis']
    
    print(json.dumps(sample_data, indent=2, default=str)[:1000] + "...")
    
    print(f"\n🎯 ROOT CAUSE DIAGNOSIS:")
    print("=" * 50)
    
    # Check if we have modern format data but in wrong structure
    has_modern_data = any(field in results for field in ['health', 'processing', 'issues'])
    has_legacy_structure = 'analysis_result' in results and isinstance(results.get('analysis_result'), dict)
    has_intelligent_analysis = 'intelligent_analysis' in results
    
    print(f"✅ Has modern data fields: {has_modern_data}")
    print(f"✅ Has legacy structure: {has_legacy_structure}")
    print(f"✅ Has intelligent_analysis: {has_intelligent_analysis}")
    
    if has_legacy_structure and not has_modern_data:
        print("\n🔧 SOLUTION: Backend is using legacy format instead of modern format")
        print("   - The analyze_modern() method may not be called")
        print("   - Session storage may be saving legacy results")
        print("   - API route may be calling analyze() instead of analyze_modern()")
    elif has_modern_data and has_legacy_structure:
        print("\n🔧 SOLUTION: Mixed format - need to choose one")
        print("   - Backend returns both modern and legacy data")
        print("   - Frontend needs to be updated to use modern data")
        print("   - Should remove legacy conversion")
    else:
        print("\n🔧 SOLUTION: Unknown data structure issue")

if __name__ == "__main__":
    analyze_data_structure()