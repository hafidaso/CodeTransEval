"""
Advanced Code Analysis and Pattern Detection Module
Phase 2 Implementation - Code Project Converter

This module provides static code analysis, pattern recognition, dependency mapping,
and code complexity assessment for improved conversion quality.
"""

import ast
import re
import os
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict
import json
import logging

class CodeAnalyzer:
    """Advanced code analysis and pattern detection for better conversion quality."""
    
    def __init__(self):
        self.patterns = self._load_patterns()
        self.complexity_metrics = {}
        self.dependency_graph = defaultdict(set)
        
    def _load_patterns(self) -> Dict[str, List[str]]:
        """Load common code patterns for different languages."""
        return {
            'python': [
                r'def\s+\w+\s*\([^)]*\):',
                r'class\s+\w+',
                r'import\s+\w+',
                r'from\s+\w+\s+import',
                r'if\s+__name__\s*==\s*[\'"]__main__[\'"]',
                r'@\w+',
                r'try:\s*\n.*except',
                r'with\s+\w+\s+as',
                r'lambda\s+\w+:',
                r'list\(.*\)|dict\(.*\)|set\(.*\)',
            ],
            'javascript': [
                r'function\s+\w+\s*\([^)]*\)',
                r'const\s+\w+\s*=',
                r'let\s+\w+\s*=',
                r'var\s+\w+\s*=',
                r'class\s+\w+',
                r'import\s+.*\s+from',
                r'export\s+.*',
                r'async\s+function',
                r'\.then\(.*\)',
                r'await\s+\w+',
            ],
            'java': [
                r'public\s+class\s+\w+',
                r'private\s+\w+\s+\w+',
                r'public\s+static\s+void\s+main',
                r'import\s+java\..*;',
                r'@Override',
                r'@Test',
                r'throws\s+\w+',
                r'new\s+\w+\s*\(',
                r'interface\s+\w+',
                r'enum\s+\w+',
            ],
            'c': [
                r'#include\s+<[^>]+>',
                r'int\s+main\s*\(',
                r'struct\s+\w+',
                r'typedef\s+struct',
                r'#define\s+\w+',
                r'void\s+\w+\s*\(',
                r'for\s*\([^)]*\)',
                r'while\s*\(',
                r'if\s*\(',
                r'return\s+',
            ]
        }
    
    def analyze_file(self, file_path: str, language: str) -> Dict[str, Any]:
        """Analyze a single file for patterns, complexity, and structure."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                'file_path': file_path,
                'language': language,
                'size': len(content),
                'lines': len(content.split('\n')),
                'patterns_found': [],
                'complexity_score': 0,
                'dependencies': [],
                'functions': [],
                'classes': [],
                'imports': [],
                'structure': {}
            }
            
            # Pattern detection
            analysis['patterns_found'] = self._detect_patterns(content, language)
            
            # Complexity analysis
            analysis['complexity_score'] = self._calculate_complexity(content, language)
            
            # Structure analysis
            analysis['structure'] = self._analyze_structure(content, language)
            
            # Extract functions, classes, imports
            analysis['functions'] = self._extract_functions(content, language)
            analysis['classes'] = self._extract_classes(content, language)
            analysis['imports'] = self._extract_imports(content, language)
            
            return analysis
            
        except Exception as e:
            logging.error(f"Error analyzing file {file_path}: {e}")
            return {'error': str(e), 'file_path': file_path}
    
    def _detect_patterns(self, content: str, language: str) -> List[str]:
        """Detect common patterns in the code."""
        patterns_found = []
        if language in self.patterns:
            for pattern in self.patterns[language]:
                matches = re.findall(pattern, content, re.MULTILINE)
                if matches:
                    patterns_found.extend(matches[:5])  # Limit to first 5 matches
        return patterns_found
    
    def _calculate_complexity(self, content: str, language: str) -> int:
        """Calculate code complexity score."""
        complexity = 0
        
        # Basic complexity factors
        complexity += content.count('if') * 1
        complexity += content.count('for') * 2
        complexity += content.count('while') * 2
        complexity += content.count('try') * 1
        complexity += content.count('except') * 1
        complexity += content.count('catch') * 1
        complexity += content.count('switch') * 2
        complexity += content.count('case') * 1
        
        # Function complexity
        if language == 'python':
            complexity += len(re.findall(r'def\s+\w+', content)) * 3
        elif language == 'javascript':
            complexity += len(re.findall(r'function\s+\w+', content)) * 3
        elif language == 'java':
            complexity += len(re.findall(r'public\s+\w+\s+\w+\s*\(', content)) * 3
        elif language == 'c':
            complexity += len(re.findall(r'\w+\s+\w+\s*\([^)]*\)\s*{', content)) * 3
        
        return complexity
    
    def _analyze_structure(self, content: str, language: str) -> Dict[str, Any]:
        """Analyze code structure and organization."""
        structure = {
            'has_main_function': False,
            'has_classes': False,
            'has_functions': False,
            'has_imports': False,
            'nesting_depth': 0,
            'file_type': 'unknown'
        }
        
        lines = content.split('\n')
        max_nesting = 0
        current_nesting = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Check for main function
            if language == 'python' and 'if __name__ == "__main__"' in stripped:
                structure['has_main_function'] = True
            elif language == 'java' and 'public static void main' in stripped:
                structure['has_main_function'] = True
            elif language == 'c' and 'int main(' in stripped:
                structure['has_main_function'] = True
            
            # Check for classes
            if any(keyword in stripped for keyword in ['class ', 'struct ']):
                structure['has_classes'] = True
            
            # Check for functions
            if any(keyword in stripped for keyword in ['def ', 'function ', 'void ', 'int ']):
                structure['has_functions'] = True
            
            # Check for imports
            if any(keyword in stripped for keyword in ['import ', '#include ']):
                structure['has_imports'] = True
            
            # Calculate nesting depth
            if stripped.endswith('{') or stripped.endswith(':'):
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            elif stripped.startswith('}') or stripped.startswith('return'):
                current_nesting = max(0, current_nesting - 1)
        
        structure['nesting_depth'] = max_nesting
        
        # Determine file type
        if structure['has_main_function']:
            structure['file_type'] = 'executable'
        elif structure['has_classes']:
            structure['file_type'] = 'class_library'
        elif structure['has_functions']:
            structure['file_type'] = 'function_library'
        else:
            structure['file_type'] = 'data_file'
        
        return structure
    
    def _extract_functions(self, content: str, language: str) -> List[str]:
        """Extract function names from code."""
        functions = []
        
        if language == 'python':
            functions = re.findall(r'def\s+(\w+)', content)
        elif language == 'javascript':
            functions = re.findall(r'function\s+(\w+)', content)
        elif language == 'java':
            functions = re.findall(r'public\s+\w+\s+(\w+)\s*\(', content)
        elif language == 'c':
            functions = re.findall(r'(\w+)\s+\w+\s*\([^)]*\)\s*{', content)
        
        return functions
    
    def _extract_classes(self, content: str, language: str) -> List[str]:
        """Extract class names from code."""
        classes = []
        
        if language == 'python':
            classes = re.findall(r'class\s+(\w+)', content)
        elif language == 'javascript':
            classes = re.findall(r'class\s+(\w+)', content)
        elif language == 'java':
            classes = re.findall(r'public\s+class\s+(\w+)', content)
        elif language == 'c':
            classes = re.findall(r'struct\s+(\w+)', content)
        
        return classes
    
    def _extract_imports(self, content: str, language: str) -> List[str]:
        """Extract import statements from code."""
        imports = []
        
        if language == 'python':
            imports = re.findall(r'import\s+(\w+)', content)
            imports.extend(re.findall(r'from\s+(\w+)', content))
        elif language == 'javascript':
            imports = re.findall(r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]', content)
        elif language == 'java':
            imports = re.findall(r'import\s+([^;]+);', content)
        elif language == 'c':
            imports = re.findall(r'#include\s+[<"]([^>"]+)[>"]', content)
        
        return imports
    
    def analyze_project(self, project_path: str, language: str) -> Dict[str, Any]:
        """Analyze entire project for patterns and dependencies."""
        project_analysis = {
            'project_path': project_path,
            'language': language,
            'files': [],
            'total_complexity': 0,
            'dependency_graph': {},
            'common_patterns': defaultdict(int),
            'project_structure': {
                'has_main_file': False,
                'has_libraries': False,
                'has_tests': False,
                'has_docs': False
            }
        }
        
        # Analyze each file
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if self._is_source_file(file, language):
                    file_path = os.path.join(root, file)
                    file_analysis = self.analyze_file(file_path, language)
                    project_analysis['files'].append(file_analysis)
                    
                    if 'complexity_score' in file_analysis:
                        project_analysis['total_complexity'] += file_analysis['complexity_score']
                    
                    # Track common patterns
                    for pattern in file_analysis.get('patterns_found', []):
                        project_analysis['common_patterns'][pattern] += 1
        
        # Build dependency graph
        project_analysis['dependency_graph'] = self._build_dependency_graph(
            project_analysis['files']
        )
        
        # Analyze project structure
        project_analysis['project_structure'] = self._analyze_project_structure(
            project_path, project_analysis['files']
        )
        
        return project_analysis
    
    def _is_source_file(self, filename: str, language: str) -> bool:
        """Check if file is a source file for the given language."""
        extensions = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx', '.ts', '.tsx'],
            'java': ['.java'],
            'c': ['.c', '.h', '.cpp', '.hpp']
        }
        
        if language in extensions:
            return any(filename.endswith(ext) for ext in extensions[language])
        return False
    
    def _build_dependency_graph(self, files: List[Dict]) -> Dict[str, List[str]]:
        """Build dependency graph from file analysis."""
        graph = {}
        
        for file_analysis in files:
            file_path = file_analysis['file_path']
            imports = file_analysis.get('imports', [])
            graph[file_path] = imports
        
        return graph
    
    def _analyze_project_structure(self, project_path: str, files: List[Dict]) -> Dict[str, bool]:
        """Analyze overall project structure."""
        structure = {
            'has_main_file': False,
            'has_libraries': False,
            'has_tests': False,
            'has_docs': False
        }
        
        for file_analysis in files:
            file_structure = file_analysis.get('structure', {})
            
            if file_structure.get('has_main_function'):
                structure['has_main_file'] = True
            
            if file_structure.get('has_classes') or file_structure.get('has_functions'):
                structure['has_libraries'] = True
        
        # Check for test files
        test_patterns = ['test', 'spec', 'unit', 'integration']
        for file_analysis in files:
            file_path = file_analysis['file_path'].lower()
            if any(pattern in file_path for pattern in test_patterns):
                structure['has_tests'] = True
                break
        
        # Check for documentation
        doc_patterns = ['readme', 'docs', 'documentation']
        for file_analysis in files:
            file_path = file_analysis['file_path'].lower()
            if any(pattern in file_path for pattern in doc_patterns):
                structure['has_docs'] = True
                break
        
        return structure
    
    def get_conversion_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate conversion recommendations based on analysis."""
        recommendations = []
        
        complexity = analysis.get('total_complexity', 0)
        if complexity > 100:
            recommendations.append("High complexity detected - consider breaking down into smaller modules")
        
        if not analysis.get('project_structure', {}).get('has_tests'):
            recommendations.append("No test files found - recommend adding unit tests after conversion")
        
        if analysis.get('project_structure', {}).get('has_libraries'):
            recommendations.append("Library code detected - ensure proper dependency mapping")
        
        patterns = analysis.get('common_patterns', {})
        if 'lambda' in patterns:
            recommendations.append("Lambda functions detected - may need special handling in target language")
        
        if 'async' in patterns:
            recommendations.append("Async code detected - ensure proper async/await conversion")
        
        return recommendations

# Global instance
code_analyzer = CodeAnalyzer()

def get_code_analyzer():
    """Get the global code analyzer instance."""
    return code_analyzer 