#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE MODULARIZATION VALIDATION SCRIPT
Pre-implementation analysis to ensure zero-risk transformation
"""

import os
import sys
import re
import ast
import importlib.util
from pathlib import Path

class ModularizationValidator:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.csdai_path = self.project_root / "CSDAIv2"
        self.results = {
            'dependencies': [],
            'imports': [],
            'cross_references': [],
            'api_routes': [],
            'test_files': [],
            'risks': [],
            'recommendations': []
        }
    
    def analyze_current_dependencies(self):
        """Analyze all files that depend on analyzers.py"""
        print("🔍 Analyzing current dependencies...")
        
        # Find all Python files that import from analyzers
        for py_file in self.csdai_path.rglob("*.py"):
            if py_file.name == "analyzers.py":
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for imports from analyzers
                import_patterns = [
                    r'from analyzers import',
                    r'import analyzers',
                    r'analyzers\.',
                    r'DSAgentLogAnalyzer',
                    r'AMSPAnalyzer',
                    r'ConflictAnalyzer',
                    r'ResourceAnalyzer',
                    r'DSAgentOfflineAnalyzer',
                    r'DiagnosticPackageAnalyzer'
                ]
                
                for pattern in import_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        self.results['dependencies'].append({
                            'file': str(py_file.relative_to(self.project_root)),
                            'pattern': pattern,
                            'matches': len(matches)
                        })
                        
            except Exception as e:
                print(f"⚠️ Error reading {py_file}: {e}")
    
    def analyze_imports_structure(self):
        """Analyze the import structure of analyzers.py"""
        print("📦 Analyzing imports structure...")
        
        analyzers_file = self.csdai_path / "analyzers.py"
        if not analyzers_file.exists():
            self.results['risks'].append("analyzers.py not found!")
            return
        
        try:
            with open(analyzers_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST to find imports
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.results['imports'].append({
                            'type': 'import',
                            'module': alias.name,
                            'line': node.lineno
                        })
                elif isinstance(node, ast.ImportFrom):
                    self.results['imports'].append({
                        'type': 'from_import',
                        'module': node.module,
                        'names': [alias.name for alias in node.names],
                        'line': node.lineno
                    })
                        
        except Exception as e:
            self.results['risks'].append(f"Error parsing analyzers.py: {e}")
    
    def analyze_cross_references(self):
        """Analyze cross-references between analyzer classes"""
        print("🔗 Analyzing cross-references...")
        
        analyzers_file = self.csdai_path / "analyzers.py"
        try:
            with open(analyzers_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find class definitions and their references to other classes
            class_pattern = r'class (\w+)\('
            classes = re.findall(class_pattern, content)
            
            for class_name in classes:
                if class_name == 'AnalyzerOutputStandardizer':
                    continue
                
                # Find references to other analyzer classes within this class
                class_start = content.find(f'class {class_name}(')
                if class_start == -1:
                    continue
                
                # Find the end of this class (start of next class or end of file)
                next_class_start = len(content)
                for other_class in classes:
                    if other_class != class_name:
                        other_start = content.find(f'class {other_class}(', class_start + 1)
                        if other_start > class_start and other_start < next_class_start:
                            next_class_start = other_start
                
                class_content = content[class_start:next_class_start]
                
                # Check for references to other analyzer classes
                for other_class in classes:
                    if other_class != class_name and other_class in class_content:
                        # Count actual instantiations (not just mentions in comments)
                        instantiation_pattern = rf'{other_class}\s*\('
                        instantiations = re.findall(instantiation_pattern, class_content)
                        if instantiations:
                            self.results['cross_references'].append({
                                'from_class': class_name,
                                'to_class': other_class,
                                'instantiations': len(instantiations)
                            })
        
        except Exception as e:
            self.results['risks'].append(f"Error analyzing cross-references: {e}")
    
    def analyze_api_routes(self):
        """Analyze API routes that use analyzers"""
        print("🌐 Analyzing API routes...")
        
        api_files = [
            "api_routes.py",
            "routes.py"
        ]
        
        for api_file in api_files:
            file_path = self.csdai_path / api_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for analyzer usage
                    analyzer_classes = [
                        'DSAgentLogAnalyzer',
                        'AMSPAnalyzer', 
                        'ConflictAnalyzer',
                        'ResourceAnalyzer',
                        'DSAgentOfflineAnalyzer',
                        'DiagnosticPackageAnalyzer'
                    ]
                    
                    for analyzer in analyzer_classes:
                        if analyzer in content:
                            usage_count = len(re.findall(rf'{analyzer}', content))
                            self.results['api_routes'].append({
                                'file': api_file,
                                'analyzer': analyzer,
                                'usage_count': usage_count
                            })
                            
                except Exception as e:
                    self.results['risks'].append(f"Error reading {api_file}: {e}")
    
    def analyze_test_files(self):
        """Analyze test files that use analyzers"""
        print("🧪 Analyzing test files...")
        
        for test_file in self.csdai_path.glob("test_*.py"):
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for analyzer imports/usage
                if 'analyzers' in content.lower():
                    imports = re.findall(r'from analyzers import.*', content)
                    direct_imports = re.findall(r'import.*Analyzer', content)
                    
                    self.results['test_files'].append({
                        'file': test_file.name,
                        'analyzer_imports': imports,
                        'direct_imports': direct_imports
                    })
                    
            except Exception as e:
                self.results['risks'].append(f"Error reading {test_file}: {e}")
    
    def validate_frontend_integration(self):
        """Validate frontend integration points"""
        print("🎨 Validating frontend integration...")
        
        frontend_api_path = self.project_root / "src" / "app" / "api" / "csdai"
        if frontend_api_path.exists():
            # Check all TypeScript files in the API routes
            for ts_file in frontend_api_path.rglob("*.ts"):
                try:
                    with open(ts_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for backend URLs that would be affected
                    backend_calls = re.findall(r'BACKEND_URL.*', content)
                    if backend_calls:
                        self.results['api_routes'].append({
                            'file': f"frontend/{ts_file.relative_to(self.project_root)}",
                            'backend_calls': backend_calls
                        })
                        
                except Exception as e:
                    self.results['risks'].append(f"Error reading frontend file {ts_file}: {e}")
    
    def assess_risks(self):
        """Assess risks and provide recommendations"""
        print("⚠️ Assessing risks...")
        
        # Risk 1: Cross-references between analyzers
        if self.results['cross_references']:
            critical_refs = [ref for ref in self.results['cross_references'] 
                           if ref['instantiations'] > 0]
            if critical_refs:
                self.results['risks'].append(
                    f"CRITICAL: Found {len(critical_refs)} cross-references between analyzer classes"
                )
                for ref in critical_refs:
                    self.results['recommendations'].append(
                        f"Ensure {ref['from_class']} properly imports {ref['to_class']} in modular structure"
                    )
        
        # Risk 2: Many files depend on analyzers.py
        if len(self.results['dependencies']) > 10:
            self.results['risks'].append(
                f"HIGH: {len(self.results['dependencies'])} files depend on analyzers.py"
            )
            self.results['recommendations'].append(
                "Ensure backward compatibility with __init__.py import hub"
            )
        
        # Risk 3: Complex API integration
        if len(self.results['api_routes']) > 5:
            self.results['risks'].append(
                "MEDIUM: Complex API integration detected"
            )
            self.results['recommendations'].append(
                "Test API endpoints thoroughly after modularization"
            )
        
        # Risk 4: Test file dependencies
        if len(self.results['test_files']) > 3:
            self.results['risks'].append(
                "MEDIUM: Multiple test files depend on analyzers"
            )
            self.results['recommendations'].append(
                "Run full test suite before and after modularization"
            )
    
    def generate_report(self):
        """Generate comprehensive validation report"""
        print("\n" + "="*60)
        print("📋 MODULARIZATION VALIDATION REPORT")
        print("="*60)
        
        print(f"\n📊 STATISTICS:")
        print(f"Dependencies found: {len(self.results['dependencies'])}")
        print(f"Import statements: {len(self.results['imports'])}")
        print(f"Cross-references: {len(self.results['cross_references'])}")
        print(f"API route usages: {len(self.results['api_routes'])}")
        print(f"Test files affected: {len(self.results['test_files'])}")
        
        print(f"\n🔗 CRITICAL CROSS-REFERENCES:")
        for ref in self.results['cross_references']:
            if ref['instantiations'] > 0:
                print(f"  {ref['from_class']} → {ref['to_class']} ({ref['instantiations']} instantiations)")
        
        print(f"\n📁 FILES THAT IMPORT ANALYZERS:")
        dependency_files = set()
        for dep in self.results['dependencies']:
            dependency_files.add(dep['file'])
        for file in sorted(dependency_files):
            print(f"  {file}")
        
        print(f"\n🌐 API INTEGRATION POINTS:")
        for api in self.results['api_routes']:
            print(f"  {api.get('file', 'Unknown')}: {api.get('analyzer', api.get('backend_calls', 'N/A'))}")
        
        print(f"\n🧪 TEST FILES:")
        for test in self.results['test_files']:
            print(f"  {test['file']}")
        
        print(f"\n⚠️ RISKS IDENTIFIED:")
        if not self.results['risks']:
            print("  ✅ No major risks identified!")
        else:
            for risk in self.results['risks']:
                print(f"  ❌ {risk}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if not self.results['recommendations']:
            print("  ✅ No additional recommendations!")
        else:
            for rec in self.results['recommendations']:
                print(f"  📌 {rec}")
        
        print(f"\n🎯 MODULARIZATION READINESS:")
        risk_count = len(self.results['risks'])
        if risk_count == 0:
            print("  🟢 LOW RISK - Safe to proceed with modularization")
        elif risk_count <= 2:
            print("  🟡 MEDIUM RISK - Proceed with caution and extra testing")
        else:
            print("  🔴 HIGH RISK - Address critical issues before proceeding")
        
        return risk_count == 0
    
    def run_full_analysis(self):
        """Run complete validation analysis"""
        print("🚀 Starting comprehensive modularization validation...")
        
        self.analyze_current_dependencies()
        self.analyze_imports_structure() 
        self.analyze_cross_references()
        self.analyze_api_routes()
        self.analyze_test_files()
        self.validate_frontend_integration()
        self.assess_risks()
        
        return self.generate_report()

def main():
    """Main validation function"""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        # Try to detect project root
        current_dir = Path.cwd()
        if (current_dir / "CSDAIv2" / "analyzers.py").exists():
            project_root = current_dir
        elif (current_dir.parent / "CSDAIv2" / "analyzers.py").exists():
            project_root = current_dir.parent
        else:
            print("❌ Could not find project root. Please run from project directory or pass path as argument.")
            print("Usage: python validate_modularization.py [project_root_path]")
            sys.exit(1)
    
    validator = ModularizationValidator(project_root)
    is_safe = validator.run_full_analysis()
    
    if is_safe:
        print(f"\n🎉 VALIDATION COMPLETE - SAFE TO PROCEED!")
        print(f"Execute the modularization plan with confidence.")
    else:
        print(f"\n⚠️ VALIDATION COMPLETE - REVIEW REQUIRED!")
        print(f"Address the identified risks before proceeding.")
    
    return 0 if is_safe else 1

if __name__ == "__main__":
    sys.exit(main())
