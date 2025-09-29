# -*- coding: utf-8 -*-
"""
Shared imports and dependencies for all analyzers
Ensures consistent dependency handling across modular analyzer system
"""

import os
import re
import xml.etree.ElementTree as ET
import zipfile
import tempfile
from datetime import datetime
from typing import List, Dict, Any, Union
from security import SecurityError, validate_xml_content, sanitize_process_name

# Import OpenAI for analysis
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Machine Learning Analysis - Backend Enhancement for Dynamic RAG
try:
    from ml_analyzer import enhance_analysis_with_ml
    ML_AVAILABLE = True
    print("✅ ML-Enhanced Analysis Available")
except ImportError as e:
    ML_AVAILABLE = False
    print(f"⚠️  ML enhancement not available: {e}")

# Dynamic RAG Integration - the only RAG system
try:
    from dynamic_rag_system import DynamicRAGSystem, apply_dynamic_rag_to_analysis
    DYNAMIC_RAG_AVAILABLE = True
    print("✅ Dynamic RAG system loaded successfully")
except ImportError as e:
    DYNAMIC_RAG_AVAILABLE = False
    print(f"⚠️ Dynamic RAG system not available: {e}")

# Export all shared dependencies
__all__ = [
    'os', 're', 'ET', 'datetime', 'List', 'Dict', 'Any', 'Union', 'zipfile', 'tempfile',
    'SecurityError', 'validate_xml_content', 'sanitize_process_name',
    'OpenAI', 'OPENAI_AVAILABLE', 'enhance_analysis_with_ml', 'ML_AVAILABLE',
    'DynamicRAGSystem', 'apply_dynamic_rag_to_analysis', 'DYNAMIC_RAG_AVAILABLE'
]
