# Intellicket Frontend Implementation Guide
*Technical Implementation Instructions for AI Agents*

## Quick Start Implementation Template

### Step 1: Basic Page Structure Template
```typescript
'use client'

import React, { useState, useCallback } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  // Import analyzer-specific icons
  Brain,
  Shield,
  ArrowLeft,
  // Add other required icons
} from 'lucide-react'

// Define interfaces matching backend API
interface AnalyzerResult {
  // Match your backend response structure
}

export default function AnalyzerPage() {
  // State management
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<AnalyzerResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Products array for footer
  const products = [
    { id: 'deep-security', name: 'Deep Security', icon: '🛡️' },
    { id: 'apex-one', name: 'Apex One', icon: '🔒' },
    { id: 'vision-one', name: 'Vision One', icon: '👁️' },
    { id: 'service-gateway', name: 'Service Gateway', icon: '🌐' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-red-950/10 to-gray-950 relative overflow-hidden">
      {/* Background Animation */}
      <div className="absolute inset-0 opacity-15">
        <div className="absolute top-20 left-20 w-96 h-96 bg-red-500 rounded-full mix-blend-multiply filter blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-orange-500 rounded-full mix-blend-multiply filter blur-3xl animate-pulse animation-delay-2000"></div>
      </div>

      {/* Header */}
      <header className="relative z-10 bg-black/40 backdrop-blur-sm border-b border-red-500/30">
        {/* Header content */}
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 py-12">
        {/* Page content */}
      </main>

      {/* Footer */}
      <footer className="relative z-10 bg-black/40 backdrop-blur-sm border-t border-white/10 text-white py-12">
        {/* Footer content */}
      </footer>
    </div>
  )
}
```

### Step 2: Header Implementation
```typescript
<header className="relative z-10 bg-black/40 backdrop-blur-sm border-b border-red-500/30">
  <div className="max-w-7xl mx-auto px-4 py-4">
    <div className="flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <Link 
          href="/"
          className="flex items-center space-x-3 hover:opacity-80 transition-opacity"
        >
          <Image 
            src="/trendlogo.png" 
            alt="Trend Micro Logo" 
            width={40}
            height={40}
            className="h-10 w-auto"
          />
          <div className="border-l border-white/30 pl-3">
            <div className="text-xl font-bold text-red-400">Intellicket</div>
            <div className="text-xs text-gray-400">AI Support Platform</div>
          </div>
        </Link>
        <span className="text-gray-500">→</span>
        <div className="flex items-center space-x-2">
          <span className="text-2xl">🛡️</span>
          <span className="text-white font-semibold">Deep Security</span>
        </div>
        <span className="text-gray-500">→</span>
        <div className="flex items-center space-x-2">
          <Brain className="h-5 w-5 text-purple-400" />
          <span className="text-gray-300 font-medium">[ANALYZER NAME]</span>
        </div>
      </div>
      <Link
        href="/products/deep-security"
        className="bg-red-500/20 text-red-300 px-6 py-2 rounded-xl hover:bg-red-500/30 transition-all duration-300 border border-red-500/30 flex items-center gap-2"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Analyzers
      </Link>
    </div>
  </div>
</header>
```

### Step 3: Page Title Section
```typescript
<div className="text-center mb-16">
  <div className="flex items-center justify-center gap-4 mb-6">
    <Link href="/products/deep-security" className="transition-transform hover:scale-105">
      <Image
        src="/trendlogo.png"
        alt="Trend Micro"
        width={60}
        height={60}
        className="drop-shadow-2xl"
      />
    </Link>
    <div className="h-12 w-px bg-gradient-to-b from-transparent via-red-500/50 to-transparent" />
    <div className="relative">
      <Shield className="h-12 w-12 text-red-500 drop-shadow-lg" />
      <div className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center animate-pulse">
        <Brain className="h-3 w-3 text-white" />
      </div>
    </div>
  </div>
  
  <div className="mb-6">
    <h1 className="text-6xl font-bold bg-gradient-to-r from-white via-gray-200 to-red-300 bg-clip-text text-transparent mb-2">
      [ANALYZER NAME] Analyzer
    </h1>
    <div className="flex items-center justify-center gap-2 mb-4">
      <Badge className="bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-blue-300 border-blue-500/30 px-3 py-1">
        <Brain className="h-3 w-3 mr-1" />
        AI-Powered
      </Badge>
      {/* Add more relevant badges */}
    </div>
    <p className="text-xl text-gray-300 max-w-4xl mx-auto leading-relaxed">
      [ANALYZER DESCRIPTION]
    </p>
  </div>
</div>
```

### Step 4: Upload Area Implementation
```typescript
{!analysisResult && (
  <div className="space-y-12">
    {/* File Requirements */}
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-white mb-4">Select Your Log Files</h2>
        <p className="text-gray-400 text-sm">Choose the [ANALYZER SPECIFIC] files you want to analyze</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {/* File requirement cards */}
        <div className="text-center p-4 bg-white/5 rounded-xl border border-green-500/20 hover:border-green-500/40 transition-colors">
          <FileText className="h-8 w-8 text-green-400 mx-auto mb-2" />
          <div className="font-semibold text-white text-sm">[FILE_NAME]</div>
          <Badge className="bg-green-500/20 text-green-300 border-green-500/30 text-xs mt-1">Required</Badge>
        </div>
        {/* Repeat for other files */}
      </div>
    </div>

    {/* Upload Area */}
    <div className="max-w-2xl mx-auto">
      <div className="relative">
        <label className="block w-full cursor-pointer group">
          <div className="relative bg-white/5 backdrop-blur-sm border-2 border-dashed border-gray-600 rounded-3xl p-12 hover:border-red-500/50 hover:bg-red-500/5 transition-all duration-500 group">
            <div className="absolute inset-0 bg-gradient-to-br from-red-500/0 to-red-500/0 group-hover:from-red-500/5 group-hover:to-red-500/10 rounded-3xl transition-all duration-500"></div>
            
            <div className="relative text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-gray-600 to-gray-700 group-hover:from-red-500 group-hover:to-red-600 rounded-2xl mx-auto mb-6 flex items-center justify-center transition-all duration-500 group-hover:scale-110">
                <Upload className="h-10 w-10 text-white" />
              </div>
              
              <div className="space-y-2">
                <h3 className="text-2xl font-bold text-white group-hover:text-red-200 transition-colors">
                  <span className="text-red-400 group-hover:text-red-300">Drag & Drop</span> or <span className="text-red-400 group-hover:text-red-300">Click to Select</span>
                </h3>
                <p className="text-gray-400 group-hover:text-gray-300 transition-colors">
                  [ANALYZER SPECIFIC] files for AI-powered analysis
                </p>
              </div>
              
              <div className="mt-6 flex items-center justify-center gap-6 text-sm text-gray-500">
                {/* Supported file types */}
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>.log</span>
                </div>
                {/* Add more file types */}
              </div>
            </div>
          </div>
          
          <input
            type="file"
            className="hidden"
            multiple
            accept=".log,.txt,.zip"
            onChange={(e) => handleFileSelect(e.target.files)}
            id="file-upload"
          />
        </label>
      </div>

      {/* Selected Files Display */}
      {selectedFiles.length > 0 && (
        <div className="mt-8 max-w-2xl mx-auto">
          <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Selected Files</h3>
              <Badge className="bg-green-500/20 text-green-300 border-green-500/30">
                {selectedFiles.length} file{selectedFiles.length !== 1 ? 's' : ''}
              </Badge>
            </div>
            
            <div className="space-y-3">
              {Array.from(selectedFiles).map((file, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10 hover:border-white/20 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                      <FileText className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <div className="font-medium text-white">{file.name}</div>
                      <div className="text-sm text-gray-400">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => removeFile(index)}
                    className="p-2 hover:bg-red-500/20 rounded-lg transition-colors group"
                    title="Remove file"
                  >
                    <X className="h-4 w-4 text-gray-400 group-hover:text-red-400" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Analysis Button */}
      {selectedFiles.length > 0 && (
        <div className="text-center mt-8">
          <button
            onClick={handleAnalysis}
            disabled={isAnalyzing}
            className="group relative inline-flex items-center justify-center px-12 py-4 text-lg font-semibold text-white bg-gradient-to-r from-red-600 to-red-700 rounded-2xl hover:from-red-500 hover:to-red-600 focus:outline-none focus:ring-4 focus:ring-red-500/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 shadow-xl hover:shadow-red-500/25"
          >
            <div className="relative flex items-center gap-3">
              {isAnalyzing ? (
                <>
                  <div className="animate-spin h-6 w-6 border-2 border-white border-t-transparent rounded-full"></div>
                  <span>Analyzing with AI...</span>
                </>
              ) : (
                <>
                  <Brain className="h-6 w-6" />
                  <span>Start AI Analysis</span>
                </>
              )}
            </div>
          </button>
        </div>
      )}
    </div>
  </div>
)}
```

### Step 5: Analysis Results Template
```typescript
{analysisResult && (
  <div className="space-y-8">
    <div className="text-center mb-8">
      <div className="flex items-center justify-center gap-3 mb-4">
        <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-700 rounded-2xl flex items-center justify-center">
          <CheckCircle className="h-8 w-8 text-white" />
        </div>
        <div className="h-12 w-px bg-gradient-to-b from-transparent via-green-500/50 to-transparent" />
        <div className="flex flex-col items-start">
          <div className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-blue-400" />
            <Target className="h-4 w-4 text-purple-400" />
            <Shield className="h-4 w-4 text-green-400" />
          </div>
        </div>
      </div>
      
      <h2 className="text-4xl font-bold bg-gradient-to-r from-white via-green-200 to-green-400 bg-clip-text text-transparent mb-3">
        Analysis Results
      </h2>
      
      <div className="flex items-center justify-center gap-4 mb-4">
        <Badge className="bg-green-500/20 text-green-300 border-green-500/30 px-4 py-2">
          <CheckCircle className="h-4 w-4 mr-2" />
          Analysis Complete
        </Badge>
        {/* Add confidence score badge if available */}
      </div>
      
      <p className="text-gray-300 max-w-3xl mx-auto">
        Comprehensive [ANALYZER NAME] analysis powered by AI, ML, and RAG technologies. 
        Results include [SPECIFIC ANALYSIS FEATURES].
      </p>
    </div>

    {/* Results Cards */}
    <Card className="bg-white/10 backdrop-blur-sm border-white/20 hover:border-blue-500/40 transition-all duration-300">
      <CardHeader className="pb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-700 rounded-xl flex items-center justify-center">
            <Info className="h-6 w-6 text-white" />
          </div>
          <div>
            <CardTitle className="text-white text-xl">[CARD TITLE]</CardTitle>
            <CardDescription className="text-gray-300">[CARD DESCRIPTION]</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Card content based on analysis results */}
      </CardContent>
    </Card>

    {/* New Analysis Button */}
    <div className="text-center pt-8">
      <Button
        onClick={() => {
          setAnalysisResult(null)
          setSelectedFiles([])
          setError(null)
        }}
        variant="outline"
        className="bg-white/10 border-white/20 text-white hover:bg-white/20 hover:border-white/30 transition-all duration-300"
      >
        Analyze New Files
      </Button>
    </div>
  </div>
)}
```

### Step 6: Footer Implementation (Use Exact Copy)
```typescript
<footer className="relative z-10 bg-black/40 backdrop-blur-sm border-t border-white/10 text-white py-12">
  <div className="max-w-7xl mx-auto px-4">
    <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
      <div className="md:col-span-2">
        <div className="flex items-center space-x-4 mb-4">
          <Image 
            src="/trendlogo.png" 
            alt="Trend Micro Logo" 
            width={32}
            height={32}
            className="h-8 w-auto"
          />
          <div className="border-l border-white/30 pl-4">
            <h3 className="text-xl font-bold text-white">Intellicket</h3>
            <p className="text-xs text-red-400 font-medium">AI Support Platform</p>
          </div>
        </div>
        <p className="text-gray-300 mb-4 max-w-md">
          Intelligent support system for Trend Micro products. Secure your digital world with AI-powered cybersecurity solutions.
        </p>
        <div className="flex space-x-4">
          <a href="#" className="text-gray-400 hover:text-red-400 transition-colors">
            <span className="sr-only">Twitter</span>
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M6.29 18.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0020 3.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.073 4.073 0 01.8 7.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 010 16.407a11.616 11.616 0 006.29 1.84" />
            </svg>
          </a>
          <a href="#" className="text-gray-400 hover:text-red-400 transition-colors">
            <span className="sr-only">LinkedIn</span>
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.338 16.338H13.67V12.16c0-.995-.017-2.277-1.387-2.277-1.39 0-1.601 1.086-1.601 2.207v4.248H8.014v-8.59h2.559v1.174h.037c.356-.675 1.227-1.387 2.526-1.387 2.703 0 3.203 1.778 3.203 4.092v4.711zM5.005 6.575a1.548 1.548 0 11-.003-3.096 1.548 1.548 0 01.003 3.096zm-1.337 9.763H6.34v-8.59H3.667v8.59zM17.668 1H2.328C1.595 1 1 1.581 1 2.298v15.403C1 18.418 1.595 19 2.328 19h15.34c.734 0 1.332-.582 1.332-1.299V2.298C19 1.581 18.402 1 17.668 1z" clipRule="evenodd" />
            </svg>
          </a>
        </div>
      </div>
      <div>
        <h3 className="text-lg font-semibold mb-4 text-red-400">Quick Links</h3>
        <ul className="space-y-3 text-gray-300">
          <li><a href="#" className="hover:text-white transition-colors duration-300 flex items-center"><span className="w-1 h-1 bg-red-500 rounded-full mr-2"></span>Support Center</a></li>
          <li><a href="#" className="hover:text-white transition-colors duration-300 flex items-center"><span className="w-1 h-1 bg-red-500 rounded-full mr-2"></span>Documentation</a></li>
          <li><a href="#" className="hover:text-white transition-colors duration-300 flex items-center"><span className="w-1 h-1 bg-red-500 rounded-full mr-2"></span>Contact Us</a></li>
          <li><a href="#" className="hover:text-white transition-colors duration-300 flex items-center"><span className="w-1 h-1 bg-red-500 rounded-full mr-2"></span>Security Blog</a></li>
        </ul>
      </div>
      <div>
        <h3 className="text-lg font-semibold mb-4 text-red-400">Products</h3>
        <ul className="space-y-3 text-gray-300">
          {products.map((product) => (
            <li key={product.id}>
              <Link 
                href={`/products/${product.id}`}
                className="hover:text-white transition-colors duration-300 text-left flex items-center"
              >
                <span className="text-lg mr-2">{product.icon}</span>
                {product.name}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
    <div className="border-t border-white/20 mt-12 pt-8">
      <div className="flex flex-col md:flex-row justify-between items-center">
        <p className="text-gray-400 text-sm">
          &copy; 2025 Intellicket - AI-Powered Cybersecurity Platform. All rights reserved. | Securing your digital transformation.
        </p>
        <div className="flex space-x-6 mt-4 md:mt-0">
          <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Privacy Policy</a>
          <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Terms of Service</a>
          <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Security</a>
        </div>
      </div>
    </div>
  </div>
</footer>
```

## Common Event Handlers Template

### File Handling
```typescript
const handleFileSelect = useCallback((files: FileList | null) => {
  if (files) {
    const fileArray = Array.from(files)
    setSelectedFiles(fileArray)
  }
}, [])

const removeFile = useCallback((index: number) => {
  setSelectedFiles(prev => prev.filter((_, i) => i !== index))
}, [])
```

### Analysis Function Template
```typescript
const handleAnalysis = async () => {
  if (selectedFiles.length === 0) return
  
  setIsAnalyzing(true)
  setError(null)
  
  try {
    const formData = new FormData()
    selectedFiles.forEach((file, index) => {
      formData.append(`file${index}`, file)
    })
    formData.append('analysis_type', '[ANALYZER_TYPE]')
    
    // Upload files
    const uploadResponse = await fetch('/api/csdai/[ANALYZER_ENDPOINT]/upload', {
      method: 'POST',
      body: formData,
    })
    
    if (!uploadResponse.ok) {
      throw new Error('Upload failed')
    }
    
    const uploadResult = await uploadResponse.json()
    const sessionId = uploadResult.session_id
    
    // Poll for results
    const pollResults = async () => {
      let attempts = 0
      const maxAttempts = 60
      
      while (attempts < maxAttempts) {
        try {
          const statusResponse = await fetch(`/api/csdai/[ANALYZER_ENDPOINT]/status/${sessionId}`)
          const statusResult = await statusResponse.json()
          
          if (statusResult.status === 'completed') {
            const resultsResponse = await fetch(`/api/csdai/[ANALYZER_ENDPOINT]/results/${sessionId}`)
            const results = await resultsResponse.json()
            
            setAnalysisResult(results)
            setIsAnalyzing(false)
            return
          } else if (statusResult.status === 'error') {
            throw new Error(statusResult.error || 'Analysis failed')
          } else if (attempts < maxAttempts) {
            attempts++
            setTimeout(pollResults, 2000)
          } else {
            throw new Error('Analysis timeout')
          }
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Unknown error occurred')
          setIsAnalyzing(false)
          return
        }
      }
    }
    
    pollResults()
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Analysis failed')
    setIsAnalyzing(false)
  }
}
```

## Customization Checklist for New Analyzers

### Required Replacements
- [ ] `[ANALYZER NAME]` - Replace with actual analyzer name
- [ ] `[ANALYZER_DESCRIPTION]` - Replace with analyzer description
- [ ] `[ANALYZER_TYPE]` - Replace with backend analyzer type
- [ ] `[ANALYZER_ENDPOINT]` - Replace with API endpoint path
- [ ] `[FILE_NAME]` - Replace with required file names
- [ ] `[ANALYZER SPECIFIC]` - Replace with analyzer-specific text
- [ ] Icon imports - Add analyzer-specific icons
- [ ] Interface definitions - Match backend response structure
- [ ] File requirement cards - Update for analyzer's file types
- [ ] Supported file types - Update accept attribute and display

### Styling Consistency Checks
- [ ] All gradients use brand colors (red, blue, purple, green)
- [ ] All cards have `bg-white/10 backdrop-blur-sm border-white/20`
- [ ] All hover effects use consistent timing (`transition-all duration-300`)
- [ ] All buttons follow the primary button pattern
- [ ] Background animation uses the floating orbs pattern
- [ ] Header and footer are exact copies with only breadcrumb changes
- [ ] Typography follows the hierarchy system
- [ ] Spacing uses consistent scale (px-4, py-8, space-y-8, etc.)

### Testing Requirements
- [ ] Build compiles without errors
- [ ] Responsive design works on mobile/tablet/desktop
- [ ] All hover states function correctly
- [ ] File upload and analysis flow works
- [ ] Navigation buttons work correctly
- [ ] Error states display properly
- [ ] Loading states show appropriate feedback

This implementation guide provides AI agents with concrete, copy-paste templates and clear customization instructions to maintain design consistency across all Intellicket analyzer pages.