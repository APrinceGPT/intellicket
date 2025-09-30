# -*- coding: utf-8 -*-
"""
Modular Analyzer System - Central Import Hub
Maintains 100% backward compatibility with original analyzers.py
CRITICAL: This file ensures zero breaking changes for all 33 dependent files
"""

# Import base class
from .base.standardizer import AnalyzerOutputStandardizer

# Phase 1: Import already extracted analyzers (safe imports with fallback)
try:
    from .conflict_analyzer import ConflictAnalyzer
    print("✅ Using modular ConflictAnalyzer")
except ImportError as e:
    print(f"❌ ConflictAnalyzer not available: {e}")
    ConflictAnalyzer = None

# Phase 2: Import all modular analyzers
try:
    from .ds_agent_log_analyzer import DSAgentLogAnalyzer
    print("✅ Using modular DSAgentLogAnalyzer (backend-only)")
except ImportError as e:
    print(f"❌ DSAgentLogAnalyzer not available: {e}")
    DSAgentLogAnalyzer = None

try:
    from .amsp_analyzer import AMSPAnalyzer
    print("✅ Using modular AMSPAnalyzer")
except ImportError as e:
    print(f"❌ AMSPAnalyzer not available: {e}")
    AMSPAnalyzer = None

try:
    from .resource_analyzer import ResourceAnalyzer
    print("✅ Using modular ResourceAnalyzer")
except ImportError as e:
    print(f"❌ ResourceAnalyzer not available: {e}")
    ResourceAnalyzer = None

try:
    from .ds_agent_offline_analyzer import DSAgentOfflineAnalyzer
    print("✅ Using modular DSAgentOfflineAnalyzer (backend-only)")
except ImportError as e:
    print(f"❌ DSAgentOfflineAnalyzer not available: {e}")
    DSAgentOfflineAnalyzer = None

try:
    from .ds_agent_log_analyzer import DSAgentLogAnalyzer
    print("✅ Using modular DSAgentLogAnalyzer (backend-only)")
except ImportError as e:
    print(f"❌ DSAgentLogAnalyzer not available: {e}")
    DSAgentLogAnalyzer = None

try:
    from .diagnostic_package_analyzer import DiagnosticPackageAnalyzer
    print("✅ Using modular DiagnosticPackageAnalyzer")
except ImportError:
    # Fallback to original during transition
    try:
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        from analyzers import DiagnosticPackageAnalyzer
        print("✅ Using original DiagnosticPackageAnalyzer")
    except ImportError as e:
        print(f"❌ DiagnosticPackageAnalyzer not available: {e}")
        DiagnosticPackageAnalyzer = None

# Export all classes for backward compatibility
# This ensures that "from analyzers import ConflictAnalyzer" continues to work
__all__ = [
    'AnalyzerOutputStandardizer',
    'DSAgentLogAnalyzer',
    'AMSPAnalyzer', 
    'ConflictAnalyzer',
    'ResourceAnalyzer',
    'DSAgentOfflineAnalyzer',
    'DiagnosticPackageAnalyzer'
]

# Remove None values from __all__ to prevent import errors
__all__ = [name for name in __all__ if globals().get(name) is not None]

print(f"📦 Modular Analyzer System loaded - Available analyzers: {__all__}")
