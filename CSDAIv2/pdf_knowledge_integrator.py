# -*- coding: utf-8 -*-
"""
Enhanced PDF Knowledge Integration for Dynamic RAG
Processes proprietary Deep Security documentation for expert analysis
"""

import os
import re
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ PyPDF2 not available - PDF processing disabled")

class PDFKnowledgeIntegrator:
    """Integrates proprietary Deep Security PDF knowledge with Dynamic RAG"""
    
    def __init__(self, pdf_dir: str = "pdf", db_path: str = "knowledge_base/ds_knowledge.db"):
        self.pdf_dir = pdf_dir
        self.db_path = db_path
        self.knowledge_base = {}
        self.patterns = {}
        
        # Ensure knowledge base directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize or load knowledge base
        self.init_knowledge_db()
        
    def init_knowledge_db(self):
        """Initialize SQLite knowledge database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables for PDF knowledge
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pdf_documents (
                    id INTEGER PRIMARY KEY,
                    filename TEXT UNIQUE,
                    title TEXT,
                    processed_date TEXT,
                    page_count INTEGER,
                    content_hash TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pdf_sections (
                    id INTEGER PRIMARY KEY,
                    doc_id INTEGER,
                    section_title TEXT,
                    content TEXT,
                    page_number INTEGER,
                    section_type TEXT,
                    keywords TEXT,
                    FOREIGN KEY (doc_id) REFERENCES pdf_documents (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ds_patterns (
                    id INTEGER PRIMARY KEY,
                    pattern_name TEXT,
                    pattern_regex TEXT,
                    component TEXT,
                    severity TEXT,
                    resolution TEXT,
                    source_doc TEXT,
                    confidence_score REAL
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ PDF Knowledge database initialized")
            
        except Exception as e:
            print(f"⚠️ Knowledge DB initialization failed: {e}")
    
    def process_all_pdfs(self):
        """Process all PDF files in the pdf directory"""
        if not PDF_AVAILABLE:
            print("❌ PyPDF2 not available - cannot process PDFs")
            return
        
        pdf_files = [f for f in os.listdir(self.pdf_dir) if f.endswith('.pdf')]
        
        if not pdf_files:
            print("⚠️ No PDF files found in pdf directory")
            return
        
        print(f"🔍 Found {len(pdf_files)} PDF files to process:")
        for pdf_file in pdf_files:
            print(f"  📄 {pdf_file}")
        
        processed_count = 0
        for pdf_file in pdf_files:
            try:
                if self.process_single_pdf(pdf_file):
                    processed_count += 1
            except Exception as e:
                print(f"❌ Failed to process {pdf_file}: {e}")
        
        print(f"✅ Successfully processed {processed_count}/{len(pdf_files)} PDF files")
        self.build_knowledge_patterns()
        
    def process_single_pdf(self, filename: str) -> bool:
        """Process a single PDF file"""
        pdf_path = os.path.join(self.pdf_dir, filename)
        
        if not os.path.exists(pdf_path):
            print(f"❌ PDF file not found: {pdf_path}")
            return False
        
        try:
            # Check if already processed
            if self.is_pdf_processed(filename):
                print(f"✅ {filename} already processed, skipping")
                return True
            
            print(f"📖 Processing {filename}...")
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                print(f"  📄 Pages: {page_count}")
                
                # Extract metadata
                title = self.extract_title(filename, pdf_reader)
                
                # Store document info
                doc_id = self.store_document_info(filename, title, page_count)
                
                # Process content by sections
                current_section = ""
                section_content = ""
                page_num = 0
                
                for page in pdf_reader.pages:
                    page_num += 1
                    try:
                        text = page.extract_text()
                        if text.strip():
                            # Detect section headers
                            sections = self.detect_sections(text)
                            
                            if sections:
                                # Save previous section
                                if current_section and section_content:
                                    self.store_section(doc_id, current_section, section_content, page_num-1)
                                
                                # Start new section
                                current_section = sections[0]
                                section_content = text
                            else:
                                section_content += "\n" + text
                    
                    except Exception as e:
                        print(f"  ⚠️ Error processing page {page_num}: {e}")
                
                # Save final section
                if current_section and section_content:
                    self.store_section(doc_id, current_section, section_content, page_num)
                
                print(f"  ✅ {filename} processed successfully")
                return True
                
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            return False
    
    def extract_title(self, filename: str, pdf_reader) -> str:
        """Extract document title from PDF metadata or filename"""
        try:
            if pdf_reader.metadata and '/Title' in pdf_reader.metadata:
                return pdf_reader.metadata['/Title']
        except:
            pass
        
        # Fallback to filename-based title
        title_mapping = {
            'deepsecurity20.pdf': 'Deep Security 20 Official Documentation',
            'Deep Security 20 Training for Certified Professionals - eBook v1.pdf': 'DS20 Certified Professional Training v1',
            'Deep Security 20 Training for Certified Professionals v2 - eBook.pdf': 'DS20 Certified Professional Training v2',
            'Deep Security AMEA Partner Handbook1.5.pdf': 'Deep Security AMEA Partner Handbook',
            'Deep_Security_20_Best_Practice_Guide.pdf': 'Deep Security 20 Best Practices Guide',
            'DS20LabGuide.pdf': 'Deep Security 20 Lab Guide'
        }
        
        return title_mapping.get(filename, filename.replace('.pdf', '').replace('_', ' '))
    
    def detect_sections(self, text: str) -> List[str]:
        """Detect section headers in PDF text"""
        section_patterns = [
            r'^(Chapter \d+[:\-\s]+.*?)$',
            r'^(\d+\.\d*[:\-\s]+.*?)$',
            r'^([A-Z][A-Z\s]{10,}?)$',
            r'^(AMSP.*?)$',
            r'^(Anti-Malware.*?)$',
            r'^(Intrusion Prevention.*?)$',
            r'^(Web Reputation.*?)$',
            r'^(Application Control.*?)$',
            r'^(Integrity Monitoring.*?)$',
            r'^(Log Inspection.*?)$',
            r'^(Troubleshooting.*?)$',
            r'^(Best Practices.*?)$',
            r'^(Configuration.*?)$',
            r'^(Installation.*?)$',
            r'^(Deployment.*?)$'
        ]
        
        sections = []
        for line in text.split('\n'):
            line = line.strip()
            if len(line) > 5 and len(line) < 100:
                for pattern in section_patterns:
                    if re.match(pattern, line, re.IGNORECASE):
                        sections.append(line)
                        break
        
        return sections
    
    def store_document_info(self, filename: str, title: str, page_count: int) -> int:
        """Store document information and return document ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO pdf_documents 
                (filename, title, processed_date, page_count, content_hash)
                VALUES (?, ?, ?, ?, ?)
            ''', (filename, title, datetime.now().isoformat(), page_count, ""))
            
            doc_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return doc_id
            
        except Exception as e:
            print(f"❌ Error storing document info: {e}")
            return 0
    
    def store_section(self, doc_id: int, section_title: str, content: str, page_number: int):
        """Store section content in database"""
        try:
            # Classify section type
            section_type = self.classify_section_type(section_title, content)
            
            # Extract keywords
            keywords = self.extract_keywords(content)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO pdf_sections 
                (doc_id, section_title, content, page_number, section_type, keywords)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (doc_id, section_title, content, page_number, section_type, ', '.join(keywords)))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error storing section: {e}")
    
    def classify_section_type(self, title: str, content: str) -> str:
        """Classify section type based on title and content"""
        title_lower = title.lower()
        content_lower = content.lower()
        
        if any(word in title_lower for word in ['troubleshoot', 'problem', 'issue', 'error']):
            return 'troubleshooting'
        elif any(word in title_lower for word in ['best practice', 'recommend', 'guide']):
            return 'best_practices'
        elif any(word in title_lower for word in ['config', 'setup', 'install']):
            return 'configuration'
        elif any(word in title_lower for word in ['amsp', 'anti-malware', 'scan']):
            return 'amsp'
        elif any(word in title_lower for word in ['intrusion', 'ips', 'prevention']):
            return 'intrusion_prevention'
        elif any(word in title_lower for word in ['web reputation', 'url', 'web']):
            return 'web_reputation'
        elif any(word in title_lower for word in ['integrity', 'fim', 'file']):
            return 'integrity_monitoring'
        else:
            return 'general'
    
    def extract_keywords(self, content: str) -> List[str]:
        """Extract key terms from content"""
        # Deep Security specific keywords
        ds_keywords = {
            'amsp', 'anti-malware', 'scan engine', 'ips', 'intrusion prevention',
            'web reputation', 'application control', 'integrity monitoring', 'log inspection',
            'dsm', 'deep security manager', 'agent', 'policy', 'rule', 'event', 'alert',
            'threat', 'malware', 'virus', 'trojan', 'worm', 'spyware', 'adware',
            'performance', 'exclusion', 'whitelist', 'certificate', 'ssl', 'tls',
            'connection', 'timeout', 'authentication', 'authorization', 'encryption'
        }
        
        content_lower = content.lower()
        found_keywords = []
        
        for keyword in ds_keywords:
            if keyword in content_lower:
                found_keywords.append(keyword)
        
        return found_keywords[:10]  # Limit to top 10 keywords
    
    def build_knowledge_patterns(self):
        """Build Deep Security patterns from processed content"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get troubleshooting sections
            cursor.execute('''
                SELECT s.content, d.filename 
                FROM pdf_sections s 
                JOIN pdf_documents d ON s.doc_id = d.id 
                WHERE s.section_type = 'troubleshooting'
            ''')
            
            troubleshooting_sections = cursor.fetchall()
            
            patterns_added = 0
            for content, source_doc in troubleshooting_sections:
                patterns = self.extract_troubleshooting_patterns(content, source_doc)
                for pattern in patterns:
                    try:
                        cursor.execute('''
                            INSERT OR REPLACE INTO ds_patterns 
                            (pattern_name, pattern_regex, component, severity, resolution, source_doc, confidence_score)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            pattern['name'],
                            pattern['regex'],
                            pattern['component'],
                            pattern['severity'],
                            pattern['resolution'],
                            source_doc,
                            pattern['confidence']
                        ))
                        patterns_added += 1
                    except Exception as e:
                        print(f"⚠️ Error adding pattern: {e}")
            
            conn.commit()
            conn.close()
            
            print(f"✅ Built {patterns_added} knowledge patterns from PDF content")
            
        except Exception as e:
            print(f"❌ Error building patterns: {e}")
    
    def extract_troubleshooting_patterns(self, content: str, source_doc: str) -> List[Dict]:
        """Extract troubleshooting patterns from content"""
        patterns = []
        
        # Pattern templates for Deep Security issues
        pattern_templates = [
            {
                'keywords': ['amsp', 'scan engine', 'crash', 'failed'],
                'component': 'amsp',
                'severity': 'critical',
                'pattern_base': r'(?i)amsp.*(?:crash|failed|error|stop)'
            },
            {
                'keywords': ['dsm', 'authentication', 'failed'],
                'component': 'dsm',
                'severity': 'error',
                'pattern_base': r'(?i)dsm.*(?:authentication.*failed|auth.*error|login.*failed)'
            },
            {
                'keywords': ['agent', 'communication', 'error'],
                'component': 'agent',
                'severity': 'warning',
                'pattern_base': r'(?i)agent.*(?:communication.*error|connection.*lost|heartbeat.*failed)'
            }
        ]
        
        content_lower = content.lower()
        
        for template in pattern_templates:
            # Check if template keywords are present
            keyword_count = sum(1 for kw in template['keywords'] if kw in content_lower)
            
            if keyword_count >= 2:  # At least 2 keywords must match
                # Look for resolution text
                resolution = self.extract_resolution_text(content, template['keywords'])
                
                if resolution:
                    pattern = {
                        'name': f"{template['component']}_issue_pattern",
                        'regex': template['pattern_base'],
                        'component': template['component'],
                        'severity': template['severity'],
                        'resolution': resolution,
                        'confidence': min(0.9, keyword_count * 0.3)
                    }
                    patterns.append(pattern)
        
        return patterns
    
    def extract_resolution_text(self, content: str, keywords: List[str]) -> str:
        """Extract resolution text from content"""
        lines = content.split('\n')
        resolution_indicators = ['solution', 'resolution', 'fix', 'workaround', 'resolve', 'correct']
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Look for resolution indicators near keyword lines
            if any(kw in line_lower for kw in keywords):
                # Check next few lines for resolution
                for j in range(i, min(i + 5, len(lines))):
                    next_line = lines[j].lower()
                    if any(indicator in next_line for indicator in resolution_indicators):
                        # Extract resolution text (next 2-3 lines)
                        resolution_lines = lines[j:min(j + 3, len(lines))]
                        resolution = ' '.join(resolution_lines).strip()
                        if len(resolution) > 20:  # Must be substantial
                            return resolution[:500]  # Limit length
        
        return ""
    
    def is_pdf_processed(self, filename: str) -> bool:
        """Check if PDF has already been processed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM pdf_documents WHERE filename = ?', (filename,))
            result = cursor.fetchone()
            
            conn.close()
            return result is not None
            
        except Exception as e:
            return False
    
    def search_knowledge(self, query: str, component: str = None, max_results: int = 5) -> List[Dict]:
        """Search processed PDF knowledge"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build search query
            search_terms = query.lower().split()
            where_conditions = []
            params = []
            
            # Search in content and section titles
            for term in search_terms:
                where_conditions.append(
                    "(LOWER(s.content) LIKE ? OR LOWER(s.section_title) LIKE ? OR LOWER(s.keywords) LIKE ?)"
                )
                params.extend([f'%{term}%', f'%{term}%', f'%{term}%'])
            
            # Filter by component if specified
            if component:
                where_conditions.append("s.section_type = ?")
                params.append(component)
            
            where_clause = " AND ".join(where_conditions)
            
            sql = f'''
                SELECT 
                    d.title,
                    s.section_title,
                    s.content,
                    s.page_number,
                    s.section_type,
                    d.filename
                FROM pdf_sections s
                JOIN pdf_documents d ON s.doc_id = d.id
                WHERE {where_clause}
                ORDER BY 
                    CASE s.section_type
                        WHEN 'troubleshooting' THEN 1
                        WHEN 'best_practices' THEN 2
                        WHEN 'configuration' THEN 3
                        ELSE 4
                    END,
                    LENGTH(s.content) DESC
                LIMIT ?
            '''
            
            params.append(max_results)
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            conn.close()
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'document_title': result[0],
                    'section_title': result[1],
                    'content': result[2][:1000] + "..." if len(result[2]) > 1000 else result[2],
                    'page_number': result[3],
                    'section_type': result[4],
                    'source_file': result[5],
                    'relevance_score': 0.8  # Base relevance score
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Knowledge search error: {e}")
            return []
    
    def get_patterns_for_component(self, component: str) -> List[Dict]:
        """Get troubleshooting patterns for specific component"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT pattern_name, pattern_regex, severity, resolution, confidence_score
                FROM ds_patterns 
                WHERE component = ?
                ORDER BY confidence_score DESC
            ''', (component,))
            
            results = cursor.fetchall()
            conn.close()
            
            patterns = []
            for result in results:
                patterns.append({
                    'pattern_name': result[0],
                    'pattern_regex': result[1],
                    'severity': result[2],
                    'resolution': result[3],
                    'confidence_score': result[4]
                })
            
            return patterns
            
        except Exception as e:
            print(f"❌ Pattern retrieval error: {e}")
            return []
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about processed knowledge"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Document stats
            cursor.execute('SELECT COUNT(*) FROM pdf_documents')
            doc_count = cursor.fetchone()[0]
            
            # Section stats
            cursor.execute('SELECT COUNT(*) FROM pdf_sections')
            section_count = cursor.fetchone()[0]
            
            # Pattern stats
            cursor.execute('SELECT COUNT(*) FROM ds_patterns')
            pattern_count = cursor.fetchone()[0]
            
            # Section type breakdown
            cursor.execute('SELECT section_type, COUNT(*) FROM pdf_sections GROUP BY section_type')
            section_types = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_documents': doc_count,
                'total_sections': section_count,
                'total_patterns': pattern_count,
                'section_types': section_types,
                'pdf_processing_available': PDF_AVAILABLE,
                'database_path': self.db_path
            }
            
        except Exception as e:
            return {'error': str(e), 'pdf_processing_available': PDF_AVAILABLE}

# Integration functions for Dynamic RAG
def get_pdf_knowledge_integrator():
    """Get PDF knowledge integrator instance"""
    return PDFKnowledgeIntegrator()

def process_proprietary_pdfs():
    """Process all proprietary Deep Security PDFs"""
    integrator = get_pdf_knowledge_integrator()
    return integrator.process_all_pdfs()

def search_proprietary_knowledge(query: str, component: str = None, max_results: int = 5):
    """Search proprietary Deep Security knowledge"""
    integrator = get_pdf_knowledge_integrator()
    return integrator.search_knowledge(query, component, max_results)

if __name__ == "__main__":
    print("🔍 PDF Knowledge Integrator Test")
    print("=" * 50)
    
    integrator = PDFKnowledgeIntegrator()
    
    # Process PDFs
    print("\n📖 Processing proprietary Deep Security PDFs...")
    integrator.process_all_pdfs()
    
    # Get stats
    stats = integrator.get_knowledge_stats()
    print(f"\n📊 Knowledge Base Statistics:")
    print(f"Documents: {stats.get('total_documents', 0)}")
    print(f"Sections: {stats.get('total_sections', 0)}")
    print(f"Patterns: {stats.get('total_patterns', 0)}")
    print(f"Section Types: {stats.get('section_types', {})}")
    
    # Test search
    print(f"\n🔍 Testing knowledge search...")
    results = integrator.search_knowledge("AMSP scan engine performance", max_results=3)
    print(f"Found {len(results)} relevant sections")
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['document_title']} - {result['section_title']}")
        print(f"   Page: {result['page_number']} | Type: {result['section_type']}")
        print(f"   Content: {result['content'][:200]}...")
