// Portal type definitions

export interface CaseFormData {
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

export interface AnalyzerRecommendation {
  analyzerId: string;
  analyzerName: string;
  confidence: number;
  reasoning: string;
  icon: string;
}

export interface CaseContext {
  caseTitle: string;
  description: string;
  product: string;
  severity: string;
  attachments: {
    name: string;
    size: number;
    type: string;
  }[];
}

export interface AnalyzerDefinition {
  id: string;
  name: string;
  description: string;
  icon: string;
  keywords: string[];
  categories: string[];
  products: string[];
}

export interface PortalSettings {
  enableAIAnalysis: boolean;
  defaultProduct: string;
  maxFileSize: number;
  allowedFileTypes: string[];
}
