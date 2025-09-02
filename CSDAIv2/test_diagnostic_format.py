#!/usr/bin/env python3
"""
Test script to verify the diagnostic package formatting function works correctly
"""

import sys
import os
sys.path.append('.')

# Import the formatting function
from routes import format_diagnostic_package_results

# Create sample data structure that matches what DiagnosticPackageAnalyzer returns
sample_analysis = {
    'package_summary': {
        'total_files_analyzed': 5,
        'analysis_duration': '0:00:15.234567',
        'analysis_timestamp': '2025-08-28 10:30:00'
    },
    'correlation_analysis': {
        'timing_correlations': [
            {'description': 'Firewall activation occurred during DS Agent restart'},
            {'description': 'AMSP scan started simultaneously with DS Agent error'}
        ],
        'component_correlations': [
            {'description': 'DS Agent and AMSP both detected memory conflicts'}
        ],
        'issue_correlations': [],
        'cross_log_patterns': [
            'Pattern: Network connectivity issues detected across multiple components'
        ]
    },
    'individual_analyses': {
        'ds_agent': {
            'summary': 'DS Agent analysis completed with 3 warnings and 1 error',
            'analysis_text': 'DS Agent logs show connectivity issues and memory warnings during startup sequence'
        },
        'amsp': {
            'summary': 'AMSP analysis found potential exclusion candidates',
            'analysis_text': 'AMSP logs indicate high CPU usage during full system scans'
        },
        'av_conflicts': {
            'analysis_text': 'No significant antivirus conflicts detected in running processes'
        }
    },
    'executive_summary': {
        'overview': 'Comprehensive analysis of diagnostic package reveals connectivity and performance issues',
        'key_findings': [
            'Network connectivity problems affecting DS Agent startup',
            'High CPU usage during AMSP scans',
            'Memory allocation warnings in DS Agent logs'
        ],
        'recommendations': [
            'Check network configuration and firewall rules',
            'Consider adding exclusions for high-usage processes'
        ]
    },
    'recommendations': [
        'Review system resources during peak scan times',
        'Update network connectivity troubleshooting documentation'
    ],
    'ml_insights': {
        'overall_health_score': 75,
        'patterns': ['connectivity_pattern', 'performance_pattern']
    },
    'dynamic_rag_analysis': {
        'ai_response': 'Based on the diagnostic data, this appears to be a common network configuration issue that can be resolved by adjusting firewall rules.',
        'knowledge_sources': ['Network Troubleshooting Guide', 'Performance Optimization Manual']
    }
}

print("Testing diagnostic package formatting function...")
print("=" * 60)

try:
    formatted_result = format_diagnostic_package_results(sample_analysis)
    
    print("✅ Formatting function executed successfully!")
    print(f"📊 Result length: {len(formatted_result)} characters")
    
    # Check if key elements are present
    checks = [
        ('Files Analyzed: 5', '5 files detected'),
        ('Cross-Correlations', 'correlations counted'),
        ('Analysis Duration', 'duration calculated'),
        ('Key Findings', 'findings section'),
        ('Recommendations', 'recommendations section'),
        ('Individual File Analysis', 'individual analyses'),
        ('Cross-Log Correlations', 'correlation section'),
    ]
    
    print("\n🔍 Content validation:")
    for check_text, description in checks:
        if check_text in formatted_result:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - missing '{check_text}'")
    
    # Save formatted result for inspection
    with open('test_diagnostic_output.html', 'w', encoding='utf-8') as f:
        f.write(formatted_result)
    print(f"\n💾 Full formatted result saved to: test_diagnostic_output.html")
    
    print("\n🎯 Test completed successfully!")
    
except Exception as e:
    print(f"❌ Formatting function failed: {e}")
    import traceback
    traceback.print_exc()
