// Progress Bar JavaScript Implementation for CSDAI Unified Analyzer
// This file contains all the JavaScript logic for the progress bar functionality

document.addEventListener('DOMContentLoaded', function() {
    // Configuration for the 4 analysis stages (ML-Enhanced Dynamic RAG Workflow)
    const stages = [
        { 
            id: 'stage-1', 
            name: 'File Parsing & Initial Analysis', 
            duration: 4000,  // Slightly increased for better UX
            messages: [
                'Reading uploaded log files...',
                'Validating file format and structure...',
                'Extracting log entries and timestamps...',
                'Preparing data for ML analysis...',
                'File parsing completed ✓'
            ]
        },
        { 
            id: 'stage-2', 
            name: 'ML Pattern Recognition & Analysis', 
            duration: 8000,  // ML analysis timing
            messages: [
                'Loading ML pattern recognition models...',
                'Running behavioral analysis algorithms...',
                'Detecting anomalies and unusual patterns...',
                'Analyzing component health scores...',
                'Classifying severity levels with ML...',
                'Processing component health metrics...',
                'ML analysis enhancement completed ✓'
            ]
        },
        { 
            id: 'stage-3', 
            name: 'Dynamic RAG & AI Intelligence', 
            duration: 32000,  // Increased for comprehensive RAG+AI processing
            messages: [
                'Initializing Dynamic RAG system...',
                'Loading Claude AI analysis engine...',
                'Extracting log context and components...',
                'Generating ML-enhanced dynamic queries...',
                'Searching proprietary PDF knowledge base...',
                'Retrieving relevant Deep Security documentation...',
                'Creating intelligent prompts with ML insights...',
                'Processing with Claude-4 Sonnet AI...',
                'Analyzing Deep Security patterns...',
                'Generating expert recommendations...',
                'Dynamic RAG analysis completed ✓'
            ]
        },
        { 
            id: 'stage-4', 
            name: 'Report Generation & Finalization', 
            duration: 6000,  // Slightly increased for comprehensive reporting
            messages: [
                'Compiling ML and AI analysis results...',
                'Integrating component health assessments...',
                'Formatting expert recommendations...',
                'Generating comprehensive HTML report...',
                'Finalizing security assessments...',
                'Report generation completed ✓'
            ]
        }
    ];
    
    // Global variables
    let currentStageIndex = 0;
    let overallProgress = 0;
    const totalDuration = stages.reduce((sum, stage) => sum + stage.duration, 0);
    let stageStartTime = Date.now();
    let progressInterval;
    let backendCompleted = false;  // Track if backend analysis is actually complete
    let progressSlowdown = 1;  // Factor to slow down progress when backend is still processing
    
    // Get session ID from template (this would be passed from Flask)
    const sessionId = document.querySelector('[data-session-id]')?.getAttribute('data-session-id') || '';
    
    // Debug logging
    console.log('Progress Bar: Session ID detected:', sessionId);
    console.log('Progress Bar: Total stage duration:', totalDuration, 'ms');
    
    /**
     * Update the main progress bar display
     */
    function updateProgress() {
        const progressBar = document.getElementById('main-progress');
        const progressText = document.getElementById('progress-text');
        
        if (progressBar && progressText) {
            progressBar.style.width = overallProgress + '%';
            progressBar.setAttribute('aria-valuenow', Math.round(overallProgress));
            progressText.textContent = Math.round(overallProgress) + '%';
        }
    }
    
    /**
     * Add a new entry to the analysis log
     */
    function addLogEntry(message, type = 'info') {
        const logContainer = document.getElementById('analysis-log');
        if (!logContainer) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const entryClass = type === 'success' ? 'success' : 
                          type === 'warning' ? 'warning' : 
                          type === 'error' ? 'error' : '';
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${entryClass}`;
        logEntry.innerHTML = `
            <span class="timestamp">[${timestamp}]</span>
            <span class="message">${message}</span>
        `;
        
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;
    }
    
    /**
     * Activate and process a specific analysis stage
     */
    function activateStage(stageIndex) {
        if (stageIndex >= stages.length) {
            // All stages complete
            const currentStageElement = document.getElementById('current-stage');
            if (currentStageElement) {
                currentStageElement.textContent = 'Analysis Complete!';
            }
            addLogEntry('All analysis stages completed successfully!', 'success');
            return;
        }
        
        const stage = stages[stageIndex];
        const stageElement = document.getElementById(stage.id);
        
        if (!stageElement) return;
        
        // Update current stage text (with null check to prevent errors on other pages)
        const currentStageElement = document.getElementById('current-stage');
        if (currentStageElement) {
            currentStageElement.textContent = stage.name;
        }
        
        // Mark stage as active
        stageElement.classList.add('active');
        const statusElement = stageElement.querySelector('.stage-status');
        if (statusElement) {
            statusElement.innerHTML = 
                '<div class="spinner-border spinner-border-sm text-primary" role="status">' +
                '<span class="visually-hidden">Loading...</span></div>';
        }
        
        // Process stage messages
        const messageInterval = stage.duration / stage.messages.length;
        
        stage.messages.forEach((message, index) => {
            setTimeout(() => {
                addLogEntry(message, index === stage.messages.length - 1 ? 'success' : 'info');
            }, messageInterval * index);
        });
        
        // Complete stage after duration
        setTimeout(() => {
            stageElement.classList.remove('active');
            stageElement.classList.add('completed');
            
            const statusElement = stageElement.querySelector('.stage-status');
            if (statusElement) {
                statusElement.innerHTML = '<i class="fa-solid fa-check text-success"></i>';
            }
            
            currentStageIndex++;
            activateStage(currentStageIndex);
        }, stage.duration);
    }
    
    /**
     * Update overall progress based on stage completion
     */
    function updateOverallProgress() {
        if (currentStageIndex < stages.length && !backendCompleted) {
            const completedDuration = stages.slice(0, currentStageIndex)
                .reduce((sum, stage) => sum + stage.duration, 0);
            const currentStageDuration = stages[currentStageIndex]?.duration || 0;
            let currentStageProgress = Math.min(Date.now() - stageStartTime, currentStageDuration);
            
            // Apply slowdown factor to prevent progress from completing before backend
            currentStageProgress = currentStageProgress * progressSlowdown;
            
            let calculatedProgress = ((completedDuration + currentStageProgress) / totalDuration) * 100;
            
            // Don't let progress exceed 95% until backend confirms completion
            if (!backendCompleted && calculatedProgress > 95) {
                calculatedProgress = 95;
                progressSlowdown = 0.1; // Slow down significantly at 95%
            } else if (!backendCompleted && calculatedProgress > 85) {
                progressSlowdown = 0.3; // Slow down at 85%
            }
            
            overallProgress = calculatedProgress;
            updateProgress();
        }
    }
    
    /**
     * Start the analysis process and progress tracking
     */
    function startAnalysis() {
        addLogEntry('Starting Deep Security analysis...', 'info');
        
        // Start overall progress tracking
        progressInterval = setInterval(updateOverallProgress, 100);
        
        // Start first stage
        activateStage(0);
        
        // Start checking actual analysis status immediately (backend analysis should already be running)
        setTimeout(checkAnalysisStatus, 1000);
    }
    
    /**
     * Check the actual analysis status from the backend
     */
    function checkAnalysisStatus() {
        if (!sessionId) {
            console.error('No session ID available');
            return;
        }
        
        console.log('Progress Bar: Checking backend status...');
        
        fetch(`/api/session/status/${sessionId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Progress Bar: Backend status:', data.status);
                console.log('Progress Bar: Backend progress:', data.progress_percentage + '%');
                console.log('Progress Bar: Current stage:', data.analysis_stage);
                console.log('Progress Bar: Progress message:', data.progress_message);
                
                // Update progress with real backend data if available
                if (data.progress_percentage && data.progress_percentage > overallProgress) {
                    overallProgress = data.progress_percentage;
                    updateProgress();
                }
                
                // Update current stage text if backend provides it
                if (data.analysis_stage && data.analysis_stage !== 'Unknown') {
                    const currentStageElement = document.getElementById('current-stage');
                    if (currentStageElement) {
                        currentStageElement.textContent = data.analysis_stage;
                    }
                }
                
                // Add backend progress messages to log
                if (data.progress_message && data.progress_message !== 'Processing...') {
                    addLogEntry(data.progress_message, 'info');
                }
                
                if (data.status === 'completed') {
                    // Backend analysis is actually complete
                    backendCompleted = true;
                    clearInterval(progressInterval);
                    overallProgress = 100;
                    updateProgress();
                    
                    addLogEntry('Backend analysis confirmed complete!', 'success');
                    
                    // Complete all visual stages immediately
                    while (currentStageIndex < stages.length) {
                        const stage = stages[currentStageIndex];
                        const stageElement = document.getElementById(stage.id);
                        if (stageElement) {
                            stageElement.classList.remove('active');
                            stageElement.classList.add('completed');
                            const statusElement = stageElement.querySelector('.stage-status');
                            if (statusElement) {
                                statusElement.innerHTML = '<i class="fa-solid fa-check text-success"></i>';
                            }
                        }
                        currentStageIndex++;
                    }
                    
                    addLogEntry('Analysis completed successfully! Redirecting...', 'success');
                    const currentStageElement = document.getElementById('current-stage');
                    if (currentStageElement) {
                        currentStageElement.textContent = 'Redirecting to Results...';
                    }
                    
                    // Redirect to results page
                    setTimeout(() => {
                        window.location.href = '/wizard/5';
                    }, 2000);
                    
                } else if (data.status === 'error' || data.status === 'failed') {
                    // Analysis failed
                    clearInterval(progressInterval);
                    addLogEntry('Analysis failed. Please try again.', 'error');
                    
                    const currentStageElement = document.getElementById('current-stage');
                    if (currentStageElement) {
                        currentStageElement.textContent = 'Analysis Failed';
                    }
                    
                    // Show error message
                    const progressContainer = document.querySelector('.analysis-progress-container');
                    if (progressContainer) {
                        progressContainer.innerHTML = `
                            <div class="alert alert-danger text-center">
                                <i class="fa-solid fa-exclamation-triangle me-2"></i>
                                <strong>Analysis Failed</strong><br>
                                <small>Please go back and try again, or contact support if the issue persists.</small>
                            </div>
                        `;
                    }
                    
                } else {
                    // Still processing, check again more frequently
                    setTimeout(checkAnalysisStatus, 1500);  // Reduced from 2000ms to 1500ms
                }
            })
            .catch(error => {
                console.error('Progress Bar: Error checking status:', error);
                addLogEntry('Connection error, retrying...', 'warning');
                
                // Retry after shorter delay
                setTimeout(checkAnalysisStatus, 2000);  // Reduced from 3000ms
            });
    }
    
    /**
     * Handle page visibility changes to pause/resume progress
     */
    function handleVisibilityChange() {
        if (document.hidden) {
            // Page is hidden, optionally pause progress updates
            console.log('Page hidden, continuing progress in background');
        } else {
            // Page is visible, ensure progress is running
            console.log('Page visible, progress continues');
        }
    }
    
    // Set up event listeners
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    // Initialize the progress bar system
    if (document.getElementById('main-progress')) {
        startAnalysis();
    }
});

// Export functions for external use if needed
window.ProgressBar = {
    // Public API for progress bar control
    pause: function() {
        // Pause progress updates
        console.log('Progress paused');
    },
    resume: function() {
        // Resume progress updates
        console.log('Progress resumed');
    },
    reset: function() {
        // Reset progress to 0
        const progressBar = document.getElementById('main-progress');
        const progressText = document.getElementById('progress-text');
        if (progressBar) progressBar.style.width = '0%';
        if (progressText) progressText.textContent = '0%';
    }
};
