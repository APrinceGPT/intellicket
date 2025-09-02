"""
PDF Text Extraction Script for Deep Security Documentation
"""
import PyPDF2
import sys

def extract_pdf_text(pdf_path):
    """Extract text content from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            print(f"PDF has {len(pdf_reader.pages)} pages")
            
            all_text = ""
            
            # Extract ALL pages (not just first 50)
            max_pages = len(pdf_reader.pages)
            
            for page_num in range(max_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                if text.strip():  # Only add non-empty pages
                    all_text += f"\n--- PAGE {page_num + 1} ---\n"
                    all_text += text
                    all_text += "\n\n"
            
            return all_text
            
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

if __name__ == "__main__":
    pdf_path = "pdf/Anti Malware.pdf"  # Target the Anti Malware PDF
    text_content = extract_pdf_text(pdf_path)
    
    # Save to text file for analysis
    with open("anti_malware_extracted.txt", "w", encoding="utf-8") as f:
        f.write(text_content)
    
    print("Anti Malware PDF text extracted and saved to anti_malware_extracted.txt")
    print(f"Total content length: {len(text_content)} characters")
    
    # Show first 2000 characters as preview
    print("\n=== PREVIEW (First 2000 characters) ===")
    print(text_content[:2000])
