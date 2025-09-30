'use client';

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import SmartTitleSuggestion from './SmartTitleSuggestion';
import DescriptionAssistant from './DescriptionAssistant';

interface FormData {
  product: string;
  productVersion: string;
  operatingSystem: string;
  issueCategory: string;
  caseTitle: string;
  severity: string;
  description: string;
  ccEmail: string;
  attachments: File[];
}

interface AnalyzerRecommendation {
  analyzerId: string;
  analyzerName: string;
  confidence: number;
  reasoning: string;
  icon: string;
}

export default function EnhancedNewCaseForm() {
  const router = useRouter();
  const recommendationRef = useRef<HTMLDivElement>(null);
  
  const [formData, setFormData] = useState<FormData>({
    product: 'Deep Security',
    productVersion: '20.0',
    operatingSystem: 'CentOS 5 32-bit',
    issueCategory: 'Product Issue',
    caseTitle: '',
    severity: '',
    description: '',
    ccEmail: '',
    attachments: []
  });

  const [expandedSections, setExpandedSections] = useState({
    product: true,
    issueCategory: true,
    requestDetail: true,
    attachments: true
  });

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [aiRecommendation, setAiRecommendation] = useState<AnalyzerRecommendation | null>(null);

  const [showLogCollectionModal, setShowLogCollectionModal] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [ticketNumber, setTicketNumber] = useState('');

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleFileUpload = async (files: FileList | null) => {
    console.log('🔄 Portal handleFileUpload called with files:', files);
    
    if (files) {
      const fileArray = Array.from(files);
      console.log('📁 Processing files:', fileArray.map(f => ({ name: f.name, size: f.size, type: f.type })));
      
      // Filter out files that are too large (1GB limit)
      const validFiles = fileArray.filter(file => {
        const maxSize = 1024 * 1024 * 1024; // 1GB
        if (file.size > maxSize) {
          alert(`File "${file.name}" is too large. Maximum file size is 1GB.`);
          return false;
        }
        return true;
      });
      
      if (validFiles.length > 0) {
        setFormData(prev => ({
          ...prev,
          attachments: [...prev.attachments, ...validFiles]
        }));
        console.log('✅ Files added to attachments:', validFiles.length);
      }
    } else {
      console.log('❌ No files provided to handleFileUpload');
    }
  };

  const removeAttachment = (index: number) => {
    setFormData(prev => ({
      ...prev,
      attachments: prev.attachments.filter((_, i) => i !== index)
    }));
  };

  const analyzeWithAI = async () => {
    console.log('🔍 Starting AI analysis with data:', {
      description: formData.description,
      product: formData.product,
      issueCategory: formData.issueCategory,
      severity: formData.severity,
      attachmentCount: formData.attachments.length,
      attachmentTypes: formData.attachments.map(f => f.type)
    });

    setIsAnalyzing(true);
    try {
      const requestBody = {
        description: formData.description,
        caseTitle: formData.caseTitle, // Include case title for better analysis
        product: formData.product,
        issueCategory: formData.issueCategory,
        severity: formData.severity,
        attachmentCount: formData.attachments.length,
        attachmentTypes: formData.attachments.map(f => f.type)
      };

      console.log('📤 Sending request to AI API:', requestBody);

      const response = await fetch('/api/ai/analyze-case', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      console.log('📥 AI API response status:', response.status, response.statusText);

      if (response.ok) {
        const recommendation = await response.json();
        console.log('✅ AI recommendation received:', recommendation);
        setAiRecommendation(recommendation);
        
        // Scroll to recommendation after a short delay to allow rendering
        setTimeout(() => {
          recommendationRef.current?.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
          });
        }, 100);
      } else {
        const errorText = await response.text();
        console.error('❌ AI analysis failed:', response.status, errorText);
        // Fallback to intelligent recommendation based on product
        const productSpecificFallback = formData.product === 'Deep Security' ? 'resource_analysis' : 'amsp_logs';
        setAiRecommendation({
          analyzerId: productSpecificFallback,
          analyzerName: productSpecificFallback === 'resource_analysis' ? 'Resource Analysis' : 'AMSP Analysis',
          confidence: 0.5,
          reasoning: 'Default recommendation based on product selection due to API error',
          icon: productSpecificFallback === 'resource_analysis' ? '📈' : '🦠'
        });
      }
    } catch (error) {
      console.error('💥 Error during AI analysis:', error);
      // Fallback recommendation based on product
      const productSpecificFallback = formData.product === 'Deep Security' ? 'resource_analysis' : 'amsp_logs';
      setAiRecommendation({
        analyzerId: productSpecificFallback,
        analyzerName: productSpecificFallback === 'resource_analysis' ? 'Resource Analysis' : 'AMSP Analysis',
        confidence: 0.5,
        reasoning: 'Default recommendation due to analysis error',
        icon: productSpecificFallback === 'resource_analysis' ? '📈' : '🦠'
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSubmitToIntellicket = async () => {
    console.log('🚀 Submit to Intellicket clicked!', {
      description: formData.description,
      hasDescription: !!formData.description.trim(),
      severity: formData.severity,
      hasSeverity: !!formData.severity,
      attachments: formData.attachments.length,
      formData
    });

    // Security Validation 1: Basic required fields
    if (!formData.description.trim()) {
      alert('Please provide a description for AI analysis');
      return;
    }

    if (!formData.severity) {
      alert('Please select a severity level');
      return;
    }

    // Security Validation 2: ZIP file attachment requirement
    const hasValidZipFiles = formData.attachments.some(file => 
      file.name.toLowerCase().endsWith('.zip') && file.size > 0
    );

    if (!hasValidZipFiles) {
      // Enhanced error modal with proper UX
      const userWantsToAddFiles = window.confirm(
        '🔒 ZIP File Required for Intellicket Analysis\n\n' +
        'Intellicket requires diagnostic ZIP files (like Diagnostic Package.zip) to perform accurate analysis.\n\n' +
        'Without ZIP files, the analyzer cannot access the necessary log files for:\n' +
        '• Deep Security Agent logs\n' +
        '• Anti-malware scan data\n' +
        '• System resource information\n' +
        '• Performance diagnostics\n\n' +
        'Would you like to attach ZIP files now?\n\n' +
        'Click OK to add files, or Cancel to submit a traditional case instead.'
      );

      if (userWantsToAddFiles) {
        // Scroll to attachment section to help user
        const attachmentSection = document.querySelector('[data-section="attachments"]');
        if (attachmentSection) {
          attachmentSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
          // Expand attachments section if collapsed
          if (!expandedSections.attachments) {
            toggleSection('attachments');
          }
        }
        return;
      } else {
        // User wants to proceed without ZIP - show warning about limitations
        const confirmWithoutZip = window.confirm(
          '⚠️ Proceeding Without ZIP Files\n\n' +
          'Without diagnostic ZIP files, Intellicket analysis will be limited:\n' +
          '• No automated log parsing\n' +
          '• No intelligent file extraction\n' +
          '• Manual file upload required in analyzer\n' +
          '• Reduced analysis accuracy\n\n' +
          'Are you sure you want to continue?\n\n' +
          'Recommendation: Attach Diagnostic Package.zip for best results.'
        );

        if (!confirmWithoutZip) {
          return; // User cancelled
        }
        
        // Log security event for audit trail
        console.warn('🔐 SECURITY: User proceeding to Intellicket without ZIP files', {
          caseTitle: formData.caseTitle,
          description: formData.description.substring(0, 100) + '...',
          attachmentCount: formData.attachments.length,
          attachmentTypes: formData.attachments.map(f => f.type),
          timestamp: new Date().toISOString()
        });
      }
    }

    console.log('🤖 Starting AI analysis...');
    await analyzeWithAI();
  };

  const proceedWithAnalyzer = async () => {
    console.log('🎯 Proceeding with analyzer:', aiRecommendation);
    
    if (!aiRecommendation) {
      console.error('❌ No AI recommendation available');
      return;
    }

    // Check if there are attachments to process
    if (formData.attachments.length > 0) {
      console.log('📦 Processing attachments for automatic upload...');
      setIsAnalyzing(true);

      try {
        // Create FormData for file extraction and upload
        const extractFormData = new FormData();
        formData.attachments.forEach(file => {
          extractFormData.append('files', file);
        });
        extractFormData.append('analyzerId', aiRecommendation.analyzerId);

        // Call the extract and upload API
        const response = await fetch('/api/extract-and-upload', {
          method: 'POST',
          body: extractFormData,
        });

        const result = await response.json();

        if (result.success) {
          console.log('✅ Files extracted and uploaded successfully:', result);
          
          // Store case context with extraction results
          const caseContext = {
            caseTitle: formData.caseTitle,
            description: formData.description,
            product: formData.product,
            severity: formData.severity,
            attachments: formData.attachments.map(f => ({ name: f.name, size: f.size, type: f.type })),
            extractedFiles: result.extractedFiles,
            autoUploaded: true,
            uploadResult: result.uploadResult
          };
          
          console.log('💾 Storing case context with extracted files:', caseContext);
          sessionStorage.setItem('caseContext', JSON.stringify(caseContext));

          // Navigate to the analyzer page - Check for dedicated analyzer pages
          let targetUrl;
          if (aiRecommendation.analyzerId === 'ds_agent_offline_analyzer') {
            // Redirect to dedicated DS Agent Offline page
            targetUrl = '/products/deep-security/analyzer-dsoffline';
          } else {
            // Use standard analyzer parameter format
            const analyzerParam = `?analyzer=${aiRecommendation.analyzerId}&autoUploaded=true`;
            targetUrl = `/products/deep-security${analyzerParam}`;
          }
          
          console.log('🚀 Navigating to analyzer with auto-uploaded files:', targetUrl);
          router.push(targetUrl);
        } else {
          console.warn('⚠️ File extraction failed, proceeding without auto-upload:', result.error);
          
          // Fallback to normal flow without auto-upload
          const caseContext = {
            caseTitle: formData.caseTitle,
            description: formData.description,
            product: formData.product,
            severity: formData.severity,
            attachments: formData.attachments.map(f => ({ name: f.name, size: f.size, type: f.type })),
            extractionError: result.error,
            requiredFiles: result.requiredFiles
          };
          
          sessionStorage.setItem('caseContext', JSON.stringify(caseContext));
          
          // Check for dedicated analyzer pages
          let targetUrl;
          if (aiRecommendation.analyzerId === 'ds_agent_offline_analyzer') {
            // Redirect to dedicated DS Agent Offline page
            targetUrl = '/products/deep-security/analyzer-dsoffline';
          } else {
            // Use standard analyzer parameter format
            const analyzerParam = `?analyzer=${aiRecommendation.analyzerId}`;
            targetUrl = `/products/deep-security${analyzerParam}`;
          }
          
          console.log('🚀 Navigating to analyzer (manual upload required):', targetUrl);
          router.push(targetUrl);
        }
      } catch (error) {
        console.error('💥 Error during file extraction:', error);
        
        // Fallback to normal flow
        const caseContext = {
          caseTitle: formData.caseTitle,
          description: formData.description,
          product: formData.product,
          severity: formData.severity,
          attachments: formData.attachments.map(f => ({ name: f.name, size: f.size, type: f.type })),
          extractionError: 'Failed to process attachments'
        };
        
        sessionStorage.setItem('caseContext', JSON.stringify(caseContext));
        
        // Check for dedicated analyzer pages
        let targetUrl;
        if (aiRecommendation.analyzerId === 'ds_agent_offline_analyzer') {
          // Redirect to dedicated DS Agent Offline page
          targetUrl = '/products/deep-security/analyzer-dsoffline';
        } else {
          // Use standard analyzer parameter format
          const analyzerParam = `?analyzer=${aiRecommendation.analyzerId}`;
          targetUrl = `/products/deep-security${analyzerParam}`;
        }
        
        console.log('🚀 Navigating to analyzer (extraction failed):', targetUrl);
        router.push(targetUrl);
      } finally {
        setIsAnalyzing(false);
      }
    } else {
      // No attachments, proceed normally
      const caseContext = {
        caseTitle: formData.caseTitle,
        description: formData.description,
        product: formData.product,
        severity: formData.severity,
        attachments: []
      };
      
      console.log('💾 Storing case context (no attachments):', caseContext);
      sessionStorage.setItem('caseContext', JSON.stringify(caseContext));

      // Navigate to the deep-security page with the recommended analyzer - Check for dedicated pages
      let targetUrl;
      if (aiRecommendation.analyzerId === 'ds_agent_offline_analyzer') {
        // Redirect to dedicated DS Agent Offline page
        targetUrl = '/products/deep-security/analyzer-dsoffline';
      } else {
        // Use standard analyzer parameter format
        const analyzerParam = `?analyzer=${aiRecommendation.analyzerId}`;
        targetUrl = `/products/deep-security${analyzerParam}`;
      }
      
      console.log('🚀 Navigating to:', targetUrl);
      router.push(targetUrl);
    }
  };

  const generateTicketNumber = () => {
    // Generate 8-digit random number
    const randomNumber = Math.floor(10000000 + Math.random() * 90000000);
    return `TM-${randomNumber}`;
  };

  const handleSubmitTraditionalCase = async () => {
    console.log('📝 Submitting traditional case...');
    
    // Validate required fields
    if (!formData.description.trim() || !formData.severity) {
      alert('Please complete: Description and Severity Level');
      return;
    }

    try {
      // Generate ticket number
      const newTicketNumber = generateTicketNumber();
      setTicketNumber(newTicketNumber);

      // Simulate case submission (you can add actual API call here)
      console.log('✅ Traditional case submitted:', {
        ticketNumber: newTicketNumber,
        caseTitle: formData.caseTitle,
        description: formData.description,
        product: formData.product,
        severity: formData.severity,
        attachments: formData.attachments.length
      });

      // Show success modal
      setShowSuccessModal(true);
      
    } catch (error) {
      console.error('❌ Error submitting traditional case:', error);
      alert('Error submitting case. Please try again.');
    }
  };

  const handleChooseDifferentAnalyzer = () => {
    console.log('🔄 User choosing different analyzer');
    
    // Show warning about re-uploading files if there are attachments
    const hasAttachments = formData.attachments.length > 0;
    
    let message = 'You will be redirected to the analyzer selection page where you can choose from different analysis tools.';
    
    if (hasAttachments) {
      message += '\n\n⚠️ Important: You will need to re-upload your files when you select a different analyzer.';
    }
    
    const userConfirmed = window.confirm(message);
    
    if (userConfirmed) {
      // Store case context without analyzer selection
      const caseContext = {
        caseTitle: formData.caseTitle,
        description: formData.description,
        product: formData.product,
        severity: formData.severity,
        attachments: formData.attachments.map(f => ({ name: f.name, size: f.size, type: f.type })),
        fromPortal: true,
        requiresReupload: hasAttachments
      };
      
      console.log('💾 Storing case context for analyzer selection:', caseContext);
      sessionStorage.setItem('caseContext', JSON.stringify(caseContext));
      
      // Navigate to analyzer selection page (without specific analyzer parameter)
      const targetUrl = '/products/deep-security';
      console.log('🚀 Navigating to analyzer selection page:', targetUrl);
      router.push(targetUrl);
    } else {
      console.log('❌ User cancelled choosing different analyzer');
    }
  };

  return (
    <div className="max-w-4xl mx-auto bg-white">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-black mb-6">
          Submit a request or inquiry with AI assistance
        </h1>
        
        <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <h2 className="text-lg font-medium text-blue-800">AI-Enhanced Case Creation</h2>
          </div>
          <p className="text-blue-700">
            Our AI assistant will help you create a comprehensive case with smart suggestions for title, 
            description quality assessment, and intelligent analyzer recommendations.
          </p>
        </div>
        
        <div className="mb-6">
          <h2 className="text-lg font-medium text-black mb-2">Account Associated with This Submission</h2>
          <p className="text-gray-800">AMEA House Account</p>
        </div>

        {/* Step 1: Choose a product */}
        <div className="border border-gray-200 rounded-lg mb-6 shadow-sm bg-white">
          <button
            onClick={() => toggleSection('product')}
            className="w-full flex items-center justify-between p-4 text-left bg-gray-50 hover:bg-gray-100 transition-colors rounded-t-lg"
          >
            <h3 className="text-lg font-medium text-black">1. Choose a product</h3>
            <svg
              className={`w-5 h-5 transition-transform ${expandedSections.product ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {expandedSections.product && (
            <div className="p-6 space-y-6">
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  <span className="text-red-500">*</span>Product
                </label>
                <select
                  value={formData.product}
                  onChange={(e) => handleInputChange('product', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-black bg-white"
                >
                  <option value="Deep Security">Deep Security</option>
                  <option value="Apex One">Apex One</option>
                  <option value="Cloud One">Cloud One</option>
                  <option value="Vision One">Vision One</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  <span className="text-red-500">*</span>Product version
                </label>
                <select
                  value={formData.productVersion}
                  onChange={(e) => handleInputChange('productVersion', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-black bg-white"
                >
                  <option value="20.0">20.0</option>
                  <option value="19.0">19.0</option>
                  <option value="18.0">18.0</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  <span className="text-red-500">*</span>Affected operating system
                </label>
                <select
                  value={formData.operatingSystem}
                  onChange={(e) => handleInputChange('operatingSystem', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-black bg-white"
                >
                  <option value="CentOS 5 32-bit">CentOS 5 32-bit</option>
                  <option value="Windows Server 2019">Windows Server 2019</option>
                  <option value="Ubuntu 20.04">Ubuntu 20.04</option>
                  <option value="Red Hat Enterprise Linux 8">Red Hat Enterprise Linux 8</option>
                </select>
              </div>
            </div>
          )}
        </div>

        {/* Step 2: Select an issue category */}
        <div className="border border-gray-200 rounded-lg mb-6 shadow-sm bg-white">
          <button
            onClick={() => toggleSection('issueCategory')}
            className="w-full flex items-center justify-between p-4 text-left bg-gray-50 hover:bg-gray-100 transition-colors rounded-t-lg"
          >
            <h3 className="text-lg font-medium text-black">2. Select an issue category</h3>
            <svg
              className={`w-5 h-5 transition-transform ${expandedSections.issueCategory ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {expandedSections.issueCategory && (
            <div className="p-6">
              <div>
                <label className="block text-sm font-medium text-black mb-4">
                  <span className="text-red-500">*</span>Issue category
                </label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {['Product Issue', 'Threat Issue', 'Account / Billing Issue', 'Compliancy Report'].map((category) => (
                    <button
                      key={category}
                      onClick={() => handleInputChange('issueCategory', category)}
                      className={`p-4 text-center border rounded-lg transition-colors ${
                        formData.issueCategory === category
                          ? 'border-red-500 bg-red-50 text-red-700'
                          : 'border-gray-300 bg-white text-black hover:bg-gray-50'
                      }`}
                    >
                      {category}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Step 3: Fill in request detail */}
        <div className="border border-gray-200 rounded-lg mb-6 shadow-sm bg-white">
          <button
            onClick={() => toggleSection('requestDetail')}
            className="w-full flex items-center justify-between p-4 text-left bg-gray-50 hover:bg-gray-100 transition-colors rounded-t-lg"
          >
            <h3 className="text-lg font-medium text-black">3. Fill in request detail</h3>
            <svg
              className={`w-5 h-5 transition-transform ${expandedSections.requestDetail ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {expandedSections.requestDetail && (
            <div className="p-6 space-y-6">
              {/* Smart Title Suggestion Component */}
              <SmartTitleSuggestion
                description={formData.description}
                product={formData.product}
                category={formData.issueCategory}
                severity={formData.severity}
                currentTitle={formData.caseTitle}
                onTitleSelect={(title) => handleInputChange('caseTitle', title)}
                onTitleChange={(title) => handleInputChange('caseTitle', title)}
              />

              {aiRecommendation && (
                <div 
                  ref={recommendationRef}
                  className="mt-6 bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-300 rounded-lg p-6 shadow-lg animate-pulse"
                >
                  <div className="flex items-start space-x-3">
                    <div className="text-3xl animate-bounce">{aiRecommendation.icon}</div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                        <span className="text-xl font-bold text-blue-700">🎉 AI Analysis Complete!</span>
                        <span className="px-3 py-1 text-sm bg-green-100 text-green-800 rounded-full font-medium">
                          {Math.round(aiRecommendation.confidence * 100)}% confidence
                        </span>
                      </div>
                      <h4 className="text-xl font-bold text-gray-800 mb-3">
                        Recommended: {aiRecommendation.analyzerName}
                      </h4>
                      <p className="text-gray-700 mb-6 text-lg">{aiRecommendation.reasoning}</p>
                      <div className="flex space-x-4">
                        <button
                          onClick={proceedWithAnalyzer}
                          disabled={isAnalyzing}
                          className="bg-gradient-to-r from-green-600 to-blue-600 text-white px-8 py-4 rounded-lg hover:from-green-700 hover:to-blue-700 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl text-lg font-semibold flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                        >
                          {isAnalyzing ? (
                            <>
                              <svg className="w-6 h-6 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                              </svg>
                              <span>Processing Files & Starting Analysis...</span>
                            </>
                          ) : (
                            <>
                              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                              </svg>
                              <span>Start Analysis with {aiRecommendation.analyzerName}</span>
                            </>
                          )}
                        </button>
                        <button
                          onClick={handleChooseDifferentAnalyzer}
                          className="px-6 py-4 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-lg"
                        >
                          Choose Different Analyzer
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-black mb-4">
                  <span className="text-red-500">*</span>Case severity level
                  <svg className="inline w-4 h-4 ml-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </label>
                <div className="flex space-x-6">
                  {['Low', 'Medium', 'High', 'Critical'].map((level) => (
                    <label key={level} className="flex items-center">
                      <input
                        type="radio"
                        name="severity"
                        value={level}
                        checked={formData.severity === level}
                        onChange={(e) => handleInputChange('severity', e.target.value)}
                        className="mr-2 text-blue-500 focus:ring-blue-500"
                      />
                      <span className="text-black">{level}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Description Assistant Component */}
              <DescriptionAssistant
                description={formData.description}
                product={formData.product}
                category={formData.issueCategory}
                severity={formData.severity}
                caseTitle={formData.caseTitle}
                onDescriptionChange={(description) => handleInputChange('description', description)}
              />

              <div data-section="attachments">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-medium text-black">Attachment</h4>
                  <div className="flex items-center space-x-2">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                      </svg>
                      ZIP Required for Intellicket
                    </span>
                  </div>
                </div>
                
                <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-start space-x-2">
                    <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div className="text-sm">
                      <p className="text-blue-800 font-medium mb-1">📦 Intellicket Analysis Requirements:</p>
                      <ul className="text-blue-700 space-y-1 text-xs">
                        <li>• <strong>ZIP files required</strong> for automated log extraction</li>
                        <li>• Diagnostic Package.zip recommended for best results</li>
                        <li>• Individual .log/.xml files supported but limited analysis</li>
                      </ul>
                      <p className="text-blue-600 text-xs mt-2">
                        💡 <button 
                          onClick={() => setShowLogCollectionModal(true)}
                          className="underline hover:text-blue-800 bg-transparent border-none cursor-pointer"
                        >
                          Log Collection Guide
                        </button>
                      </p>
                    </div>
                  </div>
                </div>

                <div className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  formData.attachments.some(f => f.name.toLowerCase().endsWith('.zip')) 
                    ? 'border-green-300 bg-green-50' 
                    : 'border-gray-300 hover:border-blue-400'
                }`}>
                  <input
                    type="file"
                    multiple
                    onChange={(e) => handleFileUpload(e.target.files)}
                    className="hidden"
                    id="file-upload"
                    accept=".log,.txt,.xml,.csv,.zip,.pdf"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    {formData.attachments.some(f => f.name.toLowerCase().endsWith('.zip')) ? (
                      <svg className="w-12 h-12 text-green-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    ) : (
                      <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                    )}
                    <p className="text-black mb-2">
                      {formData.attachments.some(f => f.name.toLowerCase().endsWith('.zip')) 
                        ? '✅ ZIP files detected - Ready for Intellicket!'
                        : 'Add files or drag files here'
                      }
                    </p>
                    <p className="text-sm text-gray-600">
                      {formData.attachments.some(f => f.name.toLowerCase().endsWith('.zip'))
                        ? 'You can add more files if needed'
                        : 'Recommended: Diagnostic Package.zip for best analysis'
                      }
                    </p>
                    <p className="text-xs text-gray-500 mt-1">File Size Limit: 1GB per file</p>
                  </label>
                </div>

                {/* Display uploaded files */}
                {formData.attachments.length > 0 && (
                  <div className="mt-4 space-y-2">
                    <h5 className="text-sm font-medium text-black">Uploaded Files:</h5>
                    {formData.attachments.map((file, index) => (
                      <div key={index} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                        <div className="flex items-center space-x-2">
                          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          <span className="text-sm text-gray-700">{file.name}</span>
                          <span className="text-xs text-gray-500">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                        </div>
                        <button
                          onClick={() => removeAttachment(index)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-black mb-2">CC Email</label>
                <input
                  type="email"
                  value={formData.ccEmail}
                  onChange={(e) => handleInputChange('ccEmail', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-black bg-white placeholder-gray-500"
                  placeholder="ex.abc@trendmicro.com"
                />
              </div>

              {/* Validation hint */}
              {(!formData.description.trim() || !formData.severity) && (
                <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.732 15.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                    <span className="text-sm text-gray-900">
                      Please complete: 
                      {!formData.description.trim() && ' Description'}
                      {(!formData.description.trim() && !formData.severity) && ' and'}
                      {!formData.severity && ' Severity Level'}
                    </span>
                  </div>
                </div>
              )}

              {/* ZIP File Status Indicator */}
              {formData.description.trim() && formData.severity && (
                <div className="mb-4">
                  {formData.attachments.some(f => f.name.toLowerCase().endsWith('.zip')) ? (
                    <div className="flex items-center space-x-2 text-green-700 bg-green-50 border border-green-200 rounded-lg p-3">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="text-sm font-medium">✅ ZIP files detected - Ready for optimal Intellicket analysis!</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2 text-amber-700 bg-amber-50 border border-amber-200 rounded-lg p-3">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                      </svg>
                      <div className="text-sm">
                        <span className="font-medium">⚠️ No ZIP files attached</span>
                        <span className="text-amber-600 ml-1">- Analysis will be limited without diagnostic files</span>
                      </div>
                    </div>
                  )}
                </div>
              )}

              <div className="flex space-x-4 pt-6">
                <button 
                  onClick={() => router.push('/')}
                  className="px-8 py-3 border border-gray-300 text-black rounded-md hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button 
                  onClick={handleSubmitTraditionalCase}
                  disabled={!formData.description.trim() || !formData.severity}
                  className="px-8 py-3 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Submit Traditional Case
                </button>
                <button 
                  onClick={handleSubmitToIntellicket}
                  disabled={isAnalyzing || !formData.description.trim() || !formData.severity}
                  className="relative px-8 py-3 bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-500 text-white rounded-md hover:from-purple-700 hover:via-blue-700 hover:to-cyan-600 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl group overflow-hidden disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 via-blue-600/20 to-cyan-500/20 animate-pulse"></div>
                  <div className="relative flex items-center space-x-2">
                    {isAnalyzing ? (
                      <>
                        <svg className="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        <span className="font-semibold">Analyzing with AI...</span>
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                        <span className="font-semibold">Submit to Intellicket</span>
                        <div className="absolute -top-1 -right-1 w-2 h-2 bg-cyan-300 rounded-full animate-ping"></div>
                      </>
                    )}
                  </div>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Log Collection Guide Modal */}
      {showLogCollectionModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                  📦 Deep Security Diagnostic Package Collection Guide
                </h2>
                <button
                  onClick={() => setShowLogCollectionModal(false)}
                  className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
                >
                  ×
                </button>
              </div>

              <div className="space-y-6">
                {/* Overview */}
                <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-blue-700">
                        <strong>Important:</strong> Diagnostic packages contain comprehensive system logs required for effective analysis. 
                        ZIP files ensure all related logs are collected together with proper file structure.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Deep Security Manager */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    🖥️ Deep Security Manager (DSM)
                  </h3>
                  <div className="space-y-3">
                    <div>
                      <h4 className="font-medium text-gray-800 mb-2">Via Web Console:</h4>
                      <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600 ml-4">
                        <li>Log in to the Deep Security Manager console</li>
                        <li>Navigate to <strong>Administration → System Information</strong></li>
                        <li>Click <strong>&quot;Create Diagnostic Package&quot;</strong></li>
                        <li>Select components to include (Manager, Database, etc.)</li>
                        <li>Click <strong>&quot;Generate&quot;</strong> and wait for completion</li>
                        <li>Download the generated ZIP file</li>
                      </ol>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-800 mb-2">Via Command Line:</h4>
                      <div className="bg-black text-green-400 rounded p-3 font-mono text-sm">
                        <p className="mb-2 text-white"><strong>Windows:</strong></p>
                        <div className="text-green-400">
                          <div>C:\&gt; cd &quot;C:\Program Files\Trend Micro\Deep Security Manager&quot;</div>
                          <div>C:\Program Files\Trend Micro\Deep Security Manager&gt; dsm_c.cmd -action creatediagnosticpackage -filename diagnostic.zip</div>
                        </div>
                        <p className="mt-3 mb-2 text-white"><strong>Linux:</strong></p>
                        <div className="text-green-400">
                          <div>$ cd /opt/dsm</div>
                          <div>$ ./dsm_c -action creatediagnosticpackage -filename diagnostic.zip</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Deep Security Agent */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    🛡️ Deep Security Agent (DSA)
                  </h3>
                  <div className="space-y-3">
                    <div>
                      <h4 className="font-medium text-gray-800 mb-2">Windows Command Line:</h4>
                      <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600 ml-4 mb-3">
                        <li>Open Command Prompt as Administrator</li>
                        <li>Navigate to Deep Security Agent installation directory</li>
                        <li>Run the diagnostic command</li>
                        <li>Wait for package creation to complete</li>
                      </ol>
                      <div className="bg-black text-green-400 rounded p-3 font-mono text-sm">
                        <div className="text-green-400">
                          <div>C:\&gt; cd &quot;C:\Program Files\Trend Micro\Deep Security Agent&quot;</div>
                          <div>C:\Program Files\Trend Micro\Deep Security Agent&gt; dsa_control.exe -d</div>
                          <div className="text-yellow-400 mt-1"># Diagnostic package will be created in the current directory</div>
                        </div>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-800 mb-2">Linux Command Line:</h4>
                      <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600 ml-4 mb-3">
                        <li>Open terminal with sudo privileges</li>
                        <li>Navigate to Deep Security Agent directory</li>
                        <li>Execute the diagnostic command</li>
                        <li>Package will be saved to current directory</li>
                      </ol>
                      <div className="bg-black text-green-400 rounded p-3 font-mono text-sm">
                        <div className="text-green-400">
                          <div>$ cd /opt/ds_agent</div>
                          <div>$ sudo ./dsa_control -d</div>
                          <div className="text-yellow-400 mt-1"># Diagnostic package created successfully</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Deep Security Virtual Appliance */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    💿 Deep Security Virtual Appliance (DSVA)
                  </h3>
                  <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600 ml-4">
                    <li>Access the DSVA management interface</li>
                    <li>Navigate to <strong>System → Diagnostic Package</strong></li>
                    <li>Click <strong>&quot;Generate Diagnostic Package&quot;</strong></li>
                    <li>Select log types and time range</li>
                    <li>Download the generated ZIP file</li>
                  </ol>
                </div>

                {/* What's Included */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    📋 What&apos;s Included in Diagnostic Packages
                  </h3>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-medium text-gray-800 mb-2">System Information:</h4>
                      <ul className="list-disc list-inside space-y-1 text-sm text-gray-600 ml-4">
                        <li>Configuration files</li>
                        <li>System specifications</li>
                        <li>Network settings</li>
                        <li>Service status</li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-800 mb-2">Log Files:</h4>
                      <ul className="list-disc list-inside space-y-1 text-sm text-gray-600 ml-4">
                        <li>Application logs</li>
                        <li>Security event logs</li>
                        <li>Anti-malware scan logs</li>
                        <li>Performance data</li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Best Practices */}
                <div className="bg-green-50 border-l-4 border-green-400 p-4">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <h4 className="text-sm font-medium text-green-700 mb-2">Best Practices:</h4>
                      <ul className="list-disc list-inside space-y-1 text-sm text-green-600 ml-4">
                        <li>Generate diagnostic packages during or immediately after issues occur</li>
                        <li>Include time range covering the problem period</li>
                        <li>Collect from all affected components (Manager, Agent, etc.)</li>
                        <li>Verify ZIP file integrity before submitting</li>
                        <li>Keep diagnostic packages secure - they contain system information</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setShowLogCollectionModal(false)}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Got it, thanks!
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Success Modal for Traditional Case Submission */}
      {showSuccessModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="p-6 text-center">
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-4">
                <svg className="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Case Submitted Successfully! 🎉
              </h3>
              
              <div className="bg-gray-50 rounded-lg p-4 mb-4">
                <p className="text-sm text-gray-600 mb-2">Your ticket number is:</p>
                <div className="text-2xl font-bold text-blue-600 font-mono bg-white rounded border-2 border-blue-200 p-3">
                  {ticketNumber}
                </div>
              </div>
              
              <div className="text-sm text-gray-600 mb-6 space-y-2">
                <p>📧 A confirmation email will be sent shortly</p>
                <p>⏱️ Expected response time: 1-2 business days</p>
                <p>🔍 You can track your case using the ticket number above</p>
              </div>
              
              <div className="space-y-3">
                <button
                  onClick={() => {
                    setShowSuccessModal(false);
                    // Reset all form states
                    setFormData({
                      product: 'Deep Security',
                      productVersion: '20.0',
                      operatingSystem: 'CentOS 5 32-bit',
                      issueCategory: 'Product Issue',
                      caseTitle: '',
                      severity: '',
                      description: '',
                      ccEmail: '',
                      attachments: []
                    });
                    setTicketNumber('');
                    setAiRecommendation(null);
                    setIsAnalyzing(false);
                    
                    // CRITICAL FIX: Clear file input value to prevent upload issues
                    const fileInput = document.getElementById('file-upload') as HTMLInputElement;
                    if (fileInput) {
                      fileInput.value = '';
                      console.log('🔄 File input cleared after form reset');
                    }
                    
                    // Clear any stored case context from previous submissions
                    sessionStorage.removeItem('caseContext');
                    console.log('✅ Form completely reset for new case creation');
                  }}
                  className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
                >
                  Create Another Case
                </button>
                
                <button
                  onClick={() => {
                    setShowSuccessModal(false);
                    router.push('/');
                  }}
                  className="w-full px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Return to Home
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
