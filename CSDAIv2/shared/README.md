# Shared Components

This folder contains shared configuration and utility files used by both the API server and Unified Analyzer.

## 📁 **Components**

### Configuration
- **`config.py`** - Shared configuration settings, security parameters, and environment variables
- **`security.py`** - Security validation, file handling, and access control functions

### Data
- **`temp/`** - Temporary file storage for uploaded logs and processing
- **`test_ds_log.txt`** - Sample Deep Security log file for testing
- **`test_log.txt`** - Additional sample log file for testing

## 🔧 **Usage**

Both `api-server` and `unified-analyzer` import these shared components:

```python
import sys
sys.path.append('../shared')
from config import get_config
from security import validate_file, create_secure_temp_file
```

## 🛡️ **Security Features**

- File type validation
- Size limit enforcement
- Secure temporary file handling
- Host access validation
- XML content validation
- Process name sanitization

## ⚙️ **Configuration Settings**

The `config.py` file manages:
- OpenAI API configuration
- File upload limits
- Temporary directory paths
- Security parameters
- Debug settings

## 📊 **Sample Data**

Test files are provided for both analyzers:
- **DS Agent logs** - Standard Deep Security agent log format
- **Generic logs** - General log file testing

## 🔄 **Shared Resources**

Both analyzer versions use the same:
- Temporary file storage
- Security validation logic
- Configuration management
- Sample test data

This ensures consistency and reduces code duplication between the two implementations.
