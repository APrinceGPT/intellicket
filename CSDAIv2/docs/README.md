# Deep Security Agent Log Analyzer (DSAI_TOOL)

## Overview

The Deep Security Agent Log Analyzer is an AI-powered tool designed to analyze Trend Micro Deep Security Agent log files (ds_agent.log) and identify errors, warnings, and potential issues. It provides comprehensive analysis with expert recommendations and troubleshooting guidance.

## Features

### 🔍 **Comprehensive Log Analysis**
- Parses and analyzes ds_agent.log files
- Identifies errors, warnings, and critical issues
- Categorizes log entries by severity and component
- Provides detailed statistics and summaries

### 🎯 **Component-Specific Analysis**
- **Anti-Malware**: AMSP, Aegis, ADC modules
- **Intrusion Prevention**: DPI/IPS modules  
- **Integrity Monitoring**: File integrity monitoring
- **Log Inspection**: Log analysis modules
- **Device Control**: USB/device management
- **Web Reputation**: URL reputation checking
- **Application Control**: Application whitelisting
- **Connection Handler**: Agent-Manager communication
- **Agent Core**: Core agent functionality

### 📁 **Unified Drag & Drop Upload**
- **Drag & Drop Interface**: Simply drag files from your computer directly to the web interface
- **Unified Upload**: Supports both single and multiple file uploads in one interface
- **Auto-Detection**: Automatically switches between single and multiple file analysis modes
- **Visual File Management**: See selected files with options to remove individual files
- **Real-time Validation**: Instant feedback on file types, sizes, and limits
- **Smart Analysis**: Combines analysis across multiple files when appropriate

### 🤖 **AI-Powered Insights**
- Expert analysis using Trend Micro knowledge base
- Root cause analysis and troubleshooting recommendations
- Performance impact assessment
- Priority issue identification

### 🛡️ **Security Features**
- Secure file upload validation
- Temporary file handling with cleanup
- Host access validation
- Input sanitization

## Installation

### Prerequisites
- Python 3.9+
- Required Python packages (automatically installed):
  - Flask
  - OpenAI (compatible version)
  - python-dotenv

### Setup
1. Copy required files to DS TOOL directory:
   ```
   config.py
   security.py
   .env
   DSAI_TOOL.py
   ```

2. Configure environment variables in `.env`:
   ```
   OPENAI_BASE_URL=https://api.rdsec.trendmicro.com/prod/aiendpoint/v1/
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=claude-4-sonnet
   ```

3. Run the application:
   ```bash
   python DSAI_TOOL.py
   ```

4. Access the web interface:
   ```
   http://127.0.0.1:5001
   ```

## Usage

### Web Interface
1. Open http://127.0.0.1:5001 in your browser
2. **Drag & Drop Files**: 
   - Drag one or more ds_agent.log files directly onto the upload area, OR
   - Click the upload area to browse and select files
3. **File Management**:
   - View selected files in the file list
   - Remove individual files if needed
   - Clear all files to start over
4. Click "Analyze Files" to process your upload(s)
5. Review the comprehensive analysis results

### Upload Methods
- **Drag & Drop**: Drag files from Windows Explorer directly to the web interface
- **Click to Browse**: Click the upload area to open a file browser
- **Mixed Selection**: Combine dragging and browsing to select multiple files

### Analysis Modes (Automatic)
The system automatically determines the analysis mode based on the number of files:

#### Single File Analysis (1 file)
- Focused analysis with detailed insights specific to that file
- Individual component breakdown
- Targeted recommendations

#### Multiple File Analysis (2-10 files)
- **Combined Statistics**: Aggregated data across all files
- **File-by-File Breakdown**: Individual status for each uploaded file  
- **Cross-File Patterns**: Issues that appear across multiple files
- **Comprehensive AI Analysis**: Insights considering all uploaded files together

### Analysis Results Include:

#### 📊 **Summary Statistics**
- Total log lines processed
- Parse success rate
- Error/warning counts
- Time range coverage

#### 🔴 **Critical Issues** (if any)
- High-priority problems requiring immediate attention
- Detailed error messages and locations
- Component identification

#### ⚠️ **Warning Analysis**
- Non-critical issues that may need attention
- Recurring patterns
- Performance implications

#### 🔍 **Known Issues Detection**
- Automatic identification of common DS agent problems
- Pre-defined resolutions and explanations
- Impact assessment

#### 🔧 **Component Health Analysis**
- Per-component error rates
- Health scoring
- Trend analysis

#### 🤖 **AI Expert Analysis**
- Comprehensive expert insights
- Root cause analysis
- Prioritized troubleshooting steps
- Performance recommendations

## Sample Analysis Output

```
🟢 Agent Status: HEALTHY

📊 Summary Statistics:
- Total Lines: 10,000
- Parsed Lines: 9,955
- Critical Issues: 0
- Errors: 0  
- Warnings: 133
- Time Range: 2025-07-26 14:34:47 to 2025-07-26 21:39:42

🔧 Component Analysis:
- Anti Malware: 391 entries, 43 warnings (Device Control metrics issue)
- Connection Handler: 3,511 entries, 0 errors
- Application Control: 3,029 entries, 0 errors

🔍 Known Issues Detected:
- AMSP_FUNC_NOT_SUPPORT: Device Control adapter metrics function not supported
  Resolution: Expected if Device Control is not enabled or supported
  Impact: Low - Metrics collection only

💡 Recommendations:
- ⚠️ Recurring issue 'AMSP_FUNC_NOT_SUPPORT' (43 occurrences)
- Consider reviewing Device Control configuration
```

## Common Issues Detected

### Device Control Metrics (AMSP_FUNC_NOT_SUPPORT)
- **Description**: Device Control adapter metrics function not supported
- **Severity**: Warning
- **Resolution**: Expected if Device Control is not enabled
- **Impact**: Low - affects metrics collection only

### File Access Issues
- **Description**: Unable to open log files
- **Severity**: Error
- **Resolution**: Check file permissions and paths
- **Impact**: Medium - may affect monitoring

### Connection Problems
- **Description**: Manager communication issues
- **Severity**: Critical
- **Resolution**: Check network connectivity and firewall rules
- **Impact**: High - affects agent functionality

## Log Format Support

The analyzer supports standard Deep Security Agent log format:
```
YYYY-MM-DD HH:MM:SS.ssssss [timezone]: [component/level] | message | location | thread
```

Example:
```
2025-07-26 14:34:47.505346 [+0100]: [Cmd/5] | Received command GetEvents | dsa/ConnectionHandler.lua:1577:LogDsmCommand | 480C:27DC:dsa.Scheduler_0006
```

## Performance

- Processes up to 10,000 log lines for performance optimization
- Efficient parsing with regex-based pattern matching
- Real-time analysis with progress indication
- Secure temporary file handling

## Security Considerations

- All uploads are validated for file type and size
- Temporary files are securely created and cleaned up
- Host access validation prevents unauthorized usage
- No sensitive data is logged or exposed

## Troubleshooting

### Common Issues:

1. **Import errors**: Ensure all required files are in the same directory
2. **API errors**: Verify OpenAI API key and endpoint configuration
3. **File upload errors**: Check file size (max 16MB) and format (.log, .txt)
4. **Parse errors**: Ensure log file is in standard DS agent format

### Debug Mode:
Set `FLASK_DEBUG=True` in `.env` for detailed error messages.

## Support

For issues and feature requests, consult the Trend Micro Deep Security documentation or contact your system administrator.

## Version Information

- **Version**: 1.0
- **Compatible with**: Deep Security 20.x agent logs
- **Platform**: Windows, Linux, macOS
- **Python**: 3.9+
