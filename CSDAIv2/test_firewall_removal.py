#!/usr/bin/env python3
"""
Test script to verify FirewallAnalyzer removal was successful
and that all remaining analyzers work correctly
"""

import sys
import traceback

def test_imports():
    """Test that all remaining analyzers can be imported"""
    print("🔍 Testing analyzer imports...")
    
    try:
        from analyzers import (
            DSAgentLogAnalyzer, 
            AMSPAnalyzer, 
            ConflictAnalyzer, 
            ResourceAnalyzer, 
            DSAgentOfflineAnalyzer, 
            DiagnosticPackageAnalyzer
        )
        print("✅ All analyzers imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_firewall_analyzer_removed():
    """Test that FirewallAnalyzer is no longer available"""
    print("\n🔍 Testing FirewallAnalyzer removal...")
    
    try:
        from analyzers import FirewallAnalyzer
        print("❌ FirewallAnalyzer still exists - removal failed!")
        return False
    except ImportError:
        print("✅ FirewallAnalyzer successfully removed")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_routes_import():
    """Test that routes.py works without FirewallAnalyzer"""
    print("\n🔍 Testing routes module...")
    
    try:
        from routes import register_routes
        print("✅ Routes module imported successfully")
        return True
    except Exception as e:
        print(f"❌ Routes import failed: {e}")
        traceback.print_exc()
        return False

def test_api_routes_import():
    """Test that api_routes.py works without FirewallAnalyzer"""
    print("\n🔍 Testing API routes module...")
    
    try:
        from api_routes import register_api_routes
        print("✅ API routes module imported successfully")
        return True
    except Exception as e:
        print(f"❌ API routes import failed: {e}")
        traceback.print_exc()
        return False

def test_diagnostic_analyzer():
    """Test that DiagnosticPackageAnalyzer works without firewall_logs"""
    print("\n🔍 Testing DiagnosticPackageAnalyzer...")
    
    try:
        from analyzers import DiagnosticPackageAnalyzer
        analyzer = DiagnosticPackageAnalyzer()
        
        # Check that firewall_logs is not in package patterns
        patterns = analyzer.package_patterns
        if 'firewall_logs' in patterns:
            print("❌ firewall_logs still exists in package patterns")
            return False
            
        print(f"✅ DiagnosticPackageAnalyzer working correctly")
        print(f"   Available patterns: {list(patterns.keys())}")
        return True
    except Exception as e:
        print(f"❌ DiagnosticPackageAnalyzer test failed: {e}")
        traceback.print_exc()
        return False

def test_component_patterns():
    """Test that firewall is removed from component patterns"""
    print("\n🔍 Testing component patterns...")
    
    try:
        from analyzers import DSAgentLogAnalyzer
        analyzer = DSAgentLogAnalyzer()
        
        if 'firewall' in analyzer.component_patterns:
            print("❌ 'firewall' still exists in component patterns")
            return False
            
        print(f"✅ Component patterns cleaned successfully")
        print(f"   Available components: {list(analyzer.component_patterns.keys())}")
        return True
    except Exception as e:
        print(f"❌ Component patterns test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Starting FirewallAnalyzer removal verification tests...\n")
    
    tests = [
        test_imports,
        test_firewall_analyzer_removed,
        test_routes_import,
        test_api_routes_import,
        test_diagnostic_analyzer,
        test_component_patterns
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print("   Test failed!")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! FirewallAnalyzer removal was successful.")
        print("✅ System is ready for operation.")
        return True
    else:
        print("❌ Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
