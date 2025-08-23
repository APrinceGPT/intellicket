"""
Test Dynamic RAG Integration across all analyzers
"""

def test_analyzer_rag_integration():
    """Test Dynamic RAG integration status for all analyzers"""
    print("🔬 TESTING DYNAMIC RAG INTEGRATION STATUS")
    print("=" * 60)
    
    try:
        # Import analyzers
        from analyzers import DSAgentLogAnalyzer, AMSPAnalyzer, ConflictAnalyzer, ResourceAnalyzer
        
        # Test data
        test_results = []
        
        analyzers = [
            ("DS Log Analyzer", DSAgentLogAnalyzer, "DS Agent logs"),
            ("AMSP Analyzer", AMSPAnalyzer, "AMSP logs"), 
            ("AV Conflict Analyzer", ConflictAnalyzer, "Process conflicts"),
            ("Resource Analyzer", ResourceAnalyzer, "Resource usage")
        ]
        
        for analyzer_name, analyzer_class, description in analyzers:
            print(f"\n🔍 Testing {analyzer_name}")
            print("-" * 40)
            
            try:
                # Check if analyzer has analyze_log_file method (for log-based analyzers)
                has_log_analysis = hasattr(analyzer_class, 'analyze_log_file')
                
                # Check if analyzer has RAG-related methods
                analyzer_instance = analyzer_class()
                
                # Get source code to check for RAG integration
                import inspect
                source_code = inspect.getsource(analyzer_class)
                
                # Check integration levels
                has_dynamic_rag = 'dynamic_rag_system' in source_code or 'DynamicRAGSystem' in source_code
                has_enhanced_rag = 'enhanced_rag_integration' in source_code or 'EnhancedRAGIntegration' in source_code
                has_standard_rag = 'rag_system' in source_code or 'CybersecurityRAG' in source_code
                
                # Determine integration status
                if has_dynamic_rag:
                    rag_status = "✅ Dynamic RAG"
                    rag_level = "Advanced"
                elif has_enhanced_rag:
                    rag_status = "🔶 Enhanced RAG Only"
                    rag_level = "Intermediate"
                elif has_standard_rag:
                    rag_status = "🔷 Standard RAG Only"  
                    rag_level = "Basic"
                else:
                    rag_status = "❌ No RAG Integration"
                    rag_level = "None"
                
                print(f"   📋 Purpose: {description}")
                print(f"   🔧 Log Analysis: {'✅ Yes' if has_log_analysis else '❌ No'}")
                print(f"   🧠 RAG Status: {rag_status}")
                print(f"   📊 Level: {rag_level}")
                
                test_results.append({
                    'analyzer': analyzer_name,
                    'has_log_analysis': has_log_analysis,
                    'has_dynamic_rag': has_dynamic_rag,
                    'has_enhanced_rag': has_enhanced_rag,
                    'has_standard_rag': has_standard_rag,
                    'rag_level': rag_level
                })
                
            except Exception as e:
                print(f"   ❌ Error testing {analyzer_name}: {e}")
                test_results.append({
                    'analyzer': analyzer_name,
                    'error': str(e)
                })
        
        # Summary
        print(f"\n📊 INTEGRATION SUMMARY")
        print("=" * 60)
        
        dynamic_count = sum(1 for r in test_results if r.get('has_dynamic_rag', False))
        enhanced_count = sum(1 for r in test_results if r.get('has_enhanced_rag', False) and not r.get('has_dynamic_rag', False))
        standard_count = sum(1 for r in test_results if r.get('has_standard_rag', False) and not r.get('has_enhanced_rag', False))
        no_rag_count = len(test_results) - dynamic_count - enhanced_count - standard_count
        
        print(f"🚀 Dynamic RAG Integrated: {dynamic_count}/4 analyzers")
        print(f"🔶 Enhanced RAG Only: {enhanced_count}/4 analyzers")
        print(f"🔷 Standard RAG Only: {standard_count}/4 analyzers")
        print(f"❌ No RAG Integration: {no_rag_count}/4 analyzers")
        
        # Detailed breakdown
        print(f"\n📋 DETAILED STATUS")
        print("-" * 60)
        for result in test_results:
            if 'error' not in result:
                analyzer = result['analyzer']
                level = result['rag_level']
                icon = {"Advanced": "✅", "Intermediate": "🔶", "Basic": "🔷", "None": "❌"}.get(level, "❓")
                print(f"{icon} {analyzer:<20} | {level}")
        
        # Recommendations
        print(f"\n🎯 RECOMMENDATIONS")
        print("-" * 60)
        
        if dynamic_count == 4:
            print("🎉 Perfect! All analyzers have Dynamic RAG integration.")
        elif dynamic_count >= 3:
            print("✅ Excellent! Most analyzers have Dynamic RAG integration.")
            print("📝 Consider upgrading remaining analyzers to Dynamic RAG.")
        elif dynamic_count >= 2:
            print("🔶 Good progress! Some analyzers have Dynamic RAG integration.")
            print("📝 Priority: Upgrade more analyzers to Dynamic RAG.")
        else:
            print("🔷 Basic status. Limited Dynamic RAG integration.")
            print("📝 Urgent: Implement Dynamic RAG across all analyzers.")
        
        # Check for excluded analyzer
        excluded_analyzers = [r for r in test_results if 'Conflict' in r['analyzer'] and not r.get('has_dynamic_rag', False)]
        if excluded_analyzers:
            print("ℹ️  Note: AV Conflict Analyzer excluded from Dynamic RAG (as requested)")
            
        return test_results
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None

if __name__ == "__main__":
    test_analyzer_rag_integration()
