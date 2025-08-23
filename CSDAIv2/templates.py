"""
HTML Templates Module
Contains the main HTML template for the Deep Security Unified Analyzer.
"""

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Trend Micro Deep Security Unified Analyzer</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css" integrity="sha512-z3gLpd7yknf1YoNbCzqRKc4qyor8gaKU1qmn+CShxbuBusANI9QpRohGBreCFkKxLhei6S9CQXFEbbKuqLg0DA==" crossorigin="anonymous" referrerpolicy="no-referrer">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;550;600;650;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/static/css/progress-bar.css">
  <style>
    /* Enhanced CSS with wizard styles */
    :root {
      --bg-gradient-start: #667eea;
      --bg-gradient-end: #764ba2;
      --header-bg: #fff;
      --header-border: #e3e3e3;
      --header-shadow: rgba(0,0,0,0.03);
      --card-bg: #fff;
      --text-primary: #222;
      --text-muted: #666;
      --text-secondary: #495057;
      --border-color: #e9ecef;
      --wizard-active: #667eea;
      --wizard-complete: #28a745;
      --wizard-inactive: #6c757d;
      --step-bg: #f8f9fa;
    }

    [data-theme="dark"] {
      --bg-gradient-start: #1a1a2e;
      --bg-gradient-end: #16213e;
      --header-bg: #2d3748;
      --header-border: #4a5568;
      --header-shadow: rgba(0,0,0,0.2);
      --card-bg: #2d3748;
      --text-primary: #e2e8f0;
      --text-muted: #a0aec0;
      --text-secondary: #cbd5e0;
      --border-color: #4a5568;
      --step-bg: #374151;
    }

    body {
      font-family: 'Inter', 'Segoe UI', 'Roboto', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
      font-weight: 400;
      line-height: 1.6;
      letter-spacing: 0.01em;
      background: linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
      min-height: 100vh;
      color: var(--text-primary);
      transition: all 0.3s ease;
    }

    /* Typography improvements for better readability */
    h1, h2, h3, h4, h5, h6 {
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
      font-weight: 600;
      line-height: 1.3;
      letter-spacing: -0.01em;
      margin-bottom: 1rem;
    }

    h1 { font-size: 2.5rem; font-weight: 700; }
    h2 { font-size: 2rem; font-weight: 650; }
    h3 { font-size: 1.75rem; font-weight: 600; }
    h4 { font-size: 1.5rem; font-weight: 600; }
    h5 { font-size: 1.25rem; font-weight: 550; }
    h6 { font-size: 1.1rem; font-weight: 550; }

    p, .text, .content {
      font-size: 1rem;
      line-height: 1.7;
      margin-bottom: 1rem;
    }

    .small-text {
      font-size: 0.875rem;
      line-height: 1.5;
    }

    /* Better text rendering */
    * {
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      text-rendering: optimizeLegibility;
    }

    /* Force font inheritance for all content including dynamically generated */
    .results-content, .results-content *, 
    .upload-card *, .step-content *,
    .detailed-results *, .analysis-content * {
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
    }

    /* Universal font override to ensure consistency everywhere */
    body, body *, html, html *,
    .container *, .row *, .col *, .card *, .btn *,
    h1, h2, h3, h4, h5, h6, p, span, div, li, td, th,
    .table *, .alert *, .form-control *, .navbar * {
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
    }

    /* Exception for Font Awesome icons - preserve icon fonts */
    .fa, .fas, .far, .fal, .fab, .fa-solid, .fa-regular, .fa-light, .fa-brands,
    i[class*="fa-"], span[class*="fa-"], 
    .fa::before, .fas::before, .far::before, .fal::before, .fab::before,
    .fa-solid::before, .fa-regular::before, .fa-light::before, .fa-brands::before {
      font-family: "Font Awesome 6 Free", "Font Awesome 6 Pro", "Font Awesome 6 Brands", "FontAwesome" !important;
      font-weight: 900 !important;
    }

    /* Extremely specific override for generated analysis content */
    .results-content *, .results-content h1, .results-content h2, .results-content h3,
    .results-content h4, .results-content h5, .results-content h6, .results-content p,
    .results-content div, .results-content span, .results-content li, .results-content ul,
    .results-content ol, .results-content table, .results-content td, .results-content th,
    .results-content tr, .results-content thead, .results-content tbody, .results-content strong,
    .results-content b, .results-content i, .results-content em, .results-content small,
    .results-content .card, .results-content .card-header, .results-content .card-body,
    .results-content .table, .results-content .row, .results-content .col,
    .results-content .mb-1, .results-content .mb-2, .results-content .mb-3, .results-content .mb-4 {
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
    }

    /* Nuclear option - force font on absolutely everything inside results */
    .results-content * {
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
    }

    .analysis-content * {
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
    }

    .font-consistent * {
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
    }

    /* Font Awesome icon exceptions - override our font rules */
    .results-content .fa, .results-content .fas, .results-content .far, .results-content .fal, .results-content .fab,
    .results-content .fa-solid, .results-content .fa-regular, .results-content .fa-light, .results-content .fa-brands,
    .results-content i[class*="fa-"], .results-content span[class*="fa-"],
    .analysis-content .fa, .analysis-content .fas, .analysis-content .far, .analysis-content .fal, .analysis-content .fab,
    .analysis-content .fa-solid, .analysis-content .fa-regular, .analysis-content .fa-light, .analysis-content .fa-brands,
    .analysis-content i[class*="fa-"], .analysis-content span[class*="fa-"],
    .font-consistent .fa, .font-consistent .fas, .font-consistent .far, .font-consistent .fal, .font-consistent .fab,
    .font-consistent .fa-solid, .font-consistent .fa-regular, .font-consistent .fa-light, .font-consistent .fa-brands,
    .font-consistent i[class*="fa-"], .font-consistent span[class*="fa-"] {
      font-family: "Font Awesome 6 Free", "Font Awesome 6 Pro", "Font Awesome 6 Brands", "FontAwesome" !important;
      font-weight: 900 !important;
    }

    /* Override any possible inline styles */
    *[style*="font-family"] {
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
    }

    /* Exception for Font Awesome inline styles */
    i[class*="fa-"][style*="font-family"], span[class*="fa-"][style*="font-family"],
    .fa[style*="font-family"], .fas[style*="font-family"], .far[style*="font-family"], 
    .fal[style*="font-family"], .fab[style*="font-family"] {
      font-family: "Font Awesome 6 Free", "Font Awesome 6 Pro", "Font Awesome 6 Brands", "FontAwesome" !important;
    }

    /* Font consistency across all pages and wizard steps */
    .upload-card, .wizard-progress, .step-content, .step-indicator,
    .step-label, .summary-card, .results-summary, .detailed-results,
    .analysis-type-card, .config-section, .alert, .form-label,
    .form-check-label, .btn, .card, .card-header, .card-body,
    .progress-status, .dynamic-progress-container {
      font-family: 'Inter', 'Segoe UI', 'Roboto', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif !important;
    }

    /* Ensure all text elements use consistent font */
    .upload-card h1, .upload-card h2, .upload-card h3, .upload-card h4, .upload-card h5, .upload-card h6,
    .step-content h1, .step-content h2, .step-content h3, .step-content h4, .step-content h5, .step-content h6,
    .wizard-progress h1, .wizard-progress h2, .wizard-progress h3, .wizard-progress h4, .wizard-progress h5, .wizard-progress h6 {
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
      font-weight: 600 !important;
      line-height: 1.3 !important;
      letter-spacing: -0.01em !important;
    }

    /* Consistent paragraph and text styling across wizard */
    .upload-card p, .step-content p, .wizard-progress p,
    .upload-card .text-muted, .step-content .text-muted, .wizard-progress .text-muted,
    .upload-card .small, .step-content .small, .wizard-progress .small {
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
      line-height: 1.6 !important;
    }

    /* Button and form element font consistency */
    .btn, button, input, select, textarea, .form-control, .form-select {
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
      font-weight: 500 !important;
    }

    /* Alert and status message consistency */
    .alert, .status-message, .progress-label, .error-message {
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
    }

    /* Improved monospace/code styling */
    .monospace, code, pre, .log-entry {
      font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
      font-size: 0.9em;
      line-height: 1.5;
      letter-spacing: 0.02em;
      font-feature-settings: "liga" 1, "calt" 1;
    }

    /* Enhanced log entry styling for results */
    .results-content .log-entry {
      background: var(--step-bg);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 1rem;
      margin-bottom: 1rem;
      font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
      font-size: 0.85rem;
      line-height: 1.6;
      color: var(--text-primary);
      overflow-x: auto;
      white-space: pre-wrap;
      word-break: break-word;
    }

    .results-content .bg-light {
      background: var(--step-bg) !important;
      border: 1px solid var(--border-color);
    }

    .main-header {
      background: var(--header-bg);
      border-bottom: 1px solid var(--header-border);
      padding: 20px 0;
      margin-bottom: 40px;
      box-shadow: 0 2px 8px var(--header-shadow);
      transition: all 0.3s ease;
    }

    .main-header .logo {
      font-size: 1.8rem;
      font-weight: 700;
      color: #667eea;
      letter-spacing: 1px;
      display: flex;
      align-items: center;
      gap: 12px;
    }

    /* Wizard Progress Bar */
    .wizard-progress {
      background: var(--card-bg);
      border-radius: 15px;
      padding: 25px;
      margin-bottom: 30px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    .progress-container {
      position: relative;
      margin-bottom: 20px;
    }

    .progress-bar-custom {
      height: 8px;
      background: #e9ecef;
      border-radius: 4px;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--wizard-active), var(--wizard-complete));
      border-radius: 4px;
      transition: width 0.3s ease;
    }

    .step-indicators {
      display: flex;
      justify-content: space-between;
      margin-top: 15px;
      position: relative;
    }

    .step-indicator {
      display: flex;
      flex-direction: column;
      align-items: center;
      position: relative;
      flex: 1;
    }

    .step-circle {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: var(--wizard-inactive);
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      font-size: 14px;
      transition: all 0.3s ease;
    }

    .step-circle.active {
      background: var(--wizard-active);
      transform: scale(1.1);
    }

    .step-circle.completed {
      background: var(--wizard-complete);
    }

    .step-label {
      margin-top: 8px;
      font-size: 12px;
      font-weight: 500;
      text-align: center;
      color: var(--text-muted);
      max-width: 100px;
    }

    .step-label.active {
      color: var(--wizard-active);
      font-weight: 600;
    }

    .step-label.completed {
      color: var(--wizard-complete);
    }

    /* Analysis Type Cards */
    .analysis-type-card {
      border: 2px solid var(--border-color);
      border-radius: 12px;
      padding: 25px;
      margin-bottom: 20px;
      cursor: pointer;
      transition: all 0.3s ease;
      background: var(--card-bg);
      position: relative;
    }

    .analysis-type-card:hover {
      border-color: var(--wizard-active);
      box-shadow: 0 8px 25px rgba(102,126,234,0.15);
      transform: translateY(-2px);
    }

    .analysis-type-card.selected {
      border-color: var(--wizard-active);
      background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(102,126,234,0.05));
    }

    .analysis-type-card.selected::before {
      content: '✓';
      position: absolute;
      top: 15px;
      right: 15px;
      background: var(--wizard-active);
      color: white;
      width: 25px;
      height: 25px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      font-weight: bold;
    }

    .analysis-icon {
      font-size: 3rem;
      margin-bottom: 15px;
      color: var(--wizard-active);
    }

    .analysis-title {
      font-size: 1.4rem;
      font-weight: 600;
      margin-bottom: 10px;
      color: var(--text-primary);
    }

    .analysis-desc {
      color: var(--text-muted);
      margin-bottom: 15px;
      line-height: 1.5;
    }

    .file-requirements {
      background: var(--step-bg);
      border-left: 4px solid var(--wizard-active);
      padding: 12px;
      border-radius: 0 8px 8px 0;
      font-size: 0.9rem;
    }

    /* Drag and Drop Enhanced */
    .drag-drop-area {
      border: 3px dashed var(--wizard-active);
      border-radius: 16px;
      padding: 60px 20px;
      text-align: center;
      background: var(--step-bg);
      transition: all 0.3s ease;
      cursor: pointer;
      position: relative;
      overflow: hidden;
      min-height: 250px;
    }

    .drag-drop-area:hover {
      border-color: var(--wizard-complete);
      background: rgba(40, 167, 69, 0.1);
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(102,126,234,0.15);
    }

    .drag-drop-area.drag-over {
      border-color: var(--wizard-complete);
      background: rgba(40, 167, 69, 0.15);
      border-style: solid;
    }

    .file-list {
      margin-top: 20px;
      text-align: left;
    }

    .file-item {
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 12px 15px;
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .file-info {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .file-icon {
      font-size: 1.2rem;
      color: var(--wizard-active);
    }

    .file-name {
      font-weight: 500;
      color: var(--text-primary);
    }

    .file-size {
      font-size: 0.85rem;
      color: var(--text-muted);
    }

    /* Configuration Panel */
    .config-section {
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 20px;
    }

    .config-title {
      font-size: 1.1rem;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 15px;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .config-option {
      margin-bottom: 12px;
    }

    .config-option label {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      color: var(--text-primary);
    }

    /* Buttons */
    .btn-primary {
      background: var(--wizard-active);
      border-color: var(--wizard-active);
      padding: 12px 30px;
      font-weight: 600;
      border-radius: 8px;
      transition: all 0.3s ease;
    }

    .btn-primary:hover {
      background: #5a6fd8;
      border-color: #5a6fd8;
      transform: translateY(-1px);
    }

    .btn-outline-primary {
      border-color: var(--wizard-active);
      color: var(--wizard-active);
      font-weight: 600;
    }

    .btn-outline-primary:hover {
      background-color: var(--wizard-active);
      border-color: var(--wizard-active);
    }

    /* Navigation Buttons */
    .wizard-navigation {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 30px;
      padding-top: 20px;
      border-top: 1px solid var(--border-color);
    }

    /* Processing Animation */
    .processing-animation {
      text-align: center;
      padding: 40px;
    }

    .spinner-custom {
      width: 60px;
      height: 60px;
      border: 4px solid var(--border-color);
      border-top: 4px solid var(--wizard-active);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 20px;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .processing-status {
      font-size: 1.1rem;
      color: var(--text-primary);
      margin-bottom: 10px;
    }

    .processing-substatus {
      color: var(--text-muted);
      font-size: 0.9rem;
    }

    /* Results Enhancement */
    .results-header {
      display: flex;
      justify-content: between;
      align-items: center;
      margin-bottom: 25px;
      padding: 20px;
      background: var(--card-bg);
      border-radius: 10px;
      border: 1px solid var(--border-color);
    }

    .results-title {
      font-size: 1.8rem;
      font-weight: 700;
      color: var(--text-primary);
    }

    .results-meta {
      color: var(--text-muted);
      font-size: 0.9rem;
    }

    /* Detailed Results Styling */
    .detailed-results {
      background: var(--card-bg);
      border-radius: 15px;
      padding: 30px;
      box-shadow: 0 8px 30px rgba(102,126,234,0.08);
      border: 1px solid var(--border-color);
      margin-bottom: 30px;
    }

    .detailed-results h5 {
      color: var(--text-primary);
      font-weight: 700;
      margin-bottom: 25px;
      padding-bottom: 15px;
      border-bottom: 2px solid var(--border-color);
    }

    .results-content {
      color: var(--text-primary);
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
      line-height: 1.7;
      font-size: 1rem;
    }

    /* Enhanced typography for analysis results */
    .results-content h1, .results-content h2, .results-content h3, 
    .results-content h4, .results-content h5, .results-content h6 {
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
      font-weight: 600;
      line-height: 1.4;
      margin-top: 2rem;
      margin-bottom: 1rem;
      letter-spacing: -0.01em;
    }

    .results-content h1 { font-size: 2rem; font-weight: 700; }
    .results-content h2 { font-size: 1.75rem; font-weight: 650; }
    .results-content h3 { font-size: 1.5rem; font-weight: 600; }
    .results-content h4 { font-size: 1.25rem; font-weight: 600; }
    .results-content h5 { font-size: 1.125rem; font-weight: 550; }
    .results-content h6 { font-size: 1rem; font-weight: 550; }

    /* Improved paragraph and text spacing */
    .results-content p {
      margin-bottom: 1.2rem;
      line-height: 1.7;
    }

    /* Better list styling */
    .results-content ul, .results-content ol {
      margin-bottom: 1.5rem;
      padding-left: 1.8rem;
    }

    .results-content li {
      margin-bottom: 0.6rem;
      line-height: 1.6;
    }

    /* Enhanced section headers with icons */
    .results-content .card-header {
      background: linear-gradient(135deg, var(--wizard-active) 0%, #5a6fd8 100%);
      color: white;
      font-weight: 600;
      font-size: 1.1rem;
      border-radius: 10px 10px 0 0 !important;
      border: none;
      padding: 1rem 1.5rem;
      letter-spacing: 0.02em;
    }

    /* Improved content readability */
    .results-content .card-body {
      color: var(--text-primary);
      padding: 1.5rem;
      font-size: 0.95rem;
      line-height: 1.6;
    }

    /* Better emphasis styling */
    .results-content strong, .results-content b {
      font-weight: 600;
      color: var(--text-primary);
    }

    /* Section header styling for analysis results */
    .results-content .card-header .fas,
    .results-content .card-header .fa-solid {
      margin-right: 0.75rem;
      font-size: 1.1em;
    }

    /* Alert and callout styling improvements */
    .results-content .alert {
      border-radius: 10px;
      border: none;
      padding: 1.25rem;
      margin-bottom: 1.5rem;
      font-size: 0.95rem;
      line-height: 1.6;
    }

    .results-content .alert-success {
      background: linear-gradient(135deg, #d4edda 0%, #c8e6c9 100%);
      color: #155724;
      border-left: 4px solid #28a745;
    }

    .results-content .alert-warning {
      background: linear-gradient(135deg, #fff3cd 0%, #ffe9a5 100%);
      color: #856404;
      border-left: 4px solid #ffc107;
    }

    .results-content .alert-danger {
      background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
      color: #721c24;
      border-left: 4px solid #dc3545;
    }

    .results-content .alert-info {
      background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
      color: #0c5460;
      border-left: 4px solid #17a2b8;
    }

    /* Improved spacing for different content types */
    .results-content .mb-1 {
      margin-bottom: 0.75rem !important;
    }

    .results-content .mb-2 {
      margin-bottom: 1rem !important;
    }

    /* Comprehensive analysis content font styling */
    .results-content, .results-content * {
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
    }

    .results-content h1, .results-content h2, .results-content h3, 
    .results-content h4, .results-content h5, .results-content h6 {
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
      font-weight: 600 !important;
      line-height: 1.3 !important;
    }

    .results-content p, .results-content li, .results-content span,
    .results-content div, .results-content td, .results-content th {
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
      line-height: 1.6 !important;
    }

    /* Override any inline or default font styling */
    .results-content .card h4, .results-content .card h5, .results-content .card h6 {
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
      font-weight: 600 !important;
    }

    .results-content .card-header {
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
      font-weight: 600 !important;
    }

    .results-content .card-body {
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
    }

    /* Status and summary text */
    .results-content strong, .results-content b {
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
      font-weight: 600 !important;
    }

    /* Maximum font override for analysis content */
    .font-consistent, .font-consistent *,
    .analysis-content, .analysis-content *,
    .font-consistent h1, .font-consistent h2, .font-consistent h3, 
    .font-consistent h4, .font-consistent h5, .font-consistent h6,
    .font-consistent p, .font-consistent span, .font-consistent div,
    .font-consistent li, .font-consistent td, .font-consistent th,
    .font-consistent strong, .font-consistent b, .font-consistent i,
    .font-consistent .card, .font-consistent .card-header, .font-consistent .card-body {
      font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
    }

    .results-content .card {
      background: var(--step-bg);
      border: 1px solid var(--border-color);
      margin-bottom: 20px;
      border-radius: 10px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .results-content .card-header {
      background: var(--wizard-active);
      color: white;
      font-weight: 600;
      border-radius: 10px 10px 0 0 !important;
      border: none;
    }

    .results-content .card-body {
      color: var(--text-primary);
      padding: 20px;
    }

    .results-content .table {
      color: var(--text-primary);
      margin-bottom: 0;
    }

    .results-content .table th {
      background: var(--step-bg);
      color: var(--text-primary);
      font-weight: 600;
      border-color: var(--border-color);
    }

    .results-content .table td {
      border-color: var(--border-color);
    }

    .results-content .text-danger {
      color: #dc3545 !important;
    }

    .results-content .text-warning {
      color: #ffc107 !important;
    }

    .results-content .text-success {
      color: #28a745 !important;
    }

    .results-preview {
      background: var(--step-bg);
      border-radius: 10px;
      padding: 20px;
      border: 1px solid var(--border-color);
    }

    .results-preview h5 {
      color: var(--text-primary);
      font-weight: 600;
    }

    /* Mobile Responsive */
    @media (max-width: 768px) {
      .step-indicators {
        flex-wrap: wrap;
        gap: 10px;
      }
      
      .step-indicator {
        flex: 0 0 calc(50% - 5px);
      }
      
      .analysis-type-card {
        padding: 20px;
      }
      
      .wizard-navigation {
        flex-direction: column;
        gap: 15px;
      }
    }

    /* Theme Toggle */
    .theme-toggle {
      position: absolute;
      right: 30px;
      top: 50%;
      transform: translateY(-50%);
      background: none;
      border: 2px solid var(--border-color);
      border-radius: 50px;
      width: 60px;
      height: 32px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s ease;
    }

    .theme-toggle:hover {
      border-color: var(--wizard-active);
      transform: translateY(-50%) scale(1.05);
    }

    .theme-toggle i {
      font-size: 16px;
      color: var(--text-primary);
    }

    [data-theme="dark"] .theme-toggle i.fa-sun {
      display: none;
    }

    [data-theme="light"] .theme-toggle i.fa-moon,
    :root .theme-toggle i.fa-moon {
      display: none;
    }

    [data-theme="dark"] .theme-toggle i.fa-moon {
      display: inline-block;
    }

    /* Session History */
    .session-card {
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 15px;
      transition: all 0.3s ease;
    }

    .session-card:hover {
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      transform: translateY(-1px);
    }

    .session-status {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: 500;
    }

    .session-status.completed {
      background: rgba(40, 167, 69, 0.1);
      color: var(--wizard-complete);
    }

    .session-status.processing {
      background: rgba(255, 193, 7, 0.1);
      color: #ffc107;
    }

    .session-status.error {
      background: rgba(220, 53, 69, 0.1);
      color: #dc3545;
    }

    /* Enhanced form controls */
    .form-control, .form-select {
      border-radius: 8px;
      border: 1px solid var(--border-color);
      background: var(--card-bg);
      color: var(--text-primary);
      transition: all 0.3s ease;
    }

    .form-control:focus, .form-select:focus {
      border-color: var(--wizard-active);
      box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
      background: var(--card-bg);
      color: var(--text-primary);
    }

    .form-check-input:checked {
      background-color: var(--wizard-active);
      border-color: var(--wizard-active);
    }

    /* Error and Success Messages */
    .alert {
      border-radius: 10px;
      border: none;
      padding: 15px 20px;
    }

    .alert-danger {
      background: rgba(220, 53, 69, 0.1);
      color: #dc3545;
      border-left: 4px solid #dc3545;
    }

    .alert-success {
      background: rgba(40, 167, 69, 0.1);
      color: var(--wizard-complete);
      border-left: 4px solid var(--wizard-complete);
    }

    .alert-info {
      background: rgba(102, 126, 234, 0.1);
      color: var(--wizard-active);
      border-left: 4px solid var(--wizard-active);
    }

    /* Additional styles for improved UI */
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      color: var(--text-primary);
    }

    .card-header {
      background: var(--step-bg);
      border-bottom: 1px solid var(--border-color);
      color: var(--text-primary);
    }

    .table {
      color: var(--text-primary);
    }

    .table-striped > tbody > tr:nth-of-type(odd) > td {
      background-color: var(--step-bg);
    }

    .badge {
      color: white;
    }

    .bg-secondary {
      background-color: var(--wizard-inactive) !important;
    }

    .bg-warning {
      background-color: #ffc107 !important;
    }

    .bg-danger {
      background-color: #dc3545 !important;
    }

    .bg-success {
      background-color: var(--wizard-complete) !important;
    }

    .bg-info {
      background-color: var(--wizard-active) !important;
    }

    .bg-primary {
      background-color: var(--wizard-active) !important;
    }

    .text-danger {
      color: #dc3545 !important;
    }

    .text-warning {
      color: #ffc107 !important;
    }

    .text-success {
      color: var(--wizard-complete) !important;
    }

    .text-info {
      color: var(--wizard-active) !important;
    }

    .text-primary {
      color: var(--wizard-active) !important;
    }

    .text-muted {
      color: var(--text-muted) !important;
    }

    .text-secondary {
      color: var(--text-secondary) !important;
    }

    .border-primary {
      border-color: var(--wizard-active) !important;
    }

    .border-danger {
      border-color: #dc3545 !important;
    }

    .border-warning {
      border-color: #ffc107 !important;
    }

    .border-success {
      border-color: var(--wizard-complete) !important;
    }

    .border-info {
      border-color: var(--wizard-active) !important;
    }

    /* Ensure Font Awesome icons display correctly */
    .fa, .fas, .far, .fal, .fab, .fa-solid, .fa-regular, .fa-light, .fa-brands {
      font-family: "Font Awesome 6 Free", "Font Awesome 6 Pro", "Font Awesome 6 Brands", "FontAwesome" !important;
      font-weight: 900 !important;
      font-style: normal !important;
      font-variant: normal !important;
      text-transform: none !important;
      line-height: 1 !important;
      -webkit-font-smoothing: antialiased !important;
      -moz-osx-font-smoothing: grayscale !important;
      display: inline-block !important;
    }

    .fa-brands {
      font-weight: 400 !important;
    }

    .fa-regular {
      font-weight: 400 !important;
    }
  </style>
</head>
<body>
  <header class="main-header">
    <div class="container-fluid d-flex align-items-center justify-content-center position-relative">
      <span class="logo">
        <i class="fa-solid fa-shield-alt"></i>
        Deep Security Unified Analyzer
      </span>
      <button class="theme-toggle" id="theme-toggle" title="Toggle Dark Mode">
        <i class="fa-solid fa-sun"></i>
        <i class="fa-solid fa-moon"></i>
      </button>
    </div>
  </header>

  <div class="container-fluid">
    {{ content | safe }}
  </div>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
  <script src="/static/js/progress-bar.js"></script>
<script>
    // Theme management
    function initializeTheme() {
      const savedTheme = localStorage.getItem('theme') || 'light';
      setTheme(savedTheme);
    }

    function setTheme(theme) {
      document.documentElement.setAttribute('data-theme', theme);
      localStorage.setItem('theme', theme);
    }

    function toggleTheme() {
      const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
      const newTheme = currentTheme === 'light' ? 'dark' : 'light';
      setTheme(newTheme);
    }

    // Initialize theme
    document.addEventListener('DOMContentLoaded', function() {
      initializeTheme();
      
      const themeToggle = document.getElementById('theme-toggle');
      if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
      }
    });
  </script>
</body>
</html>
"""
