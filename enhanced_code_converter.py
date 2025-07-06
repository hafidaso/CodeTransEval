#!/usr/bin/env python3
"""
Enhanced Code Translation Pipeline
Supports C→Python, Python→JavaScript, and Python→Java conversions for multi-file projects
Integrates with Gemma 3n for AI-powered code conversion
"""

import os
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import ast
import re
import sys
import time
import logging
from datetime import datetime

# Import AI integrations
try:
    from gemma3n_integration import get_gemma_integration
    GEMMA_AVAILABLE = True
except ImportError:
    print("Warning: gemma3n_integration not found. Using basic conversion only.")
    GEMMA_AVAILABLE = False

try:
    from ai_model_manager import get_ai_model_manager
    MODEL_MANAGER_AVAILABLE = True
except ImportError:
    print("Warning: ai_model_manager not found. Using basic model selection.")
    MODEL_MANAGER_AVAILABLE = False

# Phase 2 imports
try:
    from code_analysis import get_code_analyzer
    from testing_qa import get_test_generator, get_coverage_analyzer, get_performance_benchmark
    from enterprise_security import get_rbac_manager, get_audit_logger, get_secure_scanner, get_data_encryption
    from analytics_reporting import get_analytics_manager, get_conversion_analytics, get_report_generator
    PHASE2_AVAILABLE = True
    print("Phase 2 features available: Advanced analysis, testing, security, and analytics")
except ImportError as e:
    print(f"Warning: Phase 2 features not available: {e}")
    PHASE2_AVAILABLE = False

class EnhancedCodeConverter:
    def __init__(self, use_ai: bool = False, model_name: str = "gemma-3n-2b", use_kaggle: bool = True, 
                 auto_select_model: bool = True, enable_phase2: bool = False):
        self.model_name = model_name
        self.use_ai = use_ai and (GEMMA_AVAILABLE or MODEL_MANAGER_AVAILABLE)
        self.auto_select_model = auto_select_model
        self.enable_phase2 = enable_phase2 and PHASE2_AVAILABLE
        
        if self.use_ai:
            if MODEL_MANAGER_AVAILABLE and auto_select_model:
                self.model_manager = get_ai_model_manager()
                self.ai_integration = None  # Will be selected dynamically
                print("AI integration enabled with intelligent model selection")
            else:
                try:
                    self.ai_integration = get_gemma_integration(model_name=model_name, use_kaggle=use_kaggle)
                    print(f"AI integration enabled with {model_name}")
                except Exception as e:
                    print(f"Warning: Failed to initialize AI integration: {e}")
                    self.use_ai = False
        else:
            self.ai_integration = None
            self.model_manager = None
        
        # Initialize Phase 2 components if enabled
        if self.enable_phase2:
            self.code_analyzer = get_code_analyzer()
            self.test_generator = get_test_generator()
            self.coverage_analyzer = get_coverage_analyzer()
            self.performance_benchmark = get_performance_benchmark()
            self.rbac_manager = get_rbac_manager()
            self.audit_logger = get_audit_logger()
            self.secure_scanner = get_secure_scanner()
            self.data_encryption = get_data_encryption()
            self.analytics_manager = get_analytics_manager()
            self.conversion_analytics = get_conversion_analytics()
            self.report_generator = get_report_generator()
            print("Phase 2 features initialized: Code analysis, testing, security, and analytics")
        else:
            self.code_analyzer = None
            self.test_generator = None
            self.coverage_analyzer = None
            self.performance_benchmark = None
            self.rbac_manager = None
            self.audit_logger = None
            self.secure_scanner = None
            self.data_encryption = None
            self.analytics_manager = None
            self.conversion_analytics = None
            self.report_generator = None
        
        self.supported_conversions = {
            'c_to_python': {
                'extensions': ['.c', '.h'],
                'target_ext': '.py',
                'target_lang': 'python',
                'ai_prompt_template': self._get_c_to_python_prompt(),
                'complexity': 'medium',
                'best_models': ['gemma-3n-2b', 'claude-3-sonnet', 'gpt-4']
            },
            'python_to_javascript': {
                'extensions': ['.py'],
                'target_ext': '.js',
                'target_lang': 'javascript',
                'ai_prompt_template': self._get_python_to_js_prompt(),
                'complexity': 'medium',
                'best_models': ['gemma-3n-2b', 'claude-3-sonnet', 'gpt-4']
            },
            'python_to_java': {
                'extensions': ['.py'],
                'target_ext': '.java',
                'target_lang': 'java',
                'ai_prompt_template': self._get_python_to_java_prompt(),
                'complexity': 'high',
                'best_models': ['claude-3-sonnet', 'gpt-4', 'gemma-3n-2b']
            },
            'java_to_python': {
                'extensions': ['.java'],
                'target_ext': '.py',
                'target_lang': 'python',
                'ai_prompt_template': self._get_java_to_python_prompt(),
                'complexity': 'high',
                'best_models': ['claude-3-sonnet', 'gpt-4', 'gemma-3n-2b']
            },
            'javascript_to_python': {
                'extensions': ['.js', '.ts', '.jsx', '.tsx'],
                'target_ext': '.py',
                'target_lang': 'python',
                'ai_prompt_template': self._get_javascript_to_python_prompt(),
                'complexity': 'medium',
                'best_models': ['gemma-3n-2b', 'claude-3-sonnet', 'gpt-4']
            },
            'typescript_to_python': {
                'extensions': ['.ts', '.tsx'],
                'target_ext': '.py',
                'target_lang': 'python',
                'ai_prompt_template': self._get_typescript_to_python_prompt(),
                'complexity': 'medium',
                'best_models': ['gemma-3n-2b', 'claude-3-sonnet', 'gpt-4']
            },
            'java_to_javascript': {
                'extensions': ['.java'],
                'target_ext': '.js',
                'target_lang': 'javascript',
                'ai_prompt_template': self._get_java_to_javascript_prompt(),
                'complexity': 'high',
                'best_models': ['claude-3-sonnet', 'gpt-4', 'gemma-3n-2b']
            },
            'javascript_to_java': {
                'extensions': ['.js', '.ts', '.jsx', '.tsx'],
                'target_ext': '.java',
                'target_lang': 'java',
                'ai_prompt_template': self._get_javascript_to_java_prompt(),
                'complexity': 'high',
                'best_models': ['claude-3-sonnet', 'gpt-4', 'gemma-3n-2b']
            }
        }
    
    def _get_c_to_python_prompt(self) -> str:
        return """Convert the following C code to Python. 
Maintain the same functionality and logic, but use Python syntax and idioms.
Remove C-specific elements like includes, semicolons, and braces.
Convert printf to print, scanf to input, and adjust variable declarations.

C Code:
{source_code}

Python Code:"""
    
    def _get_python_to_js_prompt(self) -> str:
        return """Convert the following Python code to JavaScript.
Maintain the same functionality and logic, but use JavaScript syntax and idioms.
Convert print to console.log, function definitions to JavaScript style,
and adjust variable declarations and control structures.

Python Code:
{source_code}

JavaScript Code:"""
    
    def _get_python_to_java_prompt(self) -> str:
        return """Convert the following Python code to Java.
Maintain the same functionality and logic, but use Java syntax and idioms.
Convert print to System.out.println, function definitions to Java methods,
add proper class structure, and adjust variable declarations and control structures.

Python Code:
{source_code}

Java Code:"""
    
    def _get_java_to_python_prompt(self) -> str:
        return """Convert the following Java code to Python.
Maintain the same functionality and logic, but use Python syntax and idioms.
Convert System.out.println to print, Java methods to Python functions,
remove type declarations, and adjust control structures to Python style.
Handle Java-specific features like interfaces, abstract classes, and generics appropriately.

Java Code:
{source_code}

Python Code:"""
    
    def _get_javascript_to_python_prompt(self) -> str:
        return """Convert the following JavaScript code to Python.
Maintain the same functionality and logic, but use Python syntax and idioms.
Convert console.log to print, JavaScript functions to Python functions,
adjust variable declarations, and convert JavaScript-specific features to Python equivalents.
Handle async/await, promises, and JavaScript objects appropriately.

JavaScript Code:
{source_code}

Python Code:"""
    
    def _get_typescript_to_python_prompt(self) -> str:
        return """Convert the following TypeScript code to Python.
Maintain the same functionality and logic, but use Python syntax and idioms.
Convert console.log to print, TypeScript interfaces to Python classes or type hints,
remove type annotations, and adjust control structures to Python style.
Handle TypeScript-specific features like enums, generics, and decorators appropriately.

TypeScript Code:
{source_code}

Python Code:"""
    
    def _get_java_to_javascript_prompt(self) -> str:
        return """Convert the following Java code to JavaScript.
Maintain the same functionality and logic, but use JavaScript syntax and idioms.
Convert System.out.println to console.log, Java methods to JavaScript functions,
remove type declarations, and adjust control structures to JavaScript style.
Handle Java-specific features like interfaces, abstract classes, and generics appropriately.

Java Code:
{source_code}

JavaScript Code:"""
    
    def _get_javascript_to_java_prompt(self) -> str:
        return """Convert the following JavaScript code to Java.
Maintain the same functionality and logic, but use Java syntax and idioms.
Convert console.log to System.out.println, JavaScript functions to Java methods,
add proper class structure, and adjust variable declarations and control structures.
Handle JavaScript-specific features like async/await, promises, and objects appropriately.

JavaScript Code:
{source_code}

Java Code:"""
    
    def convert_project(self, source_dir: str, target_dir: str, conversion_type: str) -> Dict:
        """
        Convert an entire project from source language to target language
        """
        if conversion_type not in self.supported_conversions:
            raise ValueError(f"Unsupported conversion type: {conversion_type}")
        
        config = self.supported_conversions[conversion_type]
        source_path = Path(source_dir)
        target_path = Path(target_dir)
        
        # Create target directory
        target_path.mkdir(parents=True, exist_ok=True)
        
        # Clean up source directory (remove macOS metadata files)
        self._clean_source_directory(source_path)
        
        # Find all source files
        source_files = self._find_source_files(source_path, config['extensions'])
        
        results = {
            'conversion_type': conversion_type,
            'source_dir': str(source_path),
            'target_dir': str(target_path),
            'files_converted': [],
            'errors': [],
            'warnings': [],
            'ai_used': self.use_ai
        }
        
        # Convert each file
        for source_file in source_files:
            try:
                relative_path = source_file.relative_to(source_path)
                target_file = target_path / relative_path.with_suffix(config['target_ext'])
                
                # Create target subdirectory if needed
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Convert the file
                conversion_result = self._convert_file(
                    source_file, target_file, conversion_type, config
                )
                
                results['files_converted'].append({
                    'source': str(relative_path),
                    'target': str(target_file.relative_to(target_path)),
                    'status': conversion_result['status'],
                    'warnings': conversion_result.get('warnings', []),
                    'ai_used': conversion_result.get('ai_used', False)
                })
                
                if conversion_result['status'] == 'error':
                    results['errors'].append({
                        'file': str(relative_path),
                        'error': conversion_result['error']
                    })
                    
            except Exception as e:
                results['errors'].append({
                    'file': str(source_file),
                    'error': str(e)
                })
        
        # Generate project files (package.json, requirements.txt, etc.)
        self._generate_project_files(target_path, conversion_type)
        
        # Phase 2: Advanced analysis and processing
        if self.enable_phase2:
            phase2_results = self._run_phase2_analysis(source_path, target_path, conversion_type, results)
            results['phase2'] = phase2_results
        
        return results
    
    def _clean_source_directory(self, source_path: Path):
        """Remove macOS metadata files and other unwanted files"""
        try:
            # Remove __MACOSX directories
            macosx_dirs = list(source_path.rglob("__MACOSX"))
            for macosx_dir in macosx_dirs:
                if macosx_dir.is_dir():
                    import shutil
                    shutil.rmtree(macosx_dir)
                    print(f"Removed macOS metadata directory: {macosx_dir}")
            
            # Remove ._ files (macOS resource fork files)
            dot_underscore_files = list(source_path.rglob("._*"))
            for dot_file in dot_underscore_files:
                if dot_file.is_file():
                    dot_file.unlink()
                    print(f"Removed macOS resource fork file: {dot_file}")
                    
        except Exception as e:
            print(f"Warning: Could not clean source directory: {e}")
    
    def _find_source_files(self, source_path: Path, extensions: List[str]) -> List[Path]:
        """Find all source files with specified extensions"""
        source_files = []
        for ext in extensions:
            files = source_path.rglob(f"*{ext}")
            for file in files:
                # Skip macOS metadata files and hidden files
                if not any(part.startswith('.') or part.startswith('__MACOSX') for part in file.parts):
                    source_files.append(file)
        return sorted(source_files)
    
    def _convert_file(self, source_file: Path, target_file: Path, conversion_type: str, config: Dict) -> Dict:
        """Convert a single file using AI or basic conversion"""
        try:
            # Try different encodings to handle various file formats
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            source_code = None
            
            for encoding in encodings:
                try:
                    with open(source_file, 'r', encoding=encoding) as f:
                        source_code = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if source_code is None:
                return {'status': 'error', 'error': f'Could not decode file with any encoding: {encodings}'}
            
            # Try AI conversion first if available
            if self.use_ai:
                try:
                    ai_result = self._convert_with_ai(source_code, conversion_type, config)
                    if ai_result['success']:
                        converted_code = ai_result['code']
                        with open(target_file, 'w', encoding='utf-8') as f:
                            f.write(converted_code)
                        return {'status': 'success', 'ai_used': True}
                except Exception as e:
                    print(f"AI conversion failed for {source_file.name}: {e}")
            
            # Fall back to basic conversion
            if conversion_type == 'c_to_python':
                converted_code = self._convert_c_to_python_basic(source_code, source_file.name)
            elif conversion_type == 'python_to_javascript':
                converted_code = self._convert_python_to_javascript_basic(source_code, source_file.name)
            elif conversion_type == 'python_to_java':
                converted_code = self._convert_python_to_java_basic(source_code, source_file.name)
            elif conversion_type == 'java_to_python':
                converted_code = self._convert_java_to_python_basic(source_code, source_file.name)
            elif conversion_type == 'javascript_to_python':
                converted_code = self._convert_javascript_to_python_basic(source_code, source_file.name)
            elif conversion_type == 'typescript_to_python':
                converted_code = self._convert_typescript_to_python_basic(source_code, source_file.name)
            elif conversion_type == 'java_to_javascript':
                converted_code = self._convert_java_to_javascript_basic(source_code, source_file.name)
            elif conversion_type == 'javascript_to_java':
                converted_code = self._convert_javascript_to_java_basic(source_code, source_file.name)
            else:
                raise ValueError(f"Unknown conversion type: {conversion_type}")
            
            # Write converted code
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(converted_code)
            
            return {'status': 'success', 'ai_used': False}
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _run_phase2_analysis(self, source_path: Path, target_path: Path, 
                            conversion_type: str, conversion_results: Dict) -> Dict:
        """Run Phase 2 advanced analysis and processing."""
        phase2_results = {
            'code_analysis': {},
            'testing': {},
            'security': {},
            'analytics': {},
            'performance': {}
        }
        
        try:
            # 1. Code Analysis
            if self.code_analyzer:
                source_analysis = self.code_analyzer.analyze_project(str(source_path), 
                                                                   conversion_type.split('_')[0])
                target_analysis = self.code_analyzer.analyze_project(str(target_path), 
                                                                   conversion_type.split('_')[-1])
                
                phase2_results['code_analysis'] = {
                    'source_analysis': source_analysis,
                    'target_analysis': target_analysis,
                    'recommendations': self.code_analyzer.get_conversion_recommendations(source_analysis)
                }
            
            # 2. Security Scanning
            if self.secure_scanner:
                source_security = self.secure_scanner.scan_project(str(source_path), 
                                                                 conversion_type.split('_')[0])
                target_security = self.secure_scanner.scan_project(str(target_path), 
                                                                 conversion_type.split('_')[-1])
                
                phase2_results['security'] = {
                    'source_security': source_security,
                    'target_security': target_security,
                    'security_improvements': self._analyze_security_improvements(source_security, target_security)
                }
            
            # 3. Test Generation
            if self.test_generator:
                test_results = []
                for file_result in conversion_results['files_converted']:
                    if file_result['status'] == 'success':
                        source_file = source_path / file_result['source']
                        target_file = target_path / file_result['target']
                        
                        test_result = self.test_generator.generate_tests(
                            str(source_file), str(target_file), 
                            conversion_type.split('_')[-1], 'default'
                        )
                        test_results.append(test_result)
                
                phase2_results['testing'] = {
                    'test_generation': test_results,
                    'total_tests_generated': len([r for r in test_results if r.get('success', False)])
                }
            
            # 4. Performance Benchmarking
            if self.performance_benchmark:
                benchmark_results = []
                for file_result in conversion_results['files_converted']:
                    if file_result['status'] == 'success':
                        source_file = source_path / file_result['source']
                        target_file = target_path / file_result['target']
                        
                        benchmark_result = self.performance_benchmark.benchmark_code(
                            str(source_file), str(target_file), 
                            conversion_type.split('_')[-1]
                        )
                        benchmark_results.append(benchmark_result)
                
                phase2_results['performance'] = {
                    'benchmarks': benchmark_results,
                    'average_performance_change': self._calculate_average_performance_change(benchmark_results)
                }
            
            # 5. Analytics Recording
            if self.analytics_manager:
                # Record conversion metrics
                from analytics_reporting import ConversionMetrics
                conversion_metrics = ConversionMetrics(
                    conversion_id=f"{conversion_type}_{int(time.time())}",
                    user_id="default_user",  # In real app, get from session
                    source_language=conversion_type.split('_')[0],
                    target_language=conversion_type.split('_')[-1],
                    file_count=len(conversion_results['files_converted']),
                    total_lines=sum(len(open(source_path / f['source']).readlines()) 
                                  for f in conversion_results['files_converted'] if f['status'] == 'success'),
                    conversion_time=time.time(),  # Placeholder
                    success=len(conversion_results['errors']) == 0,
                    error_message=None if len(conversion_results['errors']) == 0 else str(conversion_results['errors']),
                    ai_model_used="gemma-3n-2b" if conversion_results.get('ai_used') else "basic",
                    quality_score=0.8,  # Placeholder
                    timestamp=datetime.now()
                )
                
                self.analytics_manager.record_conversion(conversion_metrics)
                
                phase2_results['analytics'] = {
                    'metrics_recorded': True,
                    'conversion_id': conversion_metrics.conversion_id
                }
            
            # 6. Audit Logging
            if self.audit_logger:
                from enterprise_security import SecurityLevel
                self.audit_logger.log_event(
                    user_id="default_user",
                    action="project_conversion",
                    resource=f"{conversion_type}_{source_path.name}",
                    details={
                        'conversion_type': conversion_type,
                        'files_converted': len(conversion_results['files_converted']),
                        'errors': len(conversion_results['errors']),
                        'ai_used': conversion_results.get('ai_used', False)
                    },
                    security_level=SecurityLevel.MEDIUM
                )
            
        except Exception as e:
            phase2_results['error'] = str(e)
            logging.error(f"Error in Phase 2 analysis: {e}")
        
        return phase2_results
    
    def _analyze_security_improvements(self, source_security: Dict, target_security: Dict) -> List[str]:
        """Analyze security improvements between source and target."""
        improvements = []
        
        source_vulns = source_security.get('total_vulnerabilities', 0)
        target_vulns = target_security.get('total_vulnerabilities', 0)
        
        if target_vulns < source_vulns:
            improvements.append(f"Reduced vulnerabilities from {source_vulns} to {target_vulns}")
        
        source_risk = source_security.get('overall_risk_score', 0)
        target_risk = target_security.get('overall_risk_score', 0)
        
        if target_risk < source_risk:
            improvements.append(f"Reduced risk score from {source_risk} to {target_risk}")
        
        return improvements
    
    def _calculate_average_performance_change(self, benchmark_results: List[Dict]) -> float:
        """Calculate average performance change from benchmarks."""
        if not benchmark_results:
            return 0.0
        
        total_change = 0.0
        valid_results = 0
        
        for result in benchmark_results:
            if result.get('success', False) and 'benchmark' in result:
                benchmark = result['benchmark']
                if 'performance_change_percent' in benchmark:
                    total_change += benchmark['performance_change_percent']
                    valid_results += 1
        
        return round(total_change / valid_results, 2) if valid_results > 0 else 0.0
    
    def _convert_with_ai(self, source_code: str, conversion_type: str, config: Dict) -> Dict:
        """Convert code using AI integration"""
        prompt = config['ai_prompt_template'].format(source_code=source_code)
        
        try:
            response = self.ai_integration.generate_response(prompt)
            if response and response.strip():
                return {'success': True, 'code': response.strip()}
            else:
                return {'success': False, 'error': 'Empty AI response'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _convert_c_to_python_basic(self, c_code: str, filename: str) -> str:
        """Basic C to Python conversion using regex"""
        python_code = c_code
        
        # Remove C-specific includes and defines
        python_code = re.sub(r'#include\s*<[^>]+>', '', python_code)
        python_code = re.sub(r'#include\s*"[^"]+"', '', python_code)
        python_code = re.sub(r'#define\s+\w+\s+.*', '', python_code)
        python_code = re.sub(r'#ifndef\s+\w+', '', python_code)
        python_code = re.sub(r'#define\s+\w+', '', python_code)
        python_code = re.sub(r'#endif', '', python_code)
        
        # Convert main function
        python_code = re.sub(r'int\s+main\s*\([^)]*\)\s*{', 'if __name__ == "__main__":', python_code)
        
        # Convert variable declarations
        python_code = re.sub(r'int\s+(\w+)\s*;', r'\1 = 0', python_code)
        python_code = re.sub(r'float\s+(\w+)\s*;', r'\1 = 0.0', python_code)
        python_code = re.sub(r'char\s+(\w+)\s*;', r'\1 = ""', python_code)
        python_code = re.sub(r'double\s+(\w+)\s*;', r'\1 = 0.0', python_code)
        
        # Convert printf to print
        python_code = re.sub(r'printf\s*\(\s*"([^"]*)"\s*\)\s*;', r'print("\1")', python_code)
        python_code = re.sub(r'printf\s*\(\s*"([^"]*)"\s*,\s*([^)]+)\s*\)\s*;', r'print("\1" % (\2))', python_code)
        
        # Convert scanf to input
        python_code = re.sub(r'scanf\s*\(\s*"([^"]*)"\s*,\s*&(\w+)\s*\)\s*;', r'\2 = input("\1: ")', python_code)
        
        # Convert for loops
        python_code = re.sub(r'for\s*\(\s*int\s+(\w+)\s*=\s*(\d+)\s*;\s*\1\s*<\s*(\d+)\s*;\s*\1\+\+\)', r'for \1 in range(\2, \3):', python_code)
        
        # Convert while loops
        python_code = re.sub(r'while\s*\(([^)]+)\)\s*{', r'while \1:', python_code)
        
        # Convert if statements
        python_code = re.sub(r'if\s*\(([^)]+)\)\s*{', r'if \1:', python_code)
        python_code = re.sub(r'else\s*{', r'else:', python_code)
        
        # Convert switch statements
        python_code = re.sub(r'switch\s*\(([^)]+)\)\s*{', r'# switch \1:', python_code)
        python_code = re.sub(r'case\s+([^:]+):', r'# case \1:', python_code)
        python_code = re.sub(r'break;', r'# break', python_code)
        python_code = re.sub(r'default:', r'# default:', python_code)
        
        # Remove semicolons and braces
        python_code = re.sub(r';\s*$', '', python_code, flags=re.MULTILINE)
        python_code = re.sub(r'{\s*$', '', python_code, flags=re.MULTILINE)
        python_code = re.sub(r'^\s*}\s*$', '', python_code, flags=re.MULTILINE)
        
        # Add Python header
        header = f'# Converted from C: {filename}\n'
        header += '# Note: This is an automated conversion and may require manual adjustments\n\n'
        
        return header + python_code
    
    def _convert_python_to_javascript_basic(self, python_code: str, filename: str) -> str:
        """Basic Python to JavaScript conversion using regex"""
        js_code = python_code
        
        # Convert print statements
        js_code = re.sub(r'print\s*\(\s*([^)]+)\s*\)', r'console.log(\1)', js_code)
        
        # Convert function definitions
        js_code = re.sub(r'def\s+(\w+)\s*\(([^)]*)\):', r'function \1(\2) {', js_code)
        
        # Convert if/elif/else
        js_code = re.sub(r'if\s+([^:]+):', r'if (\1) {', js_code)
        js_code = re.sub(r'elif\s+([^:]+):', r'} else if (\1) {', js_code)
        js_code = re.sub(r'else:', r'} else {', js_code)
        
        # Convert for loops
        js_code = re.sub(r'for\s+(\w+)\s+in\s+range\s*\(([^)]+)\):', r'for (let \1 = 0; \1 < \2; \1++) {', js_code)
        js_code = re.sub(r'for\s+(\w+)\s+in\s+([^:]+):', r'for (let \1 of \2) {', js_code)
        
        # Convert while loops
        js_code = re.sub(r'while\s+([^:]+):', r'while (\1) {', js_code)
        
        # Convert variable assignments
        js_code = re.sub(r'^(\s*)(\w+)\s*=\s*([^#\n]+)', r'\1let \2 = \3', js_code, flags=re.MULTILINE)
        
        # Convert string literals
        js_code = re.sub(r"'([^']*)'", r'"\1"', js_code)
        
        # Convert True/False/None
        js_code = re.sub(r'\bTrue\b', 'true', js_code)
        js_code = re.sub(r'\bFalse\b', 'false', js_code)
        js_code = re.sub(r'\bNone\b', 'null', js_code)
        
        # Convert list to array
        js_code = re.sub(r'\[([^\]]*)\]', r'[\1]', js_code)
        
        # Convert try/except to try/catch
        js_code = re.sub(r'try:', r'try {', js_code)
        js_code = re.sub(r'except\s+(\w+)\s+as\s+(\w+):', r'} catch (\2) {', js_code)
        js_code = re.sub(r'except\s+(\w+):', r'} catch (\1) {', js_code)
        js_code = re.sub(r'except:', r'} catch (error) {', js_code)
        
        # Add JavaScript header
        header = f'// Converted from Python: {filename}\n'
        header += '// Note: This is an automated conversion and may require manual adjustments\n\n'
        
        return header + js_code
    
    def _convert_python_to_java_basic(self, python_code: str, filename: str) -> str:
        """Basic Python to Java conversion using regex"""
        # Extract class name from filename
        class_name = Path(filename).stem.replace('_', '').title()
        
        java_code = f"""// Converted from Python: {filename}
// Note: This is an automated conversion and may require manual adjustments

import java.util.*;
import java.io.*;

public class {class_name} {{
"""
        
        # Convert function definitions to methods
        lines = python_code.split('\n')
        in_function = False
        function_indent = 0
        
        for line in lines:
            # Skip Python shebang and docstrings
            if (line.strip().startswith('#!') or 
                line.strip().startswith('"""') or
                line.strip().startswith("'''")):
                continue
            
            # Convert function definitions
            func_match = re.match(r'def\s+(\w+)\s*\(([^)]*)\):', line)
            if func_match:
                func_name, params = func_match.groups()
                # Convert parameters to Java types
                param_list = []
                for param in params.split(','):
                    param = param.strip()
                    if param:
                        param_list.append(f"Object {param}")  # Default to Object type
                
                java_code += f"    public static Object {func_name}({', '.join(param_list)}) {{\n"
                in_function = True
                function_indent = len(line) - len(line.lstrip())
                continue
            
            # Convert print statements
            if 'print(' in line:
                line = re.sub(r'print\s*\(\s*([^)]+)\s*\)', r'System.out.println(\1)', line)
            
            # Convert if/elif/else
            if line.strip().startswith('if ') and line.strip().endswith(':'):
                line = re.sub(r'if\s+([^:]+):', r'if (\1) {', line)
            elif line.strip().startswith('elif ') and line.strip().endswith(':'):
                line = re.sub(r'elif\s+([^:]+):', r'} else if (\1) {', line)
            elif line.strip() == 'else:':
                line = '} else {'
            
            # Convert for loops
            if 'for ' in line and ' in ' in line and line.strip().endswith(':'):
                if 'range(' in line:
                    range_match = re.match(r'for\s+(\w+)\s+in\s+range\s*\(([^)]+)\):', line)
                    if range_match:
                        var, range_expr = range_match.groups()
                        if ',' in range_expr:
                            start, end = range_expr.split(',')
                            line = f"for (int {var} = {start}; {var} < {end}; {var}++) {{"
                        else:
                            line = f"for (int {var} = 0; {var} < {range_expr}; {var}++) {{"
                else:
                    for_match = re.match(r'for\s+(\w+)\s+in\s+([^:]+):', line)
                    if for_match:
                        var, iterable = for_match.groups()
                        line = f"for (Object {var} : {iterable}) {{"
            
            # Convert while loops
            if line.strip().startswith('while ') and line.strip().endswith(':'):
                line = re.sub(r'while\s+([^:]+):', r'while (\1) {', line)
            
            # Convert variable assignments
            assign_match = re.match(r'^(\s*)(\w+)\s*=\s*([^#\n]+)', line)
            if assign_match:
                indent, var, value = assign_match.groups()
                # Add type declaration for first assignment
                line = f"{indent}Object {var} = {value};"
            
            # Convert string literals
            line = re.sub(r"'([^']*)'", r'"\1"', line)
            
            # Convert True/False/None
            line = re.sub(r'\bTrue\b', 'true', line)
            line = re.sub(r'\bFalse\b', 'false', line)
            line = re.sub(r'\bNone\b', 'null', line)
            
            # Convert list to array
            line = re.sub(r'\[([^\]]*)\]', r'new Object[]{\1}', line)
            
            # Convert try/except
            if line.strip() == 'try:':
                line = 'try {'
            elif line.strip().startswith('except'):
                line = '} catch (Exception e) {'
            
            # Add the converted line
            if line.strip():
                # Adjust indentation for Java
                if in_function:
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent <= function_indent:
                        in_function = False
                        java_code += "    }\n"
                    else:
                        # Convert Python indentation to Java
                        java_indent = "        " + "    " * ((current_indent - function_indent - 4) // 4)
                        java_code += f"{java_indent}{line.strip()}\n"
                else:
                    java_code += f"    {line.strip()}\n"
        
        # Close the class
        java_code += "}\n"
        
        return java_code
    
    def _convert_java_to_python_basic(self, java_code: str, filename: str) -> str:
        """Basic Java to Python conversion using regex"""
        python_code = java_code
        
        # Remove Java imports and package declarations
        python_code = re.sub(r'import\s+[^;]+;', '', python_code)
        python_code = re.sub(r'package\s+[^;]+;', '', python_code)
        
        # Convert class structure
        python_code = re.sub(r'public\s+class\s+(\w+)', r'class \1', python_code)
        python_code = re.sub(r'public\s+static\s+void\s+main\s*\([^)]*\)\s*{', r'if __name__ == "__main__":', python_code)
        
        # Convert method definitions
        python_code = re.sub(r'public\s+static\s+(\w+)\s+(\w+)\s*\(([^)]*)\)\s*{', r'def \2(\3):', python_code)
        python_code = re.sub(r'public\s+(\w+)\s+(\w+)\s*\(([^)]*)\)\s*{', r'def \2(self, \3):', python_code)
        python_code = re.sub(r'private\s+(\w+)\s+(\w+)\s*\(([^)]*)\)\s*{', r'def \2(self, \3):', python_code)
        
        # Convert System.out.println to print
        python_code = re.sub(r'System\.out\.println\s*\(\s*([^)]+)\s*\)\s*;', r'print(\1)', python_code)
        
        # Convert variable declarations
        python_code = re.sub(r'(\w+)\s+(\w+)\s*=\s*([^;]+);', r'\2 = \3', python_code)
        python_code = re.sub(r'(\w+)\s+(\w+)\s*;', r'\2 = None', python_code)
        
        # Convert control structures
        python_code = re.sub(r'if\s*\(([^)]+)\)\s*{', r'if \1:', python_code)
        python_code = re.sub(r'else\s+if\s*\(([^)]+)\)\s*{', r'elif \1:', python_code)
        python_code = re.sub(r'else\s*{', r'else:', python_code)
        
        # Convert for loops
        python_code = re.sub(r'for\s*\(\s*int\s+(\w+)\s*=\s*(\d+)\s*;\s*\1\s*<\s*(\d+)\s*;\s*\1\+\+\)\s*{', r'for \1 in range(\2, \3):', python_code)
        python_code = re.sub(r'for\s*\(\s*(\w+)\s+(\w+)\s*:\s*([^)]+)\s*\)\s*{', r'for \2 in \3:', python_code)
        
        # Convert while loops
        python_code = re.sub(r'while\s*\(([^)]+)\)\s*{', r'while \1:', python_code)
        
        # Convert try/catch
        python_code = re.sub(r'try\s*{', r'try:', python_code)
        python_code = re.sub(r'}\s*catch\s*\([^)]+\)\s*{', r'except:', python_code)
        
        # Convert string literals
        python_code = re.sub(r'"([^"]*)"', r"'\1'", python_code)
        
        # Convert boolean literals
        python_code = re.sub(r'\btrue\b', 'True', python_code)
        python_code = re.sub(r'\bfalse\b', 'False', python_code)
        python_code = re.sub(r'\bnull\b', 'None', python_code)
        
        # Remove semicolons and braces
        python_code = re.sub(r';\s*$', '', python_code, flags=re.MULTILINE)
        python_code = re.sub(r'{\s*$', '', python_code, flags=re.MULTILINE)
        python_code = re.sub(r'^\s*}\s*$', '', python_code, flags=re.MULTILINE)
        
        # Add Python header
        header = f'# Converted from Java: {filename}\n'
        header += '# Note: This is an automated conversion and may require manual adjustments\n\n'
        
        return header + python_code
    
    def _convert_javascript_to_python_basic(self, js_code: str, filename: str) -> str:
        """Basic JavaScript to Python conversion using regex"""
        python_code = js_code
        
        # Convert console.log to print
        python_code = re.sub(r'console\.log\s*\(\s*([^)]+)\s*\)', r'print(\1)', python_code)
        
        # Convert function definitions
        python_code = re.sub(r'function\s+(\w+)\s*\(([^)]*)\)\s*{', r'def \1(\2):', python_code)
        python_code = re.sub(r'const\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>\s*{', r'def \1(\2):', python_code)
        python_code = re.sub(r'let\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>\s*{', r'def \1(\2):', python_code)
        
        # Convert variable declarations
        python_code = re.sub(r'const\s+(\w+)\s*=\s*([^;]+);', r'\1 = \2', python_code)
        python_code = re.sub(r'let\s+(\w+)\s*=\s*([^;]+);', r'\1 = \2', python_code)
        python_code = re.sub(r'var\s+(\w+)\s*=\s*([^;]+);', r'\1 = \2', python_code)
        
        # Convert control structures
        python_code = re.sub(r'if\s*\(([^)]+)\)\s*{', r'if \1:', python_code)
        python_code = re.sub(r'}?\s*else\s+if\s*\(([^)]+)\)\s*{', r'elif \1:', python_code)
        python_code = re.sub(r'}?\s*else\s*{', r'else:', python_code)
        
        # Convert for loops
        python_code = re.sub(r'for\s*\(\s*let\s+(\w+)\s*=\s*(\d+)\s*;\s*\1\s*<\s*(\d+)\s*;\s*\1\+\+\)\s*{', r'for \1 in range(\2, \3):', python_code)
        python_code = re.sub(r'for\s*\(\s*let\s+(\w+)\s+of\s+([^)]+)\s*\)\s*{', r'for \1 in \2:', python_code)
        
        # Convert while loops
        python_code = re.sub(r'while\s*\(([^)]+)\)\s*{', r'while \1:', python_code)
        
        # Convert try/catch
        python_code = re.sub(r'try\s*{', r'try:', python_code)
        python_code = re.sub(r'}\s*catch\s*\([^)]+\)\s*{', r'except:', python_code)
        
        # Convert string literals
        python_code = re.sub(r'"([^"]*)"', r"'\1'", python_code)
        
        # Convert boolean literals
        python_code = re.sub(r'\btrue\b', 'True', python_code)
        python_code = re.sub(r'\bfalse\b', 'False', python_code)
        python_code = re.sub(r'\bnull\b', 'None', python_code)
        
        # Convert array to list
        python_code = re.sub(r'\[([^\]]*)\]', r'[\1]', python_code)
        
        # Remove semicolons and braces
        python_code = re.sub(r';\s*$', '', python_code, flags=re.MULTILINE)
        python_code = re.sub(r'{\s*$', '', python_code, flags=re.MULTILINE)
        python_code = re.sub(r'^\s*}\s*$', '', python_code, flags=re.MULTILINE)
        
        # Add Python header
        header = f'# Converted from JavaScript: {filename}\n'
        header += '# Note: This is an automated conversion and may require manual adjustments\n\n'
        
        return header + python_code
    
    def _convert_typescript_to_python_basic(self, ts_code: str, filename: str) -> str:
        """Basic TypeScript to Python conversion using regex"""
        # First convert TypeScript to JavaScript, then to Python
        js_code = ts_code
        
        # Remove TypeScript type annotations
        js_code = re.sub(r':\s*\w+(?:<[^>]+>)?(?:\s*\|\s*\w+)*', '', js_code)
        js_code = re.sub(r'interface\s+\w+\s*{[^}]*}', '', js_code)
        js_code = re.sub(r'type\s+\w+\s*=\s*[^;]+;', '', js_code)
        js_code = re.sub(r'enum\s+\w+\s*{[^}]*}', '', js_code)
        
        # Convert to Python using the JavaScript converter
        return self._convert_javascript_to_python_basic(js_code, filename)
    
    def _convert_java_to_javascript_basic(self, java_code: str, filename: str) -> str:
        """Basic Java to JavaScript conversion using regex"""
        js_code = java_code
        
        # Remove Java imports and package declarations
        js_code = re.sub(r'import\s+[^;]+;', '', js_code)
        js_code = re.sub(r'package\s+[^;]+;', '', js_code)
        
        # Convert class structure
        js_code = re.sub(r'public\s+class\s+(\w+)', r'class \1 {', js_code)
        js_code = re.sub(r'public\s+static\s+void\s+main\s*\([^)]*\)\s*{', r'// Main function', js_code)
        
        # Convert method definitions
        js_code = re.sub(r'public\s+static\s+(\w+)\s+(\w+)\s*\(([^)]*)\)\s*{', r'static \2(\3) {', js_code)
        js_code = re.sub(r'public\s+(\w+)\s+(\w+)\s*\(([^)]*)\)\s*{', r'\2(\3) {', js_code)
        
        # Convert System.out.println to console.log
        js_code = re.sub(r'System\.out\.println\s*\(\s*([^)]+)\s*\)\s*;', r'console.log(\1);', js_code)
        
        # Convert variable declarations
        js_code = re.sub(r'(\w+)\s+(\w+)\s*=\s*([^;]+);', r'let \2 = \3;', js_code)
        js_code = re.sub(r'(\w+)\s+(\w+)\s*;', r'let \2;', js_code)
        
        # Convert control structures
        js_code = re.sub(r'if\s*\(([^)]+)\)\s*{', r'if (\1) {', js_code)
        js_code = re.sub(r'else\s+if\s*\(([^)]+)\)\s*{', r'} else if (\1) {', js_code)
        js_code = re.sub(r'else\s*{', r'} else {', js_code)
        
        # Convert for loops
        js_code = re.sub(r'for\s*\(\s*int\s+(\w+)\s*=\s*(\d+)\s*;\s*\1\s*<\s*(\d+)\s*;\s*\1\+\+\)\s*{', r'for (let \1 = \2; \1 < \3; \1++) {', js_code)
        
        # Convert while loops
        js_code = re.sub(r'while\s*\(([^)]+)\)\s*{', r'while (\1) {', js_code)
        
        # Convert try/catch
        js_code = re.sub(r'try\s*{', r'try {', js_code)
        js_code = re.sub(r'}\s*catch\s*\([^)]+\)\s*{', r'} catch (error) {', js_code)
        
        # Convert string literals
        js_code = re.sub(r'"([^"]*)"', r'"\1"', js_code)
        
        # Convert boolean literals
        js_code = re.sub(r'\btrue\b', 'true', js_code)
        js_code = re.sub(r'\bfalse\b', 'false', js_code)
        js_code = re.sub(r'\bnull\b', 'null', js_code)
        
        # Add JavaScript header
        header = f'// Converted from Java: {filename}\n'
        header += '// Note: This is an automated conversion and may require manual adjustments\n\n'
        
        return header + js_code
    
    def _convert_javascript_to_java_basic(self, js_code: str, filename: str) -> str:
        """Basic JavaScript to Java conversion using regex"""
        # Extract class name from filename
        class_name = Path(filename).stem.replace('_', '').title()
        
        java_code = f"""// Converted from JavaScript: {filename}
// Note: This is an automated conversion and may require manual adjustments

import java.util.*;
import java.io.*;

public class {class_name} {{
"""
        
        # Convert console.log to System.out.println
        java_code = re.sub(r'console\.log\s*\(\s*([^)]+)\s*\)', r'System.out.println(\1)', java_code)
        
        # Convert function definitions to methods
        java_code = re.sub(r'function\s+(\w+)\s*\(([^)]*)\)\s*{', r'    public static Object \1(\2) {', java_code)
        java_code = re.sub(r'const\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>\s*{', r'    public static Object \1(\2) {', java_code)
        
        # Convert variable declarations
        java_code = re.sub(r'const\s+(\w+)\s*=\s*([^;]+);', r'        Object \1 = \2;', java_code)
        java_code = re.sub(r'let\s+(\w+)\s*=\s*([^;]+);', r'        Object \1 = \2;', java_code)
        java_code = re.sub(r'var\s+(\w+)\s*=\s*([^;]+);', r'        Object \1 = \2;', java_code)
        
        # Convert control structures
        java_code = re.sub(r'if\s*\(([^)]+)\)\s*{', r'        if (\1) {', java_code)
        java_code = re.sub(r'}?\s*else\s+if\s*\(([^)]+)\)\s*{', r'        } else if (\1) {', java_code)
        java_code = re.sub(r'}?\s*else\s*{', r'        } else {', java_code)
        
        # Convert for loops
        java_code = re.sub(r'for\s*\(\s*let\s+(\w+)\s*=\s*(\d+)\s*;\s*\1\s*<\s*(\d+)\s*;\s*\1\+\+\)\s*{', r'        for (int \1 = \2; \1 < \3; \1++) {', java_code)
        
        # Convert while loops
        java_code = re.sub(r'while\s*\(([^)]+)\)\s*{', r'        while (\1) {', java_code)
        
        # Convert try/catch
        java_code = re.sub(r'try\s*{', r'        try {', java_code)
        java_code = re.sub(r'}\s*catch\s*\([^)]+\)\s*{', r'        } catch (Exception e) {', java_code)
        
        # Convert string literals
        java_code = re.sub(r'"([^"]*)"', r'"\1"', java_code)
        
        # Convert boolean literals
        java_code = re.sub(r'\btrue\b', 'true', java_code)
        java_code = re.sub(r'\bfalse\b', 'false', java_code)
        java_code = re.sub(r'\bnull\b', 'null', java_code)
        
        # Close the class
        java_code += "}\n"
        
        return java_code
    
    def _generate_project_files(self, target_path: Path, conversion_type: str):
        """Generate project-specific files"""
        if conversion_type == 'c_to_python':
            # Generate requirements.txt
            requirements = """# Python dependencies for converted project
# Add your project dependencies here
"""
            with open(target_path / 'requirements.txt', 'w') as f:
                f.write(requirements)
            
            # Generate README
            readme = """# Python Project (Converted from C)

This project was automatically converted from C to Python.

## Setup
```bash
pip install -r requirements.txt
```

## Usage
Run the main script:
```bash
python main.py
```

## Notes
- This is an automated conversion and may require manual adjustments
- Review the converted code for Python-specific optimizations
- Consider using Python libraries for better performance
"""
            with open(target_path / 'README.md', 'w') as f:
                f.write(readme)
                
        elif conversion_type in ['python_to_javascript', 'java_to_javascript', 'javascript_to_javascript']:
            # Generate package.json for JavaScript projects
            package_json = {
                "name": "converted-project",
                "version": "1.0.0",
                "description": f"JavaScript project converted from {conversion_type.split('_to_')[0].title()}",
                "main": "index.js",
                "scripts": {
                    "start": "node index.js",
                    "test": "echo \"Error: no test specified\" && exit 1"
                },
                "keywords": [],
                "author": "",
                "license": "ISC"
            }
            
            with open(target_path / 'package.json', 'w') as f:
                json.dump(package_json, f, indent=2)
            
            # Generate README
            source_lang = conversion_type.split('_to_')[0].title()
            readme = f"""# JavaScript Project (Converted from {source_lang})

This project was automatically converted from {source_lang} to JavaScript.

## Setup
```bash
npm install
```

## Usage
Run the main script:
```bash
npm start
```

## Notes
- This is an automated conversion and may require manual adjustments
- Review the converted code for JavaScript-specific optimizations
- Consider using modern JavaScript features (ES6+) for better code
"""
            with open(target_path / 'README.md', 'w') as f:
                f.write(readme)
                
        elif conversion_type in ['python_to_java', 'javascript_to_java', 'java_to_java']:
            # Generate pom.xml for Maven
            source_lang = conversion_type.split('_to_')[0].title()
            pom_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.converted</groupId>
    <artifactId>converted-project</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>
    
    <name>Converted Project</name>
    <description>Java project converted from {source_lang}</description>
    
    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
    
    <dependencies>
        <!-- Add your dependencies here -->
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.8.1</version>
                <configuration>
                    <source>11</source>
                    <target>11</target>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>"""
            
            with open(target_path / 'pom.xml', 'w') as f:
                f.write(pom_xml)
            
            # Generate README
            readme = f"""# Java Project (Converted from {source_lang})

This project was automatically converted from {source_lang} to Java.

## Setup
```bash
# Using Maven
mvn compile
mvn exec:java -Dexec.mainClass="Main"

# Using Java directly
javac *.java
java Main
```

## Notes
- This is an automated conversion and may require manual adjustments
- Review the converted code for Java-specific optimizations
- Consider using Java libraries and frameworks for better functionality
- Add proper exception handling and type safety
"""
            with open(target_path / 'README.md', 'w') as f:
                f.write(readme)
                
        elif conversion_type in ['java_to_python', 'javascript_to_python', 'typescript_to_python']:
            # Generate requirements.txt for Python projects
            requirements = """# Python dependencies for converted project
# Add your project dependencies here
"""
            with open(target_path / 'requirements.txt', 'w') as f:
                f.write(requirements)
            
            # Generate README
            source_lang = conversion_type.split('_to_')[0].title()
            readme = f"""# Python Project (Converted from {source_lang})

This project was automatically converted from {source_lang} to Python.

## Setup
```bash
pip install -r requirements.txt
```

## Usage
Run the main script:
```bash
python main.py
```

## Notes
- This is an automated conversion and may require manual adjustments
- Review the converted code for Python-specific optimizations
- Consider using Python libraries for better performance
"""
            with open(target_path / 'README.md', 'w') as f:
                f.write(readme)
            # Generate pom.xml for Maven
            pom_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.converted</groupId>
    <artifactId>converted-project</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>
    
    <name>Converted Project</name>
    <description>Java project converted from Python</description>
    
    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
    
    <dependencies>
        <!-- Add your dependencies here -->
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.8.1</version>
                <configuration>
                    <source>11</source>
                    <target>11</target>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>"""
            
            with open(target_path / 'pom.xml', 'w') as f:
                f.write(pom_xml)
            
            # Generate README
            readme = """# Java Project (Converted from Python)

This project was automatically converted from Python to Java.

## Setup
```bash
# Using Maven
mvn compile
mvn exec:java -Dexec.mainClass="Main"

# Using Java directly
javac *.java
java Main
```

## Notes
- This is an automated conversion and may require manual adjustments
- Review the converted code for Java-specific optimizations
- Consider using Java libraries and frameworks for better functionality
- Add proper exception handling and type safety
"""
            with open(target_path / 'README.md', 'w') as f:
                f.write(readme)

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert code between programming languages with AI assistance')
    parser.add_argument('source_dir', help='Source directory containing code to convert')
    parser.add_argument('target_dir', help='Target directory for converted code')
    parser.add_argument('--type', choices=[
        'c_to_python', 'python_to_javascript', 'python_to_java',
        'java_to_python', 'javascript_to_python', 'typescript_to_python',
        'java_to_javascript', 'javascript_to_java'
    ], required=True, help='Type of conversion to perform')
    parser.add_argument('--no-ai', action='store_true', help='Disable AI assistance')
    parser.add_argument('--model', default='gemma-3n-2b', help='Model to use for conversion')
    
    args = parser.parse_args()
    
    converter = EnhancedCodeConverter(use_ai=not args.no_ai, model_name=args.model)
    results = converter.convert_project(args.source_dir, args.target_dir, args.type)
    
    # Print results
    print(f"\n=== Conversion Results ===")
    print(f"Type: {results['conversion_type']}")
    print(f"Source: {results['source_dir']}")
    print(f"Target: {results['target_dir']}")
    print(f"Files converted: {len(results['files_converted'])}")
    print(f"AI used: {results['ai_used']}")
    
    if results['errors']:
        print(f"\nErrors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"  {error['file']}: {error['error']}")
    
    if results['warnings']:
        print(f"\nWarnings: {len(results['warnings'])}")
        for warning in results['warnings']:
            print(f"  {warning}")
    
    print(f"\nConversion completed! Check the target directory for results.")

if __name__ == "__main__":
    main() 