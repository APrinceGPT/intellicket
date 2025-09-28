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
    requestDetail: true
  });

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [aiRecommendation, setAiRecommendation] = useState<AnalyzerRecommendation | null>(null);

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
    if (files) {
      const fileArray = Array.from(files);
      setFormData(prev => ({
        ...prev,
        attachments: [...prev.attachments, ...fileArray]
      }));
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

    if (!formData.description.trim()) {
      alert('Please provide a description for AI analysis');
      return;
    }

    if (!formData.severity) {
      alert('Please select a severity level');
      return;
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

          // Navigate to the analyzer page
          const analyzerParam = `?analyzer=${aiRecommendation.analyzerId}&autoUploaded=true`;
          const targetUrl = `/products/deep-security${analyzerParam}`;
          
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
          
          const analyzerParam = `?analyzer=${aiRecommendation.analyzerId}`;
          const targetUrl = `/products/deep-security${analyzerParam}`;
          
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
        
        const analyzerParam = `?analyzer=${aiRecommendation.analyzerId}`;
        const targetUrl = `/products/deep-security${analyzerParam}`;
        
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

      // Navigate to the deep-security page with the recommended analyzer
      const analyzerParam = `?analyzer=${aiRecommendation.analyzerId}`;
      const targetUrl = `/products/deep-security${analyzerParam}`;
      
      console.log('🚀 Navigating to:', targetUrl);
      router.push(targetUrl);
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

              <div>
                <h4 className="text-sm font-medium text-black mb-3">Attachment</h4>
                <p className="text-sm text-gray-800 mb-4">
                  For faster processing, please capture logs for your product by following{' '}
                  <a href="#" className="text-blue-600 underline">these steps</a> Or, directly access the{' '}
                  <a href="#" className="text-blue-600 underline">Case Diagnostic Tool</a>
                </p>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                  <input
                    type="file"
                    multiple
                    onChange={(e) => handleFileUpload(e.target.files)}
                    className="hidden"
                    id="file-upload"
                    accept=".log,.txt,.xml,.csv,.zip,.pdf"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <p className="text-black mb-2">Add file or drag files here</p>
                    <p className="text-sm text-gray-800">File Size Limit: 1GB</p>
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

              <div className="flex space-x-4 pt-6">
                <button 
                  onClick={() => router.push('/')}
                  className="px-8 py-3 border border-gray-300 text-black rounded-md hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button className="px-8 py-3 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors">
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
    </div>
  );
}
