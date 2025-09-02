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
    let targetProgress = 0;  // Smooth transition target
    const totalDuration = stages.reduce((sum, stage) => sum + stage.duration, 0);
    let stageStartTime = Date.now();
    let progressInterval;
    let smoothProgressInterval;  // Dedicated interval for smooth progress transitions
    let autoScrollEnabled = true;
    let userScrollTimer = null;
    let backendCompleted = false;  // Track if backend analysis is actually complete
    let progressSlowdown = 1;  // Factor to slow down progress when backend is still processing
    let lastBackendProgress = 0;  // Track last backend progress to prevent backward movement
    let animationFrameId = null;  // For smooth animation using requestAnimationFrame
    let lastProgressMessage = '';  // Track last progress message to prevent duplicates
    
    // Get session ID from template (this would be passed from Flask)
    const sessionId = document.querySelector('[data-session-id]')?.getAttribute('data-session-id') || '';
    
    // Debug logging
    console.log('Progress Bar: Session ID detected:', sessionId);
    console.log('Progress Bar: Total stage duration:', totalDuration, 'ms');
    
    /**
     * Update the main progress bar display with ultra-smooth animation
     */
    function updateProgress() {
        const progressBar = document.getElementById('main-progress');
        const progressText = document.getElementById('progress-text');
        
        if (progressBar && progressText) {
            // Cancel any existing animation
            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
            }
            
            // Use requestAnimationFrame for ultra-smooth animation
            function smoothUpdate() {
                const currentWidth = parseFloat(progressBar.style.width) || 0;
                const diff = targetProgress - currentWidth;
                
                if (Math.abs(diff) > 0.05) {  // Reduced threshold for smoother animation
                    // Smooth interpolation with exponential easing for natural feel
                    const newWidth = currentWidth + (diff * 0.08);  // Slightly slower for smoother effect
                    
                    // Set width directly without any CSS transitions
                    progressBar.style.width = newWidth + '%';
                    progressBar.style.transition = 'none';  // Ensure no CSS transitions interfere
                    progressBar.setAttribute('aria-valuenow', Math.round(newWidth));
                    progressText.textContent = Math.round(newWidth) + '%';
                    
                    animationFrameId = requestAnimationFrame(smoothUpdate);
                } else {
                    // Close enough, set final value
                    progressBar.style.width = targetProgress + '%';
                    progressBar.style.transition = 'none';
                    progressBar.setAttribute('aria-valuenow', Math.round(targetProgress));
                    progressText.textContent = Math.round(targetProgress) + '%';
                }
            }
            
            // Start smooth animation
            smoothUpdate();
        }
    }
    
    /**
     * Setup auto-scroll behavior with user interaction detection
     */
    function setupAutoScroll() {
        const logContainer = document.getElementById('analysis-log');
        const scrollIndicator = document.getElementById('auto-scroll-indicator');
        const scrollButton = document.getElementById('scroll-to-bottom-btn');
        
        if (!logContainer) return;
        
        // Handle scroll-to-bottom button click
        if (scrollButton) {
            scrollButton.addEventListener('click', function() {
                autoScrollEnabled = true;
                logContainer.scrollTo({
                    top: logContainer.scrollHeight,
                    behavior: 'smooth'
                });
                scrollButton.classList.remove('visible');
                if (scrollIndicator) {
                    scrollIndicator.style.opacity = '0';
                }
            });
        }
        
        // Detect user scrolling
        logContainer.addEventListener('scroll', function() {
            const isAtBottom = logContainer.scrollTop + logContainer.clientHeight >= logContainer.scrollHeight - 10;
            
            if (!isAtBottom) {
                // User scrolled up, disable auto-scroll temporarily
                autoScrollEnabled = false;
                if (scrollIndicator) {
                    scrollIndicator.textContent = 'Auto-scroll paused';
                    scrollIndicator.style.opacity = '1';
                    scrollIndicator.style.backgroundColor = 'rgba(220, 53, 69, 0.9)';
                }
                
                // Show scroll-to-bottom button
                if (scrollButton) {
                    scrollButton.classList.add('visible');
                }
                
                // Clear existing timer
                if (userScrollTimer) {
                    clearTimeout(userScrollTimer);
                }
                
                // Re-enable auto-scroll after 3 seconds of no scrolling
                userScrollTimer = setTimeout(() => {
                    autoScrollEnabled = true;
                    if (scrollIndicator) {
                        scrollIndicator.style.opacity = '0';
                        scrollIndicator.style.backgroundColor = 'rgba(13, 110, 253, 0.9)';
                        scrollIndicator.textContent = 'Auto-scrolling';
                    }
                    if (scrollButton) {
                        scrollButton.classList.remove('visible');
                    }
                }, 3000);
            } else {
                // User is at bottom, re-enable auto-scroll
                autoScrollEnabled = true;
                if (scrollIndicator) {
                    scrollIndicator.style.opacity = '0';
                }
                if (scrollButton) {
                    scrollButton.classList.remove('visible');
                }
            }
        });
    }
    
    /**
     * Add a new entry to the analysis log with performance optimization
     */
    function addLogEntry(message, type = 'info') {
        const logContainer = document.getElementById('analysis-log');
        if (!logContainer) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const entryClass = type === 'success' ? 'success' : 
                          type === 'warning' ? 'warning' : 
                          type === 'error' ? 'error' : '';
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${entryClass} new-entry`;
        logEntry.innerHTML = `
            <span class="timestamp">[${timestamp}]</span>
            <span class="message">${message}</span>
        `;
        
        // Use DocumentFragment for better performance
        const fragment = document.createDocumentFragment();
        fragment.appendChild(logEntry);
        logContainer.appendChild(fragment);
        
        // Remove the highlight effect after a moment
        setTimeout(() => {
            logEntry.classList.remove('new-entry');
        }, 1000);
        
        // Throttled auto-scroll - only scroll if enabled and not too frequent
        if (autoScrollEnabled) {
            // Use requestAnimationFrame for smooth scrolling
            requestAnimationFrame(() => {
                // Show auto-scroll indicator
                const scrollIndicator = document.getElementById('auto-scroll-indicator');
                if (scrollIndicator) {
                    scrollIndicator.style.opacity = '1';
                }
                
                // Smooth automatic scrolling to bottom
                logContainer.scrollTo({
                    top: logContainer.scrollHeight,
                    behavior: 'smooth'
                });
                
                // Hide auto-scroll indicator after scrolling completes
                setTimeout(() => {
                    if (scrollIndicator) {
                        scrollIndicator.style.opacity = '0';
                    }
                }, 500);
            });
        }
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
     * Update overall progress based on stage completion with smooth transitions
     */
    function updateOverallProgress() {
        if (backendCompleted) {
            return; // Stop fake progress when backend is complete
        }
        
        // Only use fake progress as a fallback for the first few seconds
        // or when backend hasn't provided progress yet
        if (!lastBackendProgress || lastBackendProgress === 0) {
            // Minimal fake progress only for the first 10-15 seconds to show activity
            const elapsedTime = Date.now() - stageStartTime;
            let fallbackProgress = Math.min(elapsedTime / 15000 * 10, 10); // Max 10% in 15 seconds
            
            if (fallbackProgress > overallProgress) {
                overallProgress = fallbackProgress;
                targetProgress = fallbackProgress;
                updateProgress();
            }
        }
        // All other progress updates come from backend via checkAnalysisStatus()
    }
    
    /**
     * Start the analysis process and progress tracking with improved timing
     */
    function startAnalysis() {
        addLogEntry('Starting Deep Security analysis...', 'info');
        
        // Initialize progress bar to ensure clean state
        const progressBar = document.getElementById('main-progress');
        if (progressBar) {
            progressBar.style.width = '0%';
            progressBar.style.transition = 'none';  // Disable any CSS transitions
            progressBar.setAttribute('aria-valuenow', 0);
        }
        
        const progressText = document.getElementById('progress-text');
        if (progressText) {
            progressText.textContent = '0%';
        }
        
        // Reset all progress variables
        overallProgress = 0;
        targetProgress = 0;
        currentStageIndex = 0;
        stageStartTime = Date.now();
        
        // Start overall progress tracking with optimized frequency
        progressInterval = setInterval(updateOverallProgress, 250); // Slightly increased for smoother feel
        
        // Start first stage
        activateStage(0);
        
        // Start checking actual analysis status immediately (backend analysis should already be running)
        setTimeout(checkAnalysisStatus, 1000);
    }
    
    /**
     * Check the actual analysis status from the backend with improved synchronization
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
                
                // Update progress with real backend data if available and higher than current
                if (data.progress_percentage && data.progress_percentage > lastBackendProgress) {
                    lastBackendProgress = data.progress_percentage;
                    
                    // Update from backend progress with minimal threshold for responsiveness
                    if (data.progress_percentage > targetProgress + 0.5) {  // Reduced threshold to 0.5%
                        const newTarget = Math.min(data.progress_percentage, 99); // Cap at 99% until completion
                        
                        // Smooth transition to backend progress
                        targetProgress = newTarget;
                        overallProgress = newTarget;
                        
                        console.log('Progress Bar: Updating from backend:', newTarget + '%');
                        updateProgress();
                    }
                }
                
                // Update current stage text if backend provides it
                if (data.analysis_stage && data.analysis_stage !== 'Unknown') {
                    const currentStageElement = document.getElementById('current-stage');
                    if (currentStageElement) {
                        currentStageElement.textContent = data.analysis_stage;
                    }
                }
                
                // Add backend progress messages to log (throttled to prevent spam)
                if (data.progress_message && data.progress_message !== 'Processing...' && 
                    data.progress_message !== lastProgressMessage) {
                    addLogEntry(data.progress_message, 'info');
                    lastProgressMessage = data.progress_message;
                }
                
                if (data.status === 'completed') {
                    // Backend analysis is actually complete
                    backendCompleted = true;
                    clearInterval(progressInterval);
                    
                    // Smooth completion to 100%
                    targetProgress = 100;
                    overallProgress = 100;
                    updateProgress();
                    
                    addLogEntry('Backend analysis confirmed complete!', 'success');
                    
                    // Complete all visual stages with smooth transitions
                    completeAllStagesSmooth();
                    
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
                    if (animationFrameId) {
                        cancelAnimationFrame(animationFrameId);
                    }
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
                    // Still processing, check again
                    setTimeout(checkAnalysisStatus, 1800);  // Slightly increased interval for smoother flow
                }
            })
            .catch(error => {
                console.error('Progress Bar: Error checking status:', error);
                addLogEntry('Connection error, retrying...', 'warning');
                
                // Retry after shorter delay
                setTimeout(checkAnalysisStatus, 2500);
            });
    }
    
    /**
     * Complete all remaining stages with smooth transitions
     */
    function completeAllStagesSmooth() {
        const remainingStages = stages.slice(currentStageIndex);
        
        remainingStages.forEach((stage, index) => {
            setTimeout(() => {
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
            }, index * 300); // Stagger completions by 300ms for smooth effect
        });
    }
    
    /**
     * Cleanup function to prevent memory leaks
     */
    function cleanup() {
        if (progressInterval) {
            clearInterval(progressInterval);
        }
        if (smoothProgressInterval) {
            clearInterval(smoothProgressInterval);
        }
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
        }
        if (userScrollTimer) {
            clearTimeout(userScrollTimer);
        }
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
    window.addEventListener('beforeunload', cleanup);  // Cleanup on page unload
    
    // Initialize the progress bar system
    if (document.getElementById('main-progress')) {
        setupAutoScroll();
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
