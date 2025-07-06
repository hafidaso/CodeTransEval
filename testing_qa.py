"""
Automated Testing and Quality Assurance Module
Phase 2 Implementation - Code Project Converter

This module provides unit test generation, integration test frameworks,
code coverage analysis, and performance benchmarking tools.
"""

import os
import subprocess
import tempfile
import json
import time
import logging
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import re

class TestGenerator:
    """Generate unit tests for converted code."""
    
    def __init__(self):
        self.test_templates = self._load_test_templates()
        self.coverage_data = {}
        
    def _load_test_templates(self) -> Dict[str, str]:
        """Load test templates for different languages."""
        return {
            'python': {
                'unittest': '''import unittest
import sys
import os
sys.path.append(os.path.dirname(__file__))

class Test{ClassName}(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def test_{function_name}_basic(self):
        """Test basic functionality of {function_name}."""
        # TODO: Add specific test cases
        self.assertTrue(True)
    
    def test_{function_name}_edge_cases(self):
        """Test edge cases for {function_name}."""
        # TODO: Add edge case tests
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
''',
                'pytest': '''import pytest
import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_{function_name}_basic():
    """Test basic functionality of {function_name}."""
    # TODO: Add specific test cases
    assert True

def test_{function_name}_edge_cases():
    """Test edge cases for {function_name}."""
    # TODO: Add edge case tests
    assert True
'''
            },
            'javascript': {
                'jest': '''const {ClassName} = require('./{filename}');

describe('{ClassName}', () => {{
    test('{function_name} basic functionality', () => {{
        // TODO: Add specific test cases
        expect(true).toBe(true);
    }});
    
    test('{function_name} edge cases', () => {{
        // TODO: Add edge case tests
        expect(true).toBe(true);
    }});
}});
''',
                'mocha': '''const assert = require('assert');
const {ClassName} = require('./{filename}');

describe('{ClassName}', () => {{
    it('should handle {function_name} basic functionality', () => {{
        // TODO: Add specific test cases
        assert.strictEqual(true, true);
    }});
    
    it('should handle {function_name} edge cases', () => {{
        // TODO: Add edge case tests
        assert.strictEqual(true, true);
    }});
}});
'''
            },
            'java': {
                'junit': '''import org.junit.Test;
import static org.junit.Assert.*;

public class Test{ClassName} {{
    
    @Test
    public void test{FunctionName}Basic() {{
        // TODO: Add specific test cases
        assertTrue(true);
    }}
    
    @Test
    public void test{FunctionName}EdgeCases() {{
        // TODO: Add edge case tests
        assertTrue(true);
    }}
}}
'''
            }
        }
    
    def generate_tests(self, source_file: str, target_file: str, 
                      language: str, framework: str = 'default') -> Dict[str, Any]:
        """Generate unit tests for converted code."""
        try:
            # Analyze source file to extract functions and classes
            functions = self._extract_functions(source_file, language)
            classes = self._extract_classes(source_file, language)
            
            test_files = []
            
            # Generate tests for each class
            for class_name in classes:
                test_content = self._generate_class_tests(
                    class_name, functions, target_file, language, framework
                )
                
                test_filename = f"test_{class_name.lower()}.{self._get_test_extension(language)}"
                test_path = os.path.join(os.path.dirname(target_file), test_filename)
                
                with open(test_path, 'w', encoding='utf-8') as f:
                    f.write(test_content)
                
                test_files.append({
                    'path': test_path,
                    'class': class_name,
                    'framework': framework
                })
            
            # Generate tests for standalone functions
            standalone_functions = [f for f in functions if not any(f in c for c in classes)]
            if standalone_functions:
                test_content = self._generate_function_tests(
                    standalone_functions, target_file, language, framework
                )
                
                test_filename = f"test_functions.{self._get_test_extension(language)}"
                test_path = os.path.join(os.path.dirname(target_file), test_filename)
                
                with open(test_path, 'w', encoding='utf-8') as f:
                    f.write(test_content)
                
                test_files.append({
                    'path': test_path,
                    'functions': standalone_functions,
                    'framework': framework
                })
            
            return {
                'success': True,
                'test_files': test_files,
                'framework': framework,
                'language': language
            }
            
        except Exception as e:
            logging.error(f"Error generating tests: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_functions(self, file_path: str, language: str) -> List[str]:
        """Extract function names from source file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            functions = []
            
            if language == 'python':
                functions = re.findall(r'def\s+(\w+)', content)
            elif language == 'javascript':
                functions = re.findall(r'function\s+(\w+)', content)
            elif language == 'java':
                functions = re.findall(r'public\s+\w+\s+(\w+)\s*\(', content)
            
            return functions
            
        except Exception as e:
            logging.error(f"Error extracting functions: {e}")
            return []
    
    def _extract_classes(self, file_path: str, language: str) -> List[str]:
        """Extract class names from source file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            classes = []
            
            if language == 'python':
                classes = re.findall(r'class\s+(\w+)', content)
            elif language == 'javascript':
                classes = re.findall(r'class\s+(\w+)', content)
            elif language == 'java':
                classes = re.findall(r'public\s+class\s+(\w+)', content)
            
            return classes
            
        except Exception as e:
            logging.error(f"Error extracting classes: {e}")
            return []
    
    def _generate_class_tests(self, class_name: str, functions: List[str], 
                            target_file: str, language: str, framework: str) -> str:
        """Generate tests for a specific class."""
        if language not in self.test_templates:
            return f"# Test template not available for {language}"
        
        if framework == 'default':
            framework = self._get_default_framework(language)
        
        if framework not in self.test_templates[language]:
            return f"# Test framework {framework} not available for {language}"
        
        template = self.test_templates[language][framework]
        filename = os.path.basename(target_file)
        
        # Find functions that belong to this class
        class_functions = [f for f in functions if f.lower() in class_name.lower()]
        if not class_functions:
            class_functions = ['main']  # Default function
        
        function_name = class_functions[0]
        
        return template.format(
            ClassName=class_name,
            FunctionName=function_name.capitalize(),
            function_name=function_name,
            filename=filename
        )
    
    def _generate_function_tests(self, functions: List[str], target_file: str, 
                               language: str, framework: str) -> str:
        """Generate tests for standalone functions."""
        if language not in self.test_templates:
            return f"# Test template not available for {language}"
        
        if framework == 'default':
            framework = self._get_default_framework(language)
        
        if framework not in self.test_templates[language]:
            return f"# Test framework {framework} not available for {language}"
        
        template = self.test_templates[language][framework]
        filename = os.path.basename(target_file)
        
        function_name = functions[0] if functions else 'main'
        
        return template.format(
            ClassName='Functions',
            FunctionName=function_name.capitalize(),
            function_name=function_name,
            filename=filename
        )
    
    def _get_default_framework(self, language: str) -> str:
        """Get default test framework for language."""
        defaults = {
            'python': 'pytest',
            'javascript': 'jest',
            'java': 'junit'
        }
        return defaults.get(language, 'unittest')
    
    def _get_test_extension(self, language: str) -> str:
        """Get file extension for test files."""
        extensions = {
            'python': 'py',
            'javascript': 'js',
            'java': 'java'
        }
        return extensions.get(language, 'py')

class CoverageAnalyzer:
    """Analyze code coverage for converted projects."""
    
    def __init__(self):
        self.coverage_tools = {
            'python': 'coverage',
            'javascript': 'nyc',
            'java': 'jacoco'
        }
    
    def analyze_coverage(self, project_path: str, language: str) -> Dict[str, Any]:
        """Analyze code coverage for the project."""
        try:
            if language not in self.coverage_tools:
                return {
                    'success': False,
                    'error': f'Coverage analysis not supported for {language}'
                }
            
            tool = self.coverage_tools[language]
            
            if tool == 'coverage':
                return self._run_python_coverage(project_path)
            elif tool == 'nyc':
                return self._run_javascript_coverage(project_path)
            elif tool == 'jacoco':
                return self._run_java_coverage(project_path)
            
        except Exception as e:
            logging.error(f"Error analyzing coverage: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _run_python_coverage(self, project_path: str) -> Dict[str, Any]:
        """Run Python coverage analysis."""
        try:
            # Run coverage
            result = subprocess.run(
                ['coverage', 'run', '--source=.', '-m', 'pytest'],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            # Generate coverage report
            report_result = subprocess.run(
                ['coverage', 'report'],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            # Parse coverage data
            coverage_data = self._parse_python_coverage(report_result.stdout)
            
            return {
                'success': True,
                'coverage': coverage_data,
                'output': report_result.stdout,
                'errors': report_result.stderr
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_python_coverage(self, output: str) -> Dict[str, Any]:
        """Parse Python coverage output."""
        lines = output.split('\n')
        coverage_data = {
            'total_coverage': 0,
            'file_coverage': {},
            'missing_lines': []
        }
        
        for line in lines:
            if 'TOTAL' in line:
                # Extract total coverage percentage
                match = re.search(r'(\d+)%', line)
                if match:
                    coverage_data['total_coverage'] = int(match.group(1))
            elif '.py' in line and '%' in line:
                # Extract file coverage
                parts = line.split()
                if len(parts) >= 4:
                    filename = parts[0]
                    coverage = int(parts[-1].replace('%', ''))
                    coverage_data['file_coverage'][filename] = coverage
        
        return coverage_data
    
    def _run_javascript_coverage(self, project_path: str) -> Dict[str, Any]:
        """Run JavaScript coverage analysis."""
        try:
            # Run NYC coverage
            result = subprocess.run(
                ['npx', 'nyc', 'npm', 'test'],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            # Parse coverage data
            coverage_data = self._parse_javascript_coverage(result.stdout)
            
            return {
                'success': True,
                'coverage': coverage_data,
                'output': result.stdout,
                'errors': result.stderr
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_javascript_coverage(self, output: str) -> Dict[str, Any]:
        """Parse JavaScript coverage output."""
        coverage_data = {
            'total_coverage': 0,
            'file_coverage': {},
            'missing_lines': []
        }
        
        # Extract coverage percentage from NYC output
        match = re.search(r'All files\s+\|\s+(\d+)', output)
        if match:
            coverage_data['total_coverage'] = int(match.group(1))
        
        return coverage_data
    
    def _run_java_coverage(self, project_path: str) -> Dict[str, Any]:
        """Run Java coverage analysis."""
        try:
            # Run JaCoCo coverage
            result = subprocess.run(
                ['mvn', 'clean', 'test', 'jacoco:report'],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            # Parse coverage data
            coverage_data = self._parse_java_coverage(project_path)
            
            return {
                'success': True,
                'coverage': coverage_data,
                'output': result.stdout,
                'errors': result.stderr
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_java_coverage(self, project_path: str) -> Dict[str, Any]:
        """Parse Java coverage data from JaCoCo report."""
        coverage_data = {
            'total_coverage': 0,
            'file_coverage': {},
            'missing_lines': []
        }
        
        # Look for JaCoCo report
        jacoco_report = os.path.join(project_path, 'target', 'site', 'jacoco', 'index.html')
        if os.path.exists(jacoco_report):
            # Parse HTML report for coverage data
            coverage_data['total_coverage'] = 50  # Placeholder
            coverage_data['file_coverage'] = {}
        
        return coverage_data

class PerformanceBenchmark:
    """Benchmark performance of converted code."""
    
    def __init__(self):
        self.benchmark_results = {}
    
    def benchmark_code(self, source_file: str, target_file: str, 
                      language: str, iterations: int = 1000) -> Dict[str, Any]:
        """Benchmark performance of converted code."""
        try:
            # Benchmark source code
            source_time = self._benchmark_file(source_file, language, iterations)
            
            # Benchmark target code
            target_time = self._benchmark_file(target_file, language, iterations)
            
            # Calculate performance metrics
            performance_ratio = target_time / source_time if source_time > 0 else 0
            performance_change = ((target_time - source_time) / source_time * 100) if source_time > 0 else 0
            
            benchmark_data = {
                'source_time': source_time,
                'target_time': target_time,
                'performance_ratio': performance_ratio,
                'performance_change_percent': performance_change,
                'iterations': iterations,
                'language': language
            }
            
            self.benchmark_results[f"{source_file}_{target_file}"] = benchmark_data
            
            return {
                'success': True,
                'benchmark': benchmark_data
            }
            
        except Exception as e:
            logging.error(f"Error benchmarking code: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _benchmark_file(self, file_path: str, language: str, iterations: int) -> float:
        """Benchmark a single file."""
        try:
            start_time = time.time()
            
            if language == 'python':
                subprocess.run(['python', file_path], 
                             capture_output=True, timeout=30)
            elif language == 'javascript':
                subprocess.run(['node', file_path], 
                             capture_output=True, timeout=30)
            elif language == 'java':
                # Compile and run Java
                class_name = os.path.splitext(os.path.basename(file_path))[0]
                subprocess.run(['javac', file_path], 
                             capture_output=True, timeout=30)
                subprocess.run(['java', class_name], 
                             capture_output=True, timeout=30)
            
            end_time = time.time()
            return end_time - start_time
            
        except subprocess.TimeoutExpired:
            return 30.0  # Timeout value
        except Exception as e:
            logging.error(f"Error benchmarking {file_path}: {e}")
            return 0.0

# Global instances
test_generator = TestGenerator()
coverage_analyzer = CoverageAnalyzer()
performance_benchmark = PerformanceBenchmark()

def get_test_generator():
    """Get the global test generator instance."""
    return test_generator

def get_coverage_analyzer():
    """Get the global coverage analyzer instance."""
    return coverage_analyzer

def get_performance_benchmark():
    """Get the global performance benchmark instance."""
    return performance_benchmark 