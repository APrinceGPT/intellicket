# Wizard Step Templates for CSDAI Unified Analyzer
# Content-only templates designed to be embedded within the main HTML template

# Step 1: Analysis Type Selection
WIZARD_STEP_1_TEMPLATE = """
<div class="upload-card" style="max-width: 1200px; margin: 0 auto; border-radius: 22px; box-shadow: 0 12px 40px rgba(102,126,234,0.10); background: var(--card-bg); padding: 48px;">
  
  <!-- Wizard Progress -->
  <div class="wizard-progress">
    <div class="progress-container">
      <div class="progress-bar-custom">
        <div class="progress-fill" style="width: {{ progress_percentage }}%;"></div>
      </div>
    </div>
    <div class="step-indicators">
      {% for step_num, step_data in wizard_steps.items() %}
      <div class="step-indicator">
        <div class="step-circle {{ "active" if step_num == current_step else 'completed' if step_num < current_step else '' }}">
          {% if step_num < current_step %}
            <i class="fa-solid fa-check"></i>
          {% else %}
            {{ step_num }}
          {% endif %}
        </div>
        <div class="step-label {{ "active" if step_num == current_step else 'completed' if step_num < current_step else '' }}">
          {{ step_data.name }}
        </div>
      </div>
      {% endfor %}
    </div>
  </div>

  <!-- Step Content -->
  <div class="step-content">
    <h2 class="text-center mb-4">Choose Your Analysis Type</h2>
    <p class="text-center text-muted mb-5">
      Select the type of Deep Security analysis you want to perform
    </p>

    {% if error %}
    <div class="alert alert-danger">
      <i class="fa-solid fa-exclamation-triangle me-2"></i>{{ error }}
    </div>
    {% endif %}

    <form method="post" id="step1-form">
      <div class="row">
        <div class="col-md-6 col-lg-3 mb-4">
          <div class="analysis-type-card" data-type="ds_logs">
            <div class="text-center">
              <i class="fa-solid fa-file-lines analysis-icon"></i>
              <h5 class="analysis-title">DS Agent Logs</h5>
              <p class="analysis-desc">Analyze ds_agent.log files for errors, warnings, and performance issues with AI-enhanced insights</p>
              <div class="file-requirements">
                <strong>Required:</strong> ds_agent.log files<br>
                <small class="text-muted">Single or multiple log files</small>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-6 col-lg-3 mb-4">
          <div class="analysis-type-card" data-type="amsp_logs">
            <div class="text-center">
              <i class="fa-solid fa-shield-virus analysis-icon"></i>
              <h5 class="analysis-title">AMSP Anti-Malware</h5>
              <p class="analysis-desc">Analyze AMSP installation and debug logs with expert knowledge correlation</p>
              <div class="file-requirements">
                <strong>Required:</strong> AMSP-Inst_LocalDebugLog files<br>
                <small class="text-muted">Installation and runtime logs</small>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-6 col-lg-3 mb-4">
          <div class="analysis-type-card" data-type="av_conflicts">
            <div class="text-center">
              <i class="fa-solid fa-exclamation-triangle analysis-icon"></i>
              <h5 class="analysis-title">AV Conflicts</h5>
              <p class="analysis-desc">Detect conflicting antivirus software that may interfere with Deep Security</p>
              <div class="file-requirements">
                <strong>Required:</strong> RunningProcess.xml<br>
                <small class="text-muted">Process list export</small>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-6 col-lg-3 mb-4">
          <div class="analysis-type-card" data-type="resource_analysis">
            <div class="text-center">
              <i class="fa-solid fa-chart-line analysis-icon"></i>
              <h5 class="analysis-title">Resource Analysis</h5>
              <p class="analysis-desc">Analyze system performance and recommend scan exclusions for optimization</p>
              <div class="file-requirements">
                <strong>Required:</strong> RunningProcess.xml + TopNBusyProcess.txt<br>
                <small class="text-muted">Process list and performance data</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <input type="hidden" name="analysis_type" id="selected-analysis-type">
      
      <div class="text-center mt-4">
        <button type="submit" class="btn btn-primary btn-lg" id="continue-btn" disabled>
          <i class="fa-solid fa-arrow-right me-2"></i>Continue to Upload
        </button>
      </div>
    </form>
  </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const analysisCards = document.querySelectorAll('.analysis-type-card');
    const continueBtn = document.getElementById('continue-btn');
    const selectedInput = document.getElementById('selected-analysis-type');
    
    analysisCards.forEach(card => {
        card.addEventListener('click', function() {
            // Remove selected class from all cards
            analysisCards.forEach(c => c.classList.remove('selected'));
            
            // Add selected class to clicked card
            this.classList.add('selected');
            
            // Update hidden input
            const analysisType = this.getAttribute('data-type');
            selectedInput.value = analysisType;
            
            // Enable continue button
            continueBtn.disabled = false;
        });
    });
});
</script>
"""

# Step 2: File Upload
WIZARD_STEP_2_TEMPLATE = """
<div class="upload-card" style="max-width: 1000px; margin: 0 auto; border-radius: 22px; box-shadow: 0 12px 40px rgba(102,126,234,0.10); background: var(--card-bg); padding: 48px;">
  
  <!-- Wizard Progress -->
  <div class="wizard-progress">
    <div class="progress-container">
      <div class="progress-bar-custom">
        <div class="progress-fill" style="width: {{ progress_percentage }}%;"></div>
      </div>
    </div>
    <div class="step-indicators">
      {% for step_num, step_data in wizard_steps.items() %}
      <div class="step-indicator">
        <div class="step-circle {{ "active" if step_num == current_step else 'completed' if step_num < current_step else '' }}">
          {% if step_num < current_step %}
            <i class="fa-solid fa-check"></i>
          {% else %}
            {{ step_num }}
          {% endif %}
        </div>
        <div class="step-label {{ "active" if step_num == current_step else 'completed' if step_num < current_step else '' }}">
          {{ step_data.name }}
        </div>
      </div>
      {% endfor %}
    </div>
  </div>

  <!-- Step Content -->
  <div class="step-content">
    <h2 class="text-center mb-4">Upload Your Files</h2>
    <p class="text-center text-muted mb-5">
      {% if session_data.analysis_type %}
        Upload files for {{ session_data.analysis_type.replace('_', ' ').title() }} analysis
      {% else %}
        Upload your analysis files
      {% endif %}
    </p>

    {% if error %}
    <div class="alert alert-danger">
      <i class="fa-solid fa-exclamation-triangle me-2"></i>{{ error }}
    </div>
    {% endif %}

    <!-- File Requirements -->
    {% if analysis_guidance %}
    <div class="alert alert-info mb-4">
      <h6><i class="fa-solid fa-info-circle me-2"></i>File Requirements:</h6>
      <p class="mb-0">{{ analysis_guidance.description }}</p>
      {% if analysis_guidance.file_types %}
      <small class="text-muted">Supported files: {{ analysis_guidance.file_types | join(', ') }}</small>
      {% endif %}
    </div>
    {% endif %}

    <form method="post" enctype="multipart/form-data" id="upload-form">
      <!-- File Drop Zone -->
      <div class="file-drop-zone" id="file-drop-zone">
        <div class="text-center">
          <i class="fa-solid fa-cloud-upload-alt upload-icon"></i>
          <h5 class="mt-3 mb-2">Drag & Drop Files Here</h5>
          <p class="text-muted mb-3">or click to browse files</p>
          <input type="file" multiple name="files" id="file-input" class="d-none" accept=".log,.xml,.txt,.csv,.json">
          <button type="button" class="btn btn-outline-primary" onclick=\"document.getElementById('file-input').click()\">
            <i class="fa-solid fa-folder-open me-2"></i>Browse Files
          </button>
        </div>
      </div>

      <!-- Selected Files -->
      <div id="selected-files" class="mt-4" style="display: none;">
        <h6><i class="fa-solid fa-files me-2"></i>Selected Files:</h6>
        <div id="file-list" class="file-list"></div>
      </div>

      <!-- Navigation -->
      <div class="d-flex justify-content-between mt-5">
        <a href="/wizard/1" class="btn btn-outline-secondary">
          <i class="fa-solid fa-arrow-left me-2"></i>Back
        </a>
        <button type="submit" class="btn btn-primary" id="upload-btn" disabled>
          <i class="fa-solid fa-arrow-right me-2"></i>Continue to Configuration
        </button>
      </div>
    </form>
  </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file-input');
    const dropZone = document.getElementById('file-drop-zone');
    const selectedFiles = document.getElementById('selected-files');
    const fileList = document.getElementById('file-list');
    const uploadBtn = document.getElementById('upload-btn');
    
    let files = [];
    
    // File input change
    fileInput.addEventListener('change', function(e) {
        handleFiles(e.target.files);
    });
    
    // Drag and drop
    dropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });
    
    dropZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
    });
    
    dropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        handleFiles(e.dataTransfer.files);
    });
    
    function handleFiles(fileList) {
        files = Array.from(fileList);
        updateFileDisplay();
        updateUploadButton();
    }
    
    function updateFileDisplay() {
        if (files.length > 0) {
            selectedFiles.style.display = 'block';
            fileList.innerHTML = files.map((file, index) => `
                <div class="file-item d-flex justify-content-between align-items-center p-2 border rounded mb-2">
                    <div>
                        <i class="fa-solid fa-file me-2"></i>
                        <span>${file.name}</span>
                        <small class="text-muted">(${(file.size / 1024).toFixed(1)} KB)</small>
                    </div>
                    <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeFile(${index})">
                        <i class="fa-solid fa-times"></i>
                    </button>
                </div>
            `).join('');
        } else {
            selectedFiles.style.display = 'none';
        }
    }
    
    function updateUploadButton() {
        uploadBtn.disabled = files.length === 0;
    }
    
    window.removeFile = function(index) {
        files.splice(index, 1);
        updateFileDisplay();
        updateUploadButton();
    };
});
</script>
"""

# Step 3: Configuration
WIZARD_STEP_3_TEMPLATE = """
<div class="upload-card" style="max-width: 1000px; margin: 0 auto; border-radius: 22px; box-shadow: 0 12px 40px rgba(102,126,234,0.10); background: var(--card-bg); padding: 48px;">
  
  <!-- Wizard Progress -->
  <div class="wizard-progress">
    <div class="progress-container">
      <div class="progress-bar-custom">
        <div class="progress-fill" style="width: {{ progress_percentage }}%;"></div>
      </div>
    </div>
    <div class="step-indicators">
      {% for step_num, step_data in wizard_steps.items() %}
      <div class="step-indicator">
        <div class="step-circle {{ "active" if step_num == current_step else 'completed' if step_num < current_step else '' }}">
          {% if step_num < current_step %}
            <i class="fa-solid fa-check"></i>
          {% else %}
            {{ step_num }}
          {% endif %}
        </div>
        <div class="step-label {{ "active" if step_num == current_step else 'completed' if step_num < current_step else '' }}">
          {{ step_data.name }}
        </div>
      </div>
      {% endfor %}
    </div>
  </div>

  <!-- Step Content -->
  <div class="step-content">
    <h2 class="text-center mb-4">Analysis Ready</h2>
    <p class="text-center text-muted mb-5">
      The system is configured for expert-level analysis with comprehensive reporting
    </p>

    {% if error %}
    <div class="alert alert-danger">
      <i class="fa-solid fa-exclamation-triangle me-2"></i>{{ error }}
    </div>
    {% endif %}

    <form method="post" id="config-form">
      <!-- Analysis Configuration -->
      <div class="config-section mb-4">
        <div class="alert alert-info">
          <i class="fa-solid fa-info-circle me-2"></i>
          <strong>Analysis Configuration:</strong> The system will automatically perform the most comprehensive expert-level analysis with HTML report output for optimal results.
        </div>
        <!-- Hidden inputs to set the configuration -->
        <input type="hidden" name="analysis_depth" value="expert">
        <input type="hidden" name="output_format" value="html">
      </div>

      <!-- Advanced Options -->
      <div class="config-section mb-4">
        <h5><i class="fa-solid fa-cogs me-2"></i>Advanced Options</h5>
        <div class="row">
          <div class="col-md-6">
            <div class="form-check form-switch mb-3">
              <input class="form-check-input" type="checkbox" name="ml_analysis" id="ml-analysis" checked>
              <label class="form-check-label" for="ml-analysis">
                <strong>Enable ML Analysis</strong><br>
                <small class="text-muted">Use machine learning for enhanced insights</small>
              </label>
            </div>
          </div>
          <div class="col-md-6">
            <div class="form-check form-switch mb-3">
              <input class="form-check-input" type="checkbox" name="rag_enhancement" id="rag-enhancement" checked>
              <label class="form-check-label" for="rag-enhancement">
                <strong>RAG Enhancement</strong><br>
                <small class="text-muted">Knowledge-enhanced analysis using RAG</small>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <div class="d-flex justify-content-between mt-5">
        <a href="/wizard/2" class="btn btn-outline-secondary">
          <i class="fa-solid fa-arrow-left me-2"></i>Back
        </a>
        <button type="submit" class="btn btn-primary btn-analysis-expert">
          <i class="fa-solid fa-play me-2"></i>Begin Expert Analysis
        </button>
      </div>
    </form>
</div>
</div>

<style>
/* Fixed button styling - no animations */
.btn-analysis-expert {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
  color: white !important;
  font-weight: 600 !important;
  padding: 12px 30px !important;
  border-radius: 8px !important;
  transition: transform 0.2s ease, box-shadow 0.2s ease !important;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
}

.btn-analysis-expert:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4d93 100%) !important;
  color: white !important;
}

.btn-analysis-expert:focus,
.btn-analysis-expert:active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: white !important;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
}

.btn-analysis-expert:disabled {
  background: #6c757d !important;
  color: white !important;
  transform: none !important;
  box-shadow: none !important;
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Dynamic Progress Bar Animation
    const segments = document.querySelectorAll('.progress-segment');
    const statusText = document.getElementById('progress-status-text');
    
    const progressSteps = [
        { text: "Initializing AI models...", delay: 500 },
        { text: "Loading ML algorithms...", delay: 1000 },
        { text: "Connecting to RAG system...", delay: 1500 },
        { text: "Preparing expert analysis engine...", delay: 2000 },
        { text: "Analysis engine ready! Click to proceed.", delay: 2500 }
    ];
    
    function animateProgress() {
        progressSteps.forEach((step, index) => {
            setTimeout(() => {
                if (index < segments.length) {
                    // Activate current segment
                    segments[index].classList.add('active');
                    
                    // Complete previous segments
                    for (let i = 0; i < index; i++) {
                        segments[i].classList.remove('active');
                        segments[i].classList.add('completed');
                    }
                }
                
                // Update status text
                statusText.textContent = step.text;
                statusText.classList.add('pulse');
                
                setTimeout(() => {
                    statusText.classList.remove('pulse');
                }, 300);
                
                // Keep submit button consistent - removed color changing animation
            }, step.delay);
        });
    }
    
    // Start animation after a short delay
    setTimeout(animateProgress, 300);
    
    // Old config options code (if any config options remain)
    const configOptions = document.querySelectorAll('.config-option');
    
    configOptions.forEach(option => {
        option.addEventListener('click', function() {
            const input = this.querySelector('input[type="radio"]');
            if (input) {
                input.checked = true;
                
                // Update visual state
                const name = input.name;
                document.querySelectorAll(`input[name="${name}"]`).forEach(radio => {
                    radio.closest('.config-option').classList.remove('selected');
                });
                this.classList.add('selected');
            }
        });
    });
    
    // Initialize selected states
    document.querySelectorAll('input[type="radio"]:checked').forEach(radio => {
        radio.closest('.config-option').classList.add('selected');
    });
});
</script>
"""

# Step 4: Processing (Enhanced Progress Bar Implementation)
WIZARD_STEP_4_TEMPLATE = """
<div class="upload-card" style="max-width: 900px; margin: 0 auto; border-radius: 22px; box-shadow: 0 12px 40px rgba(102,126,234,0.10); background: var(--card-bg); padding: 48px;">
  
  <!-- Wizard Progress -->
  <div class="wizard-progress">
    <div class="progress-container">
      <div class="progress-bar-custom">
        <div class="progress-fill" style="width: {{ progress_percentage }}%;"></div>
      </div>
    </div>
    <div class="step-indicators">
      {% for step_num, step_data in wizard_steps.items() %}
      <div class="step-indicator">
        <div class="step-circle {{ 'active' if step_num == current_step else 'completed' if step_num < current_step else '' }}">
          {% if step_num < current_step %}
            <i class="fa-solid fa-check"></i>
          {% else %}
            {{ step_num }}
          {% endif %}
        </div>
        <div class="step-label {{ 'active' if step_num == current_step else 'completed' if step_num < current_step else '' }}">
          {{ step_data.name }}
        </div>
      </div>
      {% endfor %}
    </div>
  </div>

  <!-- Step Content -->
  <div class="step-content text-center">
    <h2 class="mb-3">🔬 AI Analysis in Progress</h2>
    <p class="text-muted mb-4">
      Our advanced AI systems are analyzing your files. Please wait while we generate comprehensive insights.
    </p>

    <!-- Enhanced Progress Bar -->
    <div class="analysis-progress-container mb-5" data-session-id="{{ session_data.session_id if session_data else '' }}">
      <div class="analysis-progress-header mb-3">
        <h5 id="current-stage">Initializing Analysis...</h5>
        <div class="progress-percentage">
          <span id="progress-text">0%</span>
        </div>
      </div>
      
      <!-- Main Progress Bar -->
      <div class="main-progress-bar mb-4">
        <div class="progress" style="height: 20px; border-radius: 10px;">
          <div class="progress-bar progress-bar-striped progress-bar-animated bg-primary" 
               role="progressbar" 
               id="main-progress" 
               style="width: 0%; transition: width 0.5s ease;"
               aria-valuenow="0" 
               aria-valuemin="0" 
               aria-valuemax="100">
          </div>
        </div>
      </div>

      <!-- Analysis Stages -->
      <div class="analysis-stages">
        <div class="row text-center">
          <div class="col-md-3 mb-3">
            <div class="stage-card" id="stage-1">
              <div class="stage-icon">
                <i class="fa-solid fa-file-text"></i>
              </div>
              <div class="stage-title">File Parsing</div>
              <div class="stage-status">
                <i class="fa-solid fa-clock text-muted"></i>
              </div>
            </div>
          </div>
          <div class="col-md-3 mb-3">
            <div class="stage-card" id="stage-2">
              <div class="stage-icon">
                <i class="fa-solid fa-brain"></i>
              </div>
              <div class="stage-title">AI Analysis</div>
              <div class="stage-status">
                <i class="fa-solid fa-clock text-muted"></i>
              </div>
            </div>
          </div>
          <div class="col-md-3 mb-3">
            <div class="stage-card" id="stage-3">
              <div class="stage-icon">
                <i class="fa-solid fa-magic"></i>
              </div>
              <div class="stage-title">ML Enhancement</div>
              <div class="stage-status">
                <i class="fa-solid fa-clock text-muted"></i>
              </div>
            </div>
          </div>
          <div class="col-md-3 mb-3">
            <div class="stage-card" id="stage-4">
              <div class="stage-icon">
                <i class="fa-solid fa-file-alt"></i>
              </div>
              <div class="stage-title">Report Generation</div>
              <div class="stage-status">
                <i class="fa-solid fa-clock text-muted"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Live Analysis Feed -->
    <div class="analysis-feed mb-4">
      <div class="card">
        <div class="card-header">
          <h6 class="mb-0">
            <i class="fa-solid fa-terminal me-2"></i>Analysis Log
          </h6>
        </div>
        <div class="card-body" style="height: 200px; overflow-y: auto; background: #f8f9fa;">
          <div id="analysis-log" style="font-family: monospace; font-size: 0.9em;">
            <div class="log-entry text-success">
              <span class="timestamp">[00:00:00]</span>
              <span class="message">Analysis session initiated...</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Estimated Time -->
    <div class="estimated-time mb-4">
      <div class="alert alert-info">
        <i class="fa-solid fa-clock me-2"></i>
        <strong>Estimated Time:</strong> <span id="estimated-time">2-3 minutes</span>
        <br>
        <small>Analysis time depends on file size and selected enhancement options.</small>
      </div>
    </div>

    <!-- Auto-redirect notification -->
    <div class="mt-4">
      <small class="text-muted">
        <i class="fa-solid fa-info-circle me-1"></i>
        You will be automatically redirected to the results page when analysis is complete.
      </small>
    </div>
  </div>
</div>
"""

# Step 5: Results
WIZARD_STEP_5_TEMPLATE = """
<!-- DEBUG: UPDATED TEMPLATE VERSION 2.0 - NO VIEW DETAILED RESULTS BUTTON -->
<div class="upload-card" style="max-width: 1200px; margin: 0 auto; border-radius: 22px; box-shadow: 0 12px 40px rgba(102,126,234,0.10); background: var(--card-bg); padding: 48px;">
  
  <!-- Wizard Progress -->
  <div class="wizard-progress">
    <div class="progress-container">
      <div class="progress-bar-custom">
        <div class="progress-fill" style="width: {{ progress_percentage }}%;"></div>
      </div>
    </div>
    <div class="step-indicators">
      {% for step_num, step_data in wizard_steps.items() %}
      <div class="step-indicator">
        <div class="step-circle {{ "active" if step_num == current_step else 'completed' if step_num < current_step else '' }}">
          {% if step_num < current_step %}
            <i class="fa-solid fa-check"></i>
          {% else %}
            {{ step_num }}
          {% endif %}
        </div>
        <div class="step-label {{ "active" if step_num == current_step else 'completed' if step_num < current_step else '' }}">
          {{ step_data.name }}
        </div>
      </div>
      {% endfor %}
    </div>
  </div>

  <!-- Step Content -->
  <div class="step-content">
    <h2 class="text-center mb-4">Analysis Complete! 🎉</h2>
    <p class="text-center text-muted mb-5">
      Your analysis has been completed successfully. Review the complete results below.
      <!-- UPDATED VERSION - NO VIEW DETAILED RESULTS BUTTON -->
      <!-- TEMPLATE VERSION: 3.0 - BUTTON REMOVED SUCCESSFULLY -->
    </p>

    <!-- Analysis Summary -->
    <div class="results-summary mb-5">
      <div class="row text-center">
        <div class="col-md-3 mb-3">
          <div class="summary-card">
            <i class="fa-solid fa-files summary-icon text-primary"></i>
            <h4>{{ session_data.uploaded_files|length if session_data.uploaded_files else 0 }}</h4>
            <p class="text-muted mb-0">Files Analyzed</p>
          </div>
        </div>
        <div class="col-md-3 mb-3">
          <div class="summary-card">
            <i class="fa-solid fa-check-circle summary-icon text-success"></i>
            <h4>{{ "Completed" if session_data.status == 'completed' else "Processing" }}</h4>
            <p class="text-muted mb-0">Analysis Status</p>
          </div>
        </div>
        <div class="col-md-3 mb-3">
          <div class="summary-card">
            <i class="fa-solid fa-cogs summary-icon text-info"></i>
            <h4>{{ session_data.analysis_type.replace('_', ' ').title() if session_data.analysis_type else 'N/A' }}</h4>
            <p class="text-muted mb-0">Analysis Type</p>
          </div>
        </div>
        <div class="col-md-3 mb-3">
          <div class="summary-card">
            <i class="fa-solid fa-clock summary-icon text-info"></i>
            <h4>
              {% if session_data.completed_at %}
                {{ session_data.completed_at.split('T')[1].split('.')[0] if 'T' in session_data.completed_at else 'Just now' }}
              {% else %}
                Just now
              {% endif %}
            </h4>
            <p class="text-muted mb-0">Completed At</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Detailed Analysis Results with Navigation -->
    <div class="detailed-results mb-5">
      <h5 class="mb-3">
        <i class="fa-solid fa-chart-line me-2"></i>Complete Analysis Results
      </h5>
      
      {% if session_data.results %}
      <div class="alert alert-info mb-3">
        <i class="fa-solid fa-info-circle me-2"></i>
        <strong>Analysis Complete:</strong> Use the navigation tabs below to explore specific sections of your analysis results.
      </div>

      <!-- Analysis Navigation Bar -->
      <div class="analysis-navigation mb-4">
        <div class="card">
          <div class="card-header bg-light">
            <h6 class="mb-0"><i class="fa-solid fa-compass me-2"></i>Analysis Sections</h6>
          </div>
          <div class="card-body p-2">
            <div class="analysis-nav-tabs" role="tablist">
              <button class="analysis-nav-tab active" data-section="all" role="tab">
                <i class="fa-solid fa-list-ul me-1"></i>View All
              </button>
              <button class="analysis-nav-tab" data-section="summary-stats" role="tab">
                <i class="fa-solid fa-chart-bar me-1"></i>Summary Statistics
              </button>
              <button class="analysis-nav-tab" data-section="recommendations" role="tab">
                <i class="fa-solid fa-bullseye me-1"></i>Key Recommendations
              </button>
              <button class="analysis-nav-tab" data-section="component-analysis" role="tab">
                <i class="fa-solid fa-wrench me-1"></i>Component Analysis
              </button>
              <button class="analysis-nav-tab" data-section="ml-analysis" role="tab">
                <i class="fa-solid fa-brain me-1"></i>ML Analysis
              </button>
              <button class="analysis-nav-tab" data-section="rag-analysis" role="tab">
                <i class="fa-solid fa-database me-1"></i>RAG Analysis
              </button>
              <button class="analysis-nav-tab" data-section="connection-health" role="tab">
                <i class="fa-solid fa-cloud me-1"></i>Connection Health
              </button>
              <button class="analysis-nav-tab" data-section="ai-analysis" role="tab">
                <i class="fa-solid fa-robot me-1"></i>AI Analysis
              </button>
              <button class="analysis-nav-tab" data-section="priority-actions" role="tab">
                <i class="fa-solid fa-exclamation-circle me-1"></i>Priority Actions
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Results Content with Section Parsing -->
      <div class="results-content analysis-content font-consistent" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
        <div id="analysis-sections-container" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
          {{ session_data.results | safe }}
        </div>
      </div>
      {% else %}
      <div class="alert alert-danger mb-3">
        <i class="fa-solid fa-exclamation-triangle me-2"></i>
        <strong>No Results Found:</strong> It appears no analysis results are available in this session. 
        This could mean the analysis hasn't completed yet or there was an error during processing.
      </div>
      {% endif %}
    </div>

    <!-- Action Buttons -->
    <div class="text-center">
      <div class="btn-group" role="group">
        <button type="button" class="btn btn-outline-primary me-3" onclick="downloadReport()">
          <i class="fa-solid fa-download me-2"></i>Download Report
        </button>
        <button type="button" class="btn btn-success" onclick="startNewAnalysis()" id="newAnalysisBtn">
          <i class="fa-solid fa-plus me-2"></i>Start Fresh Analysis
        </button>
      </div>
    </div>
  </div>
</div>

<script>
function downloadReport() {
    // Download the analysis report
    const sessionId = '{{ session_data.session_id if session_data else "" }}';
    if (sessionId) {
        window.location.href = '/download/' + sessionId;
    } else {
        alert('Unable to download report - session not found');
    }
}

function startNewAnalysis() {
    // Show loading state
    const button = document.getElementById('newAnalysisBtn');
    if (button) {
        button.disabled = true;
        button.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i>Cleaning Cache...';
        button.classList.remove('btn-success');
        button.classList.add('btn-warning');
    }
    
    // Clean up cache before starting new analysis
    fetch('/api/cleanup/cache', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success message briefly
            if (button) {
                button.innerHTML = '<i class="fa-solid fa-check me-2"></i>Cache Cleaned! Redirecting...';
                button.classList.remove('btn-warning');
                button.classList.add('btn-success');
            }
            
            // Show notification to user
            if (data.sessions_cleaned > 0 || data.temp_files_cleaned > 0) {
                console.log(`✅ Cache cleanup successful: ${data.sessions_cleaned} sessions and ${data.temp_files_cleaned} temp files cleaned`);
            }
            
            // Redirect to step 1 after short delay
            setTimeout(() => {
                window.location.href = '/wizard/1';
            }, 1500);
        } else {
            console.warn('Cache cleanup failed:', data.error);
            // Restore button and continue anyway
            if (button) {
                button.innerHTML = '<i class="fa-solid fa-exclamation-triangle me-2"></i>Cleanup Failed - Continuing...';
                button.classList.remove('btn-warning');
                button.classList.add('btn-danger');
            }
            setTimeout(() => {
                window.location.href = '/wizard/1';
            }, 2000);
        }
    })
    .catch(error => {
        console.warn('Cache cleanup error:', error);
        // Restore button and continue anyway
        if (button) {
            button.innerHTML = '<i class="fa-solid fa-exclamation-triangle me-2"></i>Cleanup Error - Continuing...';
            button.classList.remove('btn-warning');
            button.classList.add('btn-danger');
        }
        setTimeout(() => {
            window.location.href = '/wizard/1';
        }, 2000);
    });
}

// Analysis Section Navigation
document.addEventListener('DOMContentLoaded', function() {
    const navigationTabs = document.querySelectorAll('.analysis-nav-tab');
    const analysisContainer = document.getElementById('analysis-sections-container');
    
    if (!analysisContainer) return;
    
    // Parse the analysis results into sections
    parseAnalysisSections();
    
    // Add event listeners to navigation tabs
    navigationTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const section = this.dataset.section;
            showAnalysisSection(section);
            
            // Update active tab
            navigationTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    function parseAnalysisSections() {
        const analysisHTML = analysisContainer.innerHTML;
        
        // Store the full content
        window.analysisSections = { 'all': analysisHTML };
        
        // Use a more robust approach to extract sections
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = analysisHTML;
        
        // Extract sections by looking for specific patterns
        const sections = {
            'summary-stats': 'Summary Statistics',
            'recommendations': 'Key Recommendations', 
            'component-analysis': 'Component Analysis',
            'ml-analysis': 'Machine Learning Analysis',
            'rag-analysis': 'RAG-Enhanced Knowledge Analysis',
            'connection-health': 'Cloud One Workload Security Connection Health',
            'ai-analysis': 'AI-Powered Comprehensive Analysis',
            'priority-actions': 'Priority Actions'
        };
        
              for (const [sectionKey, sectionTitle] of Object.entries(sections)) {
                  // Method 1: Try to find by ID first (most reliable) - Enhanced
                  let sectionElement = tempDiv.querySelector(`#${sectionKey}-section`);
                  if (!sectionElement) {
                      // Try variations of the section name
                      const variations = [
                          sectionKey.replace('-', '_') + '-section',
                          sectionKey.replace('-', '') + '-section',
                          sectionTitle.toLowerCase().replace(/\s+/g, '-') + '-section',
                          sectionTitle.toLowerCase().replace(/\s+/g, '_') + '-section'
                      ];
                      for (const variation of variations) {
                          sectionElement = tempDiv.querySelector(`#${variation}`);
                          if (sectionElement) break;
                      }
                  }
                  
                  if (sectionElement) {
                      // Found by ID - this is the most reliable method
                      // However, some sections like summary-stats contain multiple cards
                      // We need to extract only the relevant card for that specific section
                      if (sectionKey === 'summary-stats') {
                          // For summary stats, get only the first card (Summary Statistics card)
                          const statsCard = sectionElement.querySelector('.card:first-child, .col-md-6:first-child .card');
                          if (statsCard) {
                              window.analysisSections[sectionKey] = `<div class="row mb-4"><div class="col-12">${statsCard.outerHTML}</div></div>`;
                              console.log(`Session Detail - Found ${sectionKey} by ID (first card): #${sectionElement.id}`);
                              continue;
                          }
                      } else if (sectionKey === 'recommendations') {
                          // For recommendations, get only the second card (Key Recommendations card)
                          const recommendationsCard = sectionElement.querySelector('.col-md-6:last-child .card, #recommendations-section');
                          if (recommendationsCard) {
                              window.analysisSections[sectionKey] = `<div class="row mb-4"><div class="col-12">${recommendationsCard.outerHTML}</div></div>`;
                              console.log(`Session Detail - Found ${sectionKey} by ID (recommendations card): #${sectionElement.id}`);
                              continue;
                          }
                      } else {
                          // For other sections, use the entire element
                          window.analysisSections[sectionKey] = sectionElement.outerHTML;
                          console.log(`Session Detail - Found ${sectionKey} by ID: #${sectionElement.id}`);
                          continue;
                      }
                  }            // Method 2: Find by card header text
            const headers = tempDiv.querySelectorAll('.card-header, h1, h2, h3, h4, h5, h6, .section-title');
            for (const header of headers) {
                if (header.textContent.trim().includes(sectionTitle)) {
                    // Get only the immediate card container, not the entire row
                    const card = header.closest('.card');
                    if (card) {
                        // For sections that might be in the same row, extract just the individual card
                        const cardClone = card.cloneNode(true);
                        window.analysisSections[sectionKey] = `<div class="row mb-4"><div class="col-12">${cardClone.outerHTML}</div></div>`;
                        break;
                    } else {
                        // If it's not in a card, look for the parent row but be more specific
                        const row = header.closest('.row');
                        if (row) {
                            // Check if this is a multi-card row (like Summary Stats + Recommendations)
                            const cardsInRow = row.querySelectorAll('.card');
                            if (cardsInRow.length > 1) {
                                // Find which card contains our header
                                for (const cardInRow of cardsInRow) {
                                    const cardHeader = cardInRow.querySelector('.card-header, h1, h2, h3, h4, h5, h6');
                                    if (cardHeader && cardHeader.textContent.trim().includes(sectionTitle)) {
                                        window.analysisSections[sectionKey] = `<div class="row mb-4"><div class="col-12">${cardInRow.outerHTML}</div></div>`;
                                        break;
                                    }
                                }
                            } else {
                                // Single card in row, take the whole row
                                window.analysisSections[sectionKey] = row.outerHTML;
                            }
                            break;
                        } else {
                            // Look for a containing div or section
                            const container = header.closest('div[class*="section"], div[class*="analysis"], section');
                            if (container) {
                                window.analysisSections[sectionKey] = `<div class="row mb-4"><div class="col-12">${container.outerHTML}</div></div>`;
                                break;
                            }
                        }
                    }
                }
            }
            
                  // Method 3: Special handling for sections that might not be in standard card format
                  if (!window.analysisSections[sectionKey]) {
                      const allElements = tempDiv.querySelectorAll('*');
                      
                      // Priority Actions patterns
                      if (sectionKey === 'priority-actions') {
                          for (const element of allElements) {
                              const text = element.textContent.toLowerCase();
                              if ((text.includes('priority') && text.includes('action')) || 
                                  text.includes('immediate action') || 
                                  text.includes('recommended action') ||
                                  text.includes('next steps')) {
                                  
                                  // Find the closest meaningful container
                                  let container = element.closest('.card, .row, .container, div[class*="section"], section');
                                  if (!container) {
                                      container = element.parentElement;
                                  }
                                  
                                  // Make sure this container has substantial content related to priority actions
                                  if (container && container.textContent.length > 100) {
                                      window.analysisSections[sectionKey] = `<div class="row mb-4"><div class="col-12">${container.outerHTML}</div></div>`;
                                      break;
                                  }
                              }
                          }
                      }
                      
                      // Summary Statistics patterns
                      if (sectionKey === 'summary-stats') {
                          for (const element of allElements) {
                              const text = element.textContent.toLowerCase();
                              if ((text.includes('summary') && text.includes('statistics')) ||
                                  text.includes('total files') ||
                                  text.includes('analysis summary') ||
                                  (text.includes('statistics') && (text.includes('log') || text.includes('file') || text.includes('event')))) {
                                  
                                  let container = element.closest('.card, .row, .container, div[class*="section"], section, div[class*="stats"]');
                                  if (!container) {
                                      container = element.parentElement;
                                  }
                                  
                                  if (container && container.textContent.length > 100) {
                                      window.analysisSections[sectionKey] = `<div class="row mb-4"><div class="col-12">${container.outerHTML}</div></div>`;
                                      break;
                                  }
                              }
                          }
                      }
                      
                      // AI Analysis patterns
                      if (sectionKey === 'ai-analysis') {
                          for (const element of allElements) {
                              const text = element.textContent.toLowerCase();
                              if ((text.includes('ai') && text.includes('analysis')) ||
                                  text.includes('ai-powered') ||
                                  text.includes('artificial intelligence') ||
                                  text.includes('comprehensive analysis') ||
                                  (text.includes('ai') && (text.includes('insight') || text.includes('recommendation')))) {
                                  
                                  let container = element.closest('.card, .row, .container, div[class*="section"], section, div[class*="ai"]');
                                  if (!container) {
                                      container = element.parentElement;
                                  }
                                  
                                  if (container && container.textContent.length > 100) {
                                      window.analysisSections[sectionKey] = `<div class="row mb-4"><div class="col-12">${container.outerHTML}</div></div>`;
                                      break;
                                  }
                              }
                          }
                      }
                  }            // Method 4: For any remaining sections, try to find by text content pattern
            if (!window.analysisSections[sectionKey]) {
                const allText = tempDiv.textContent.toLowerCase();
                const sectionTitleLower = sectionTitle.toLowerCase();
                
                if (allText.includes(sectionTitleLower)) {
                    // Look for elements that contain the section title
                    const allElements = tempDiv.querySelectorAll('*');
                    for (const element of allElements) {
                        if (element.textContent.toLowerCase().includes(sectionTitleLower) && 
                            element.textContent.length > sectionTitle.length + 50) {
                            
                            let container = element.closest('.card, .row, div[class*="col-"]');
                            if (!container) {
                                container = element;
                            }
                            
                            window.analysisSections[sectionKey] = `<div class="row mb-4"><div class="col-12">${container.outerHTML}</div></div>`;
                            break;
                        }
                    }
                }
            }
        }
        
        // Debug: Log what sections were found
        console.log('Parsed sections:', Object.keys(window.analysisSections).filter(k => k !== 'all'));
        console.log('Priority Actions found:', !!window.analysisSections['priority-actions']);
    }
    
    function showAnalysisSection(sectionKey) {
        if (!window.analysisSections) return;
        
        if (sectionKey === 'all') {
            analysisContainer.innerHTML = window.analysisSections['all'];
            // Add quick jump navigation when showing all sections
            addQuickJumpNavigation();
        } else if (window.analysisSections[sectionKey]) {
            analysisContainer.innerHTML = `
                <div class="section-header mb-3">
                    <button class="btn btn-outline-secondary btn-sm" onclick="showAllSections()">
                        <i class="fa-solid fa-arrow-left me-1"></i>Back to All Sections
                    </button>
                    <span class="ms-3 text-muted">Viewing: <strong>${getSectionDisplayName(sectionKey)}</strong></span>
                </div>
                ${window.analysisSections[sectionKey]}
            `;
        } else {
            analysisContainer.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fa-solid fa-info-circle me-2"></i>
                    <strong>Section Not Available:</strong> The "${getSectionDisplayName(sectionKey)}" section was not found in this analysis.
                    <br><small>This section may not be applicable to your analysis type or no data was available.</small>
                </div>
                <div class="mb-3">
                    <h6>Available Sections:</h6>
                    <div class="available-sections">
                        ${getAvailableSections()}
                    </div>
                </div>
                <button class="btn btn-outline-secondary btn-sm" onclick="showAllSections()">
                    <i class="fa-solid fa-arrow-left me-1"></i>Back to All Sections
                </button>
            `;
        }
    }
    
    function getSectionDisplayName(sectionKey) {
        const displayNames = {
            'summary-stats': 'Summary Statistics',
            'recommendations': 'Key Recommendations',
            'component-analysis': 'Component Analysis',
            'ml-analysis': 'Machine Learning Analysis',
            'rag-analysis': 'RAG-Enhanced Knowledge Analysis',
            'connection-health': 'Connection Health',
            'ai-analysis': 'AI-Powered Analysis',
            'priority-actions': 'Priority Actions'
        };
        return displayNames[sectionKey] || sectionKey;
    }
    
    function getAvailableSections() {
        if (!window.analysisSections) return '';
        
        const availableSections = [];
        for (const [key, content] of Object.entries(window.analysisSections)) {
            if (key !== 'all' && content) {
                availableSections.push(`
                    <button class="btn btn-outline-primary btn-sm me-2 mb-2" onclick="showSpecificSection('${key}')">
                        ${getSectionDisplayName(key)}
                    </button>
                `);
            }
        }
        return availableSections.join('');
    }
    
    function addQuickJumpNavigation() {
        // Add floating quick navigation when viewing all sections
        if (!document.getElementById('quick-jump-nav')) {
            const quickNav = document.createElement('div');
            quickNav.id = 'quick-jump-nav';
            quickNav.className = 'quick-jump-navigation';
            quickNav.innerHTML = `
                <div class="quick-nav-content">
                    <div class="quick-nav-title">Quick Jump</div>
                    <div class="quick-nav-buttons">
                        ${getQuickJumpButtons()}
                    </div>
                </div>
            `;
            document.body.appendChild(quickNav);
        }
    }
    
    function getQuickJumpButtons() {
        if (!window.analysisSections) return '';
        
        const buttons = [];
        for (const [key, content] of Object.entries(window.analysisSections)) {
            if (key !== 'all' && content) {
                buttons.push(`
                    <button class="quick-nav-btn" onclick="scrollToSection('${key}')" title="${getSectionDisplayName(key)}">
                        ${getSectionIcon(key)}
                    </button>
                `);
            }
        }
        return buttons.join('');
    }
    
    function getSectionIcon(sectionKey) {
        const icons = {
            'summary-stats': '<i class="fa-solid fa-chart-bar"></i>',
            'recommendations': '<i class="fa-solid fa-bullseye"></i>',
            'component-analysis': '<i class="fa-solid fa-wrench"></i>',
            'ml-analysis': '<i class="fa-solid fa-brain"></i>',
            'rag-analysis': '<i class="fa-solid fa-database"></i>',
            'connection-health': '<i class="fa-solid fa-cloud"></i>',
            'ai-analysis': '<i class="fa-solid fa-robot"></i>',
            'priority-actions': '<i class="fa-solid fa-exclamation-circle"></i>'
        };
        return icons[sectionKey] || '<i class="fa-solid fa-section"></i>';
    }
    
    function scrollToSection(sectionKey) {
        const sectionTitle = getSectionDisplayName(sectionKey);
        const headers = document.querySelectorAll('.card-header');
        for (const header of headers) {
            if (header.textContent.includes(sectionTitle)) {
                header.scrollIntoView({ behavior: 'smooth', block: 'start' });
                // Add temporary highlight
                const card = header.closest('.card') || header.closest('.row');
                if (card) {
                    card.style.transition = 'box-shadow 0.3s ease';
                    card.style.boxShadow = '0 0 20px rgba(102, 126, 234, 0.5)';
                    setTimeout(() => {
                        card.style.boxShadow = '';
                    }, 2000);
                }
                break;
            }
        }
    }
    
    window.showSpecificSection = function(sectionKey) {
        // Find the tab and click it
        const tab = document.querySelector(`[data-section="${sectionKey}"]`);
        if (tab) {
            tab.click();
        }
    };
    
    // Remove quick nav when switching to individual sections
    function removeQuickNav() {
        const quickNav = document.getElementById('quick-jump-nav');
        if (quickNav) {
            quickNav.remove();
        }
    }
    
    window.showAllSections = function() {
        document.querySelector('[data-section="all"]').click();
    };
});
</script>

<style>
/* Analysis Navigation Styles */
.analysis-navigation {
    position: sticky;
    top: 20px;
    z-index: 100;
}

.analysis-nav-tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.analysis-nav-tab {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    color: #495057;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.875rem;
    font-weight: 500;
    display: flex;
    align-items: center;
}

.analysis-nav-tab:hover {
    background: #e9ecef;
    border-color: #adb5bd;
    color: #212529;
    transform: translateY(-1px);
}

.analysis-nav-tab.active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-color: #667eea;
    color: white;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.analysis-nav-tab.active:hover {
    background: linear-gradient(135deg, #5a6fd8 0%, #6a4d93 100%);
    transform: translateY(-1px);
}

/* Section header for individual views */
.section-header {
    border-bottom: 1px solid #dee2e6;
    padding-bottom: 12px;
}

/* Responsive design for smaller screens */
@media (max-width: 768px) {
    .analysis-nav-tabs {
        flex-direction: column;
    }
    
    .analysis-nav-tab {
        justify-content: center;
        text-align: center;
    }
}

/* Enhanced card styling for better visual separation */
.detailed-results .card {
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border-radius: 8px;
}

.detailed-results .card-header {
    font-weight: 600;
    border-bottom: 2px solid rgba(0,0,0,0.1);
}

/* Smooth transitions */
#analysis-sections-container {
    transition: opacity 0.3s ease;
}

/* Quick Jump Navigation (Floating) */
.quick-jump-navigation {
    position: fixed;
    top: 50%;
    right: 20px;
    transform: translateY(-50%);
    z-index: 1000;
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    padding: 12px;
    min-width: 60px;
}

.quick-nav-content {
    text-align: center;
}

.quick-nav-title {
    font-size: 0.75rem;
    font-weight: 600;
    color: #6c757d;
    margin-bottom: 8px;
    writing-mode: vertical-rl;
    text-orientation: mixed;
}

.quick-nav-buttons {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.quick-nav-btn {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    color: #495057;
    padding: 8px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.875rem;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.quick-nav-btn:hover {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    transform: scale(1.1);
}

/* Hide quick nav on mobile */
@media (max-width: 768px) {
    .quick-jump-navigation {
        display: none;
    }
}

/* Available sections styling */
.available-sections {
    margin-top: 10px;
}

/* Enhanced section highlighting */
.section-highlight {
    animation: sectionPulse 1s ease-in-out;
}

@keyframes sectionPulse {
    0% { box-shadow: 0 0 0 rgba(102, 126, 234, 0.5); }
    50% { box-shadow: 0 0 20px rgba(102, 126, 234, 0.8); }
    100% { box-shadow: 0 0 0 rgba(102, 126, 234, 0.5); }
}
</style>
"""

# Sessions Template (for viewing analysis history)
SESSIONS_TEMPLATE = """
<div class="container mt-5">
  <div class="row justify-content-center">
    <div class="col-12 col-lg-10">
      <div class="card">
        <div class="card-header">
          <h3 class="mb-0"><i class="fa-solid fa-history me-2"></i>Analysis Sessions</h3>
        </div>
        <div class="card-body">
          {% if sessions %}
            <div class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Session ID</th>
                    <th>Analysis Type</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Files</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {% for session in sessions %}
                  <tr>
                    <td><code>{{ session.session_id[:8] }}...</code></td>
                    <td>
                      {% if session.analysis_type %}
                        <span class="badge bg-primary">{{ session.analysis_type.replace('_', ' ').title() }}</span>
                      {% else %}
                        <span class="text-muted">Not set</span>
                      {% endif %}
                    </td>
                    <td>
                      {% if session.status == 'completed' %}
                        <span class="badge bg-success">Completed</span>
                      {% elif session.status == 'processing' %}
                        <span class="badge bg-warning">Processing</span>
                      {% elif session.status == 'failed' %}
                        <span class="badge bg-danger">Failed</span>
                      {% else %}
                        <span class="badge bg-secondary">{{ session.status.title() }}</span>
                      {% endif %}
                    </td>
                    <td>{{ session.created_at.strftime('%Y-%m-%d %H:%M') if session.created_at else 'N/A' }}</td>
                    <td>{{ session.uploaded_files|length if session.uploaded_files else 0 }} files</td>
                    <td>
                      <a href="/session/{{ session.session_id }}" class="btn btn-sm btn-outline-primary">
                        <i class="fa-solid fa-eye me-1"></i>View
                      </a>
                      {% if session.status == 'completed' %}
                      <button class="btn btn-sm btn-outline-success ms-1" onclick=\"downloadSession('{{ session.session_id }}')\">
                        <i class="fa-solid fa-download me-1"></i>Download
                      </button>
                      {% endif %}
                    </td>
                  </tr>
                  {% endfor %}
                </tbody>
              </table>
            </div>
          {% else %}
            <div class="text-center py-5">
              <i class="fa-solid fa-history text-muted" style="font-size: 4rem; margin-bottom: 20px;"></i>
              <h4 class="text-muted">No Analysis Sessions</h4>
              <p class="text-muted mb-4">You haven't run any analyses yet.</p>
              <a href="/wizard/1" class="btn btn-primary">
                <i class="fa-solid fa-plus me-2"></i>Start Your First Analysis
              </a>
            </div>
          {% endif %}
        </div>
      </div>
    </div>
  </div>
</div>

<script>
function downloadSession(sessionId) {
    window.location.href = '/download/' + sessionId;
}
</script>
"""

# Session Detail Template (for viewing individual session details)
SESSION_DETAIL_TEMPLATE = """
<div class="container mt-5">
  <div class="row justify-content-center">
    <div class="col-12">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2><i class="fa-solid fa-file-alt me-2"></i>Session Details</h2>
        <a href="/sessions" class="btn btn-outline-secondary">
          <i class="fa-solid fa-arrow-left me-2"></i>Back to Sessions
        </a>
      </div>

      <!-- Session Info -->
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0"><i class="fa-solid fa-info-circle me-2"></i>Session Information</h5>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <strong>Session ID:</strong> <code>{{ session_data.session_id }}</code><br>
              <strong>Analysis Type:</strong> 
              {% if session_data.analysis_type %}
                <span class="badge bg-primary">{{ session_data.analysis_type.replace('_', ' ').title() }}</span>
              {% else %}
                <span class="text-muted">Not set</span>
              {% endif %}<br>
              <strong>Status:</strong> 
              {% if session_data.status == 'completed' %}
                <span class="badge bg-success">Completed</span>
              {% elif session_data.status == 'processing' %}
                <span class="badge bg-warning">Processing</span>
              {% elif session_data.status == 'failed' %}
                <span class="badge bg-danger">Failed</span>
              {% else %}
                <span class="badge bg-secondary">{{ session_data.status.title() }}</span>
              {% endif %}
            </div>
            <div class="col-md-6">
              <strong>Created:</strong> {{ session_data.created_at.strftime('%Y-%m-%d %H:%M:%S') if session_data.created_at else 'N/A' }}<br>
              <strong>Files Uploaded:</strong> {{ session_data.uploaded_files|length if session_data.uploaded_files else 0 }}<br>
              <strong>Duration:</strong> 
              <span class="fs-6">
                {% if session_data.completed_at %}
                  {{ session_data.completed_at.split('T')[1].split('.')[0] if 'T' in session_data.completed_at else 'N/A' }}
                {% else %}
                  N/A
                {% endif %}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Configuration -->
      {% if session_data.configuration %}
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0"><i class="fa-solid fa-cog me-2"></i>Configuration Used</h5>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <strong>Analysis Depth:</strong> {{ session_data.configuration.analysis_depth.title() if session_data.configuration.analysis_depth else 'N/A' }}<br>
              <strong>Output Format:</strong> {{ session_data.configuration.output_format.title() if session_data.configuration.output_format else 'N/A' }}
            </div>
            <div class="col-md-6">
              <strong>ML Analysis:</strong> {{ "Yes" if session_data.configuration.ml_analysis else 'No' }}<br>
              <strong>RAG Enhancement:</strong> {{ "Yes" if session_data.configuration.rag_enhancement else 'No' }}
            </div>
          </div>
        </div>
      </div>
      {% endif %}

      <!-- Results with Navigation -->
      {% if session_data.results %}
      <div class="card">
        <div class="card-header">
          <h5 class="mb-0"><i class="fa-solid fa-chart-line me-2"></i>Analysis Results</h5>
        </div>
        <div class="card-body">
          <!-- Analysis Navigation Bar -->
          <div class="analysis-navigation mb-4">
            <div class="card">
              <div class="card-header bg-light">
                <h6 class="mb-0"><i class="fa-solid fa-compass me-2"></i>Analysis Sections</h6>
              </div>
              <div class="card-body p-2">
                <div class="analysis-nav-tabs" role="tablist">
                  <button class="analysis-nav-tab active" data-section="all" role="tab">
                    <i class="fa-solid fa-list-ul me-1"></i>View All
                  </button>
                  <button class="analysis-nav-tab" data-section="summary-stats" role="tab">
                    <i class="fa-solid fa-chart-bar me-1"></i>Summary Statistics
                  </button>
                  <button class="analysis-nav-tab" data-section="recommendations" role="tab">
                    <i class="fa-solid fa-bullseye me-1"></i>Key Recommendations
                  </button>
                  <button class="analysis-nav-tab" data-section="component-analysis" role="tab">
                    <i class="fa-solid fa-wrench me-1"></i>Component Analysis
                  </button>
                  <button class="analysis-nav-tab" data-section="ml-analysis" role="tab">
                    <i class="fa-solid fa-brain me-1"></i>ML Analysis
                  </button>
                  <button class="analysis-nav-tab" data-section="rag-analysis" role="tab">
                    <i class="fa-solid fa-database me-1"></i>RAG Analysis
                  </button>
                  <button class="analysis-nav-tab" data-section="connection-health" role="tab">
                    <i class="fa-solid fa-cloud me-1"></i>Connection Health
                  </button>
                  <button class="analysis-nav-tab" data-section="ai-analysis" role="tab">
                    <i class="fa-solid fa-robot me-1"></i>AI Analysis
                  </button>
                  <button class="analysis-nav-tab" data-section="priority-actions" role="tab">
                    <i class="fa-solid fa-exclamation-circle me-1"></i>Priority Actions
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Results Content -->
          <div id="analysis-sections-container">
            {{ session_data.results | safe }}
          </div>
        </div>
      </div>

      <script>
      // Analysis Section Navigation (Session Detail Page)
      document.addEventListener('DOMContentLoaded', function() {
          const navigationTabs = document.querySelectorAll('.analysis-nav-tab');
          const analysisContainer = document.getElementById('analysis-sections-container');
          
          if (!analysisContainer) return;
          
          // Parse the analysis results into sections
          parseAnalysisSections();
          
          // Add event listeners to navigation tabs
          navigationTabs.forEach(tab => {
              tab.addEventListener('click', function() {
                  const section = this.dataset.section;
                  
                  // Remove quick nav when switching to individual sections
                  if (section !== 'all') {
                      removeQuickNav();
                  }
                  
                  showAnalysisSection(section);
                  
                  // Update active tab
                  navigationTabs.forEach(t => t.classList.remove('active'));
                  this.classList.add('active');
              });
          });
          
          function parseAnalysisSections() {
              const analysisHTML = analysisContainer.innerHTML;
              
              // Store the full content
              window.analysisSections = { 'all': analysisHTML };
              
              // Use a more robust approach to extract sections
              const tempDiv = document.createElement('div');
              tempDiv.innerHTML = analysisHTML;
              
              // Extract sections by looking for card headers with specific text
              const sections = {
                  'summary-stats': 'Summary Statistics',
                  'recommendations': 'Key Recommendations', 
                  'component-analysis': 'Component Analysis',
                  'ml-analysis': 'Machine Learning Analysis',
                  'rag-analysis': 'RAG-Enhanced Knowledge Analysis',
                  'connection-health': 'Cloud One Workload Security Connection Health',
                  'ai-analysis': 'AI-Powered Comprehensive Analysis',
                  'priority-actions': 'Priority Actions'
              };
              
              for (const [sectionKey, sectionTitle] of Object.entries(sections)) {
                  // Method 1: Try to find by ID first (most reliable) - Enhanced
                  let sectionElement = tempDiv.querySelector(`#${sectionKey}-section`);
                  if (!sectionElement) {
                      // Try variations of the section name
                      const variations = [
                          sectionKey.replace('-', '_') + '-section',
                          sectionKey.replace('-', '') + '-section',
                          sectionTitle.toLowerCase().replace(/\s+/g, '-') + '-section',
                          sectionTitle.toLowerCase().replace(/\s+/g, '_') + '-section'
                      ];
                      for (const variation of variations) {
                          sectionElement = tempDiv.querySelector(`#${variation}`);
                          if (sectionElement) break;
                      }
                  }
                  
                  if (sectionElement) {
                      // Found by ID - this is the most reliable method
                      // However, some sections like summary-stats contain multiple cards
                      // We need to extract only the relevant card for that specific section
                      if (sectionKey === 'summary-stats') {
                          // For summary stats, get only the first card (Summary Statistics card)
                          const statsCard = sectionElement.querySelector('.card:first-child, .col-md-6:first-child .card');
                          if (statsCard) {
                              window.analysisSections[sectionKey] = `<div class="row mb-4"><div class="col-12">${statsCard.outerHTML}</div></div>`;
                              console.log(`Found ${sectionKey} by ID (first card): #${sectionElement.id}`);
                              continue;
                          }
                      } else if (sectionKey === 'recommendations') {
                          // For recommendations, get only the second card (Key Recommendations card)
                          const recommendationsCard = sectionElement.querySelector('.col-md-6:last-child .card, #recommendations-section');
                          if (recommendationsCard) {
                              window.analysisSections[sectionKey] = `<div class="row mb-4"><div class="col-12">${recommendationsCard.outerHTML}</div></div>`;
                              console.log(`Found ${sectionKey} by ID (recommendations card): #${sectionElement.id}`);
                              continue;
                          }
                      } else {
                          // For other sections, use the entire element
                          window.analysisSections[sectionKey] = sectionElement.outerHTML;
                          console.log(`Found ${sectionKey} by ID: #${sectionElement.id}`);
                          continue;
                      }
                  }
                  
                  // Method 2: Find by card header text
                  const headers = tempDiv.querySelectorAll('.card-header, h1, h2, h3, h4, h5, h6, .section-title');
                  for (const header of headers) {
                      if (header.textContent.trim().includes(sectionTitle)) {
                          // Get only the immediate card container, not the entire row
                          const card = header.closest('.card');
                          if (card) {
                              // For sections that might be in the same row, extract just the individual card
                              const cardClone = card.cloneNode(true);
                              window.analysisSections[sectionKey] = `<div class="row mb-4"><div class="col-12">${cardClone.outerHTML}</div></div>`;
                              break;
                          } else {
                              // If it's not in a card, look for the parent row but be more specific
                              const row = header.closest('.row');
                              if (row) {
                                  // Check if this is a multi-card row (like Summary Stats + Recommendations)
                                  const cardsInRow = row.querySelectorAll('.card');
                                  if (cardsInRow.length > 1) {
                                      // Find which card contains our header
                                      for (const cardInRow of cardsInRow) {
                                          const cardHeader = cardInRow.querySelector('.card-header, h1, h2, h3, h4, h5, h6');
                                          if (cardHeader && cardHeader.textContent.trim().includes(sectionTitle)) {
                                              window.analysisSections[sectionKey] = `<div class="row mb-4"><div class="col-12">${cardInRow.outerHTML}</div></div>`;
                                              break;
                                          }
                                      }
                                  } else {
                                      // Single card in row, take the whole row
                                      window.analysisSections[sectionKey] = row.outerHTML;
                                  }
                                  break;
                              } else {
                                  // Look for a containing div or section
                                  const container = header.closest('div[class*="section"], div[class*="analysis"], section');
                                  if (container) {
                                      window.analysisSections[sectionKey] = `<div class="row mb-4"><div class="col-12">${container.outerHTML}</div></div>`;
                                      break;
                                  }
                              }
                          }
                      }
                  }
                  
                  // Method 3: Special handling for sections that might not be in standard card format
                  if (!window.analysisSections[sectionKey]) {
                      const allElements = tempDiv.querySelectorAll('*');
                      
                      // Priority Actions patterns
                      if (sectionKey === 'priority-actions') {
                          for (const element of allElements) {
                              const text = element.textContent.toLowerCase();
                              if ((text.includes('priority') && text.includes('action')) || 
                                  text.includes('immediate action') || 
                                  text.includes('recommended action') ||
                                  text.includes('next steps')) {
                                  
                                  // Find the closest meaningful container
                                  let container = element.closest('.card, .row, .container, div[class*="section"], section');
                                  if (!container) {
                                      container = element.parentElement;
                                  }
                                  
                                  // Make sure this container has substantial content related to priority actions
                                  if (container && container.textContent.length > 100) {
                                      window.analysisSections[sectionKey] = `<div class="row mb-4"><div class="col-12">${container.outerHTML}</div></div>`;
                                      break;
                                  }
                              }
                          }
                      }
                      
                      // Summary Statistics patterns
                      if (sectionKey === 'summary-stats') {
                          for (const element of allElements) {
                              const text = element.textContent.toLowerCase();
                              if ((text.includes('summary') && text.includes('statistics')) ||
                                  text.includes('total files') ||
                                  text.includes('analysis summary') ||
                                  (text.includes('statistics') && (text.includes('log') || text.includes('file') || text.includes('event')))) {
                                  
                                  let container = element.closest('.card, .row, .container, div[class*="section"], section, div[class*="stats"]');
                                  if (!container) {
                                      container = element.parentElement;
                                  }
                                  
                                  if (container && container.textContent.length > 100) {
                                      window.analysisSections[sectionKey] = `<div class="row mb-4"><div class="col-12">${container.outerHTML}</div></div>`;
                                      break;
                                  }
                              }
                          }
                      }
                      
                      // AI Analysis patterns
                      if (sectionKey === 'ai-analysis') {
                          for (const element of allElements) {
                              const text = element.textContent.toLowerCase();
                              if ((text.includes('ai') && text.includes('analysis')) ||
                                  text.includes('ai-powered') ||
                                  text.includes('artificial intelligence') ||
                                  text.includes('comprehensive analysis') ||
                                  (text.includes('ai') && (text.includes('insight') || text.includes('recommendation')))) {
                                  
                                  let container = element.closest('.card, .row, .container, div[class*="section"], section, div[class*="ai"]');
                                  if (!container) {
                                      container = element.parentElement;
                                  }
                                  
                                  if (container && container.textContent.length > 100) {
                                      window.analysisSections[sectionKey] = `<div class="row mb-4"><div class="col-12">${container.outerHTML}</div></div>`;
                                      break;
                                  }
                              }
                          }
                      }
                  }
                  
                  // Method 4: For any remaining sections, try to find by text content pattern
                  if (!window.analysisSections[sectionKey]) {
                      const allText = tempDiv.textContent.toLowerCase();
                      const sectionTitleLower = sectionTitle.toLowerCase();
                      
                      if (allText.includes(sectionTitleLower)) {
                          // Look for elements that contain the section title
                          const allElements = tempDiv.querySelectorAll('*');
                          for (const element of allElements) {
                              if (element.textContent.toLowerCase().includes(sectionTitleLower) && 
                                  element.textContent.length > sectionTitle.length + 50) {
                                  
                                  let container = element.closest('.card, .row, div[class*="col-"]');
                                  if (!container) {
                                      container = element;
                                  }
                                  
                                  window.analysisSections[sectionKey] = `<div class="row mb-4"><div class="col-12">${container.outerHTML}</div></div>`;
                                  break;
                              }
                          }
                      }
                  }
              }
              
              // Debug: Log what sections were found
              console.log('Parsed sections:', Object.keys(window.analysisSections).filter(k => k !== 'all'));
              console.log('Priority Actions found:', !!window.analysisSections['priority-actions']);
          }
          
          function showAnalysisSection(sectionKey) {
              if (!window.analysisSections) return;
              
              if (sectionKey === 'all') {
                  analysisContainer.innerHTML = window.analysisSections['all'];
                  // Add quick jump navigation when showing all sections
                  addQuickJumpNavigation();
              } else if (window.analysisSections[sectionKey]) {
                  analysisContainer.innerHTML = `
                      <div class="section-header mb-3">
                          <button class="btn btn-outline-secondary btn-sm" onclick="showAllSections()">
                              <i class="fa-solid fa-arrow-left me-1"></i>Back to All Sections
                          </button>
                          <span class="ms-3 text-muted">Viewing: <strong>${getSectionDisplayName(sectionKey)}</strong></span>
                      </div>
                      ${window.analysisSections[sectionKey]}
                  `;
              } else {
                  analysisContainer.innerHTML = `
                      <div class="alert alert-warning">
                          <i class="fa-solid fa-info-circle me-2"></i>
                          <strong>Section Not Available:</strong> The "${getSectionDisplayName(sectionKey)}" section was not found in this analysis.
                          <br><small>This section may not be applicable to your analysis type or no data was available.</small>
                      </div>
                      <div class="mb-3">
                          <h6>Available Sections:</h6>
                          <div class="available-sections">
                              ${getAvailableSections()}
                          </div>
                      </div>
                      <button class="btn btn-outline-secondary btn-sm" onclick="showAllSections()">
                          <i class="fa-solid fa-arrow-left me-1"></i>Back to All Sections
                      </button>
                  `;
              }
          }
          
          function getSectionDisplayName(sectionKey) {
              const displayNames = {
                  'summary-stats': 'Summary Statistics',
                  'recommendations': 'Key Recommendations',
                  'component-analysis': 'Component Analysis',
                  'ml-analysis': 'Machine Learning Analysis',
                  'rag-analysis': 'RAG-Enhanced Knowledge Analysis',
                  'connection-health': 'Connection Health',
                  'ai-analysis': 'AI-Powered Analysis',
                  'priority-actions': 'Priority Actions'
              };
              return displayNames[sectionKey] || sectionKey;
          }
          
          function getAvailableSections() {
              if (!window.analysisSections) return '';
              
              const availableSections = [];
              for (const [key, content] of Object.entries(window.analysisSections)) {
                  if (key !== 'all' && content) {
                      availableSections.push(`
                          <button class="btn btn-outline-primary btn-sm me-2 mb-2" onclick="showSpecificSection('${key}')">
                              ${getSectionDisplayName(key)}
                          </button>
                      `);
                  }
              }
              return availableSections.join('');
          }
          
          function addQuickJumpNavigation() {
              // Add floating quick navigation when viewing all sections
              if (!document.getElementById('quick-jump-nav')) {
                  const quickNav = document.createElement('div');
                  quickNav.id = 'quick-jump-nav';
                  quickNav.className = 'quick-jump-navigation';
                  quickNav.innerHTML = `
                      <div class="quick-nav-content">
                          <div class="quick-nav-title">Quick Jump</div>
                          <div class="quick-nav-buttons">
                              ${getQuickJumpButtons()}
                          </div>
                      </div>
                  `;
                  document.body.appendChild(quickNav);
              }
          }
          
          function getQuickJumpButtons() {
              if (!window.analysisSections) return '';
              
              const buttons = [];
              for (const [key, content] of Object.entries(window.analysisSections)) {
                  if (key !== 'all' && content) {
                      buttons.push(`
                          <button class="quick-nav-btn" onclick="scrollToSection('${key}')" title="${getSectionDisplayName(key)}">
                              ${getSectionIcon(key)}
                          </button>
                      `);
                  }
              }
              return buttons.join('');
          }
          
          function getSectionIcon(sectionKey) {
              const icons = {
                  'summary-stats': '<i class="fa-solid fa-chart-bar"></i>',
                  'recommendations': '<i class="fa-solid fa-bullseye"></i>',
                  'component-analysis': '<i class="fa-solid fa-wrench"></i>',
                  'ml-analysis': '<i class="fa-solid fa-brain"></i>',
                  'rag-analysis': '<i class="fa-solid fa-database"></i>',
                  'connection-health': '<i class="fa-solid fa-cloud"></i>',
                  'ai-analysis': '<i class="fa-solid fa-robot"></i>',
                  'priority-actions': '<i class="fa-solid fa-exclamation-circle"></i>'
              };
              return icons[sectionKey] || '<i class="fa-solid fa-section"></i>';
          }
          
          function scrollToSection(sectionKey) {
              const sectionTitle = getSectionDisplayName(sectionKey);
              const headers = document.querySelectorAll('.card-header');
              for (const header of headers) {
                  if (header.textContent.includes(sectionTitle)) {
                      header.scrollIntoView({ behavior: 'smooth', block: 'start' });
                      // Add temporary highlight
                      const card = header.closest('.card') || header.closest('.row');
                      if (card) {
                          card.style.transition = 'box-shadow 0.3s ease';
                          card.style.boxShadow = '0 0 20px rgba(102, 126, 234, 0.5)';
                          setTimeout(() => {
                              card.style.boxShadow = '';
                          }, 2000);
                      }
                      break;
                  }
              }
          }
          
          window.showSpecificSection = function(sectionKey) {
              // Find the tab and click it
              const tab = document.querySelector(`[data-section="${sectionKey}"]`);
              if (tab) {
                  tab.click();
              }
          };
          
          // Remove quick nav when switching to individual sections
          function removeQuickNav() {
              const quickNav = document.getElementById('quick-jump-nav');
              if (quickNav) {
                  quickNav.remove();
              }
          }
          
          window.showAllSections = function() {
              document.querySelector('[data-section="all"]').click();
          };
      });
      </script>

      <style>
      /* Analysis Navigation Styles for Session Detail */
      .analysis-navigation {
          position: sticky;
          top: 20px;
          z-index: 100;
      }

      .analysis-nav-tabs {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
      }

      .analysis-nav-tab {
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          color: #495057;
          padding: 8px 16px;
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.2s ease;
          font-size: 0.875rem;
          font-weight: 500;
          display: flex;
          align-items: center;
      }

      .analysis-nav-tab:hover {
          background: #e9ecef;
          border-color: #adb5bd;
          color: #212529;
          transform: translateY(-1px);
      }

      .analysis-nav-tab.active {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-color: #667eea;
          color: white;
          box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
      }

      .analysis-nav-tab.active:hover {
          background: linear-gradient(135deg, #5a6fd8 0%, #6a4d93 100%);
          transform: translateY(-1px);
      }

      /* Section header for individual views */
      .section-header {
          border-bottom: 1px solid #dee2e6;
          padding-bottom: 12px;
      }

      /* Responsive design for smaller screens */
      @media (max-width: 768px) {
          .analysis-nav-tabs {
              flex-direction: column;
          }
          
          .analysis-nav-tab {
              justify-content: center;
              text-align: center;
          }
      }

      /* Enhanced card styling for better visual separation */
      .card .card {
          margin-bottom: 20px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          border-radius: 8px;
      }

      .card .card-header {
          font-weight: 600;
          border-bottom: 2px solid rgba(0,0,0,0.1);
      }

      /* Smooth transitions */
      #analysis-sections-container {
          transition: opacity 0.3s ease;
      }
      </style>
      {% else %}
      <div class="text-center py-5">
        <i class="fa-solid fa-exclamation-circle text-muted" style="font-size: 4rem; margin-bottom: 20px;"></i>
        <h4 class="text-muted">No Results Available</h4>
        <p class="text-muted">This session has not completed or failed to produce results.</p>
      </div>
      {% endif %}
    </div>
  </div>
</div>
"""
