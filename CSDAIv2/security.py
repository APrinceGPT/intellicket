"""
Security utilities for the CSD AntiVirus Conflict Analyzer
Contains functions to handle security-related operations safely
"""
import os
import tempfile
import uuid
from werkzeug.utils import secure_filename
from typing import Optional, List
import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError

class SecurityError(Exception):
    """Custom exception for security-related errors"""
    pass

def validate_file(file) -> str:
    """
    Validate uploaded file for security (XML, PDF, or LOG)
    
    Args:
        file: Flask file object
        
    Returns:
        str: File type ('xml', 'pdf', or 'log')
        
    Raises:
        SecurityError: If file fails security checks
    """
    if not file:
        raise SecurityError("No file provided")
    
    if not file.filename:
        raise SecurityError("No filename provided")
    
    # Check file extension
    filename = secure_filename(file.filename)
    if filename.lower().endswith('.xml'):
        file_type = 'xml'
    elif filename.lower().endswith('.pdf'):
        file_type = 'pdf'
    elif filename.lower().endswith(('.log', '.txt')):
        file_type = 'log'
    elif filename.lower().endswith('.zip'):
        file_type = 'zip'
    elif filename.lower().endswith(('.db', '.dat', '.json', '.csv', '.cfg', '.conf')):
        file_type = 'data'
    else:
        raise SecurityError("File must be an XML, PDF, LOG, ZIP, or DATA file (.log, .txt, .xml, .pdf, .zip, .db, .dat, .json, .csv, .cfg, .conf)")
    
    # Check file size (basic check, Flask's MAX_CONTENT_LENGTH handles the rest)
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if size > 500 * 1024 * 1024:  # 500MB limit per file
        raise SecurityError("File too large")
    
    if size == 0:
        raise SecurityError("File is empty")
    
    return file_type

def create_secure_temp_file(file, temp_dir: str = "temp") -> str:
    """
    Create a secure temporary file from uploaded file
    
    Args:
        file: Flask file object
        temp_dir: Directory for temporary files
        
    Returns:
        str: Path to secure temporary file
        
    Raises:
        SecurityError: If file operations fail
    """
    try:
        # Ensure temp directory exists
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())
        temp_filename = f"upload_{unique_id}.xml"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        # Save file securely
        file.save(temp_path)
        
        return temp_path
        
    except Exception as e:
        raise SecurityError(f"Failed to create secure temporary file: {str(e)}")

def validate_xml_content(xml_path: str) -> bool:
    """
    Validate XML content for security issues
    
    Args:
        xml_path: Path to XML file
        
    Returns:
        bool: True if XML is safe to parse
        
    Raises:
        SecurityError: If XML contains security issues
    """
    try:
        with open(xml_path, 'rb') as f:
            content = f.read()
            
        # Check for potentially dangerous XML features
        content_str = content.decode('utf-8', errors='ignore').lower()
        
        dangerous_patterns = [
            '<!entity',     # External entities
            '<!doctype',    # Document type declarations with external entities
            'file://',      # File protocol
            'ftp://',       # FTP protocol
            'jar://',       # JAR protocol
            'netdoc://',    # NetDoc protocol
            'gopher://',    # Gopher protocol
            'ldap://',      # LDAP protocol
        ]
        
        # More specific system-related patterns that are actually dangerous
        dangerous_system_patterns = [
            'system(',           # System function calls
            'system "',          # System command execution
            'system\'',          # System command execution with single quotes
            '<!entity system',   # External system entity
            'system public',     # System public identifier
        ]
        
        for pattern in dangerous_patterns:
            if pattern in content_str:
                raise SecurityError(f"Potentially dangerous XML pattern detected: {pattern}")
        
        for pattern in dangerous_system_patterns:
            if pattern in content_str:
                raise SecurityError(f"Potentially dangerous XML system pattern detected: {pattern}")
        
        # Check for excessive entity references (billion laughs attack)
        # Count only potentially dangerous entities, not standard HTML entities
        dangerous_entity_patterns = ['&[a-zA-Z]+;', '%[a-zA-Z]+;']
        standard_html_entities = ['&quot;', '&amp;', '&lt;', '&gt;', '&apos;']
        
        # Count total entities
        total_entities = content_str.count('&') + content_str.count('%')
        
        # Subtract standard HTML entities from the count
        for entity in standard_html_entities:
            total_entities -= content_str.count(entity.lower())
        
        # Allow reasonable number of non-standard entities
        if total_entities > 500:  # Increased limit for legitimate use
            raise SecurityError("Excessive non-standard entity references detected")
        
        # Try to parse the XML safely without setting readonly attributes
        try:
            # Use defusedxml approach - disable dangerous features by not enabling them
            ET.fromstring(content)
        except ET.ParseError as e:
            raise SecurityError(f"Invalid XML format: {str(e)}")
        
        return True
        
    except ExpatError as e:
        raise SecurityError(f"Invalid XML format: {str(e)}")
    except Exception as e:
        raise SecurityError(f"XML validation failed: {str(e)}")

def sanitize_process_name(process_name: str) -> str:
    """
    Sanitize process names to prevent injection attacks
    
    Args:
        process_name: Raw process name from XML
        
    Returns:
        str: Sanitized process name
    """
    if not process_name:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', '\n', '\r', '\t']
    sanitized = process_name
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    # Limit length to prevent buffer overflow attacks
    return sanitized[:255]

def cleanup_temp_file(file_path: str) -> None:
    """
    Securely clean up temporary files
    
    Args:
        file_path: Path to temporary file to remove
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        # Log error in production, but don't expose details
        pass

def validate_host_access(request_host: str, allowed_hosts: List[str]) -> bool:
    """
    Validate that request is coming from allowed host
    
    Args:
        request_host: Host from request
        allowed_hosts: List of allowed hosts
        
    Returns:
        bool: True if host is allowed
    """
    if not request_host:
        return False
    
    # Remove port if present
    host_without_port = request_host.split(':')[0]
    
    return host_without_port in allowed_hosts
