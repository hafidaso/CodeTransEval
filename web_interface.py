#!/usr/bin/env python3
"""
Web Interface for Code Conversion Pipeline
Provides a user-friendly web interface for converting projects between programming languages
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
import json
import zipfile
import tempfile
import shutil
from pathlib import Path
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

# Import our conversion pipeline
try:
    from enhanced_code_converter import EnhancedCodeConverter
except ImportError:
    from improved_code_converter import ImprovedCodeConverter as EnhancedCodeConverter

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configuration
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
ALLOWED_EXTENSIONS = {'zip', 'tar', 'gz', 'rar'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Create directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_next_steps_guidance(conversion_type, ai_used, files_converted, errors):
    """Generate next steps guidance based on conversion results"""
    guidance = {
        "what_to_do": [
            "Download the converted project",
            "Review the converted code",
            "Test the converted project", 
            "Make manual adjustments if needed"
        ],
        "important_notes": [
            "This is an automated conversion",
            "Manual review is recommended",
            "Test thoroughly before production use",
            "Check for security implications"
        ],
        "detailed_guidance": {
            "review_code": [
                "Check for syntax errors in the target language",
                "Verify that all functions and logic are preserved",
                "Review variable names and data types",
                "Ensure proper error handling and exceptions",
                "Check for language-specific best practices"
            ],
            "test_project": [
                "Run the converted code with sample inputs",
                "Compare output with the original program",
                "Test edge cases and error conditions",
                "Check for memory leaks or performance issues",
                "Verify all dependencies are properly included"
            ],
            "security_considerations": [
                "Review input validation and sanitization",
                "Check for potential injection vulnerabilities",
                "Verify secure handling of sensitive data",
                "Ensure proper authentication and authorization",
                "Review file and network access permissions"
            ]
        },
        "conversion_specific_notes": []
    }
    
    # Add conversion-specific guidance
    if conversion_type == "c_to_python":
        guidance["conversion_specific_notes"].extend([
            "Review memory management (C pointers converted to Python references)",
            "Check for C-specific optimizations that may need Python equivalents",
            "Verify that C structs are properly converted to Python classes",
            "Review any platform-specific code that may not work in Python"
        ])
    elif conversion_type == "python_to_javascript":
        guidance["conversion_specific_notes"].extend([
            "Review Python-specific libraries that may not have JS equivalents",
            "Check for Python list comprehensions converted to JavaScript",
            "Verify that Python exceptions are properly converted to JavaScript error handling",
            "Review any Python-specific syntax that may need manual adjustment"
        ])
    elif conversion_type == "python_to_java":
        guidance["conversion_specific_notes"].extend([
            "Review Python dynamic typing converted to Java static typing",
            "Check for Python list comprehensions converted to Java streams",
            "Verify that Python exceptions are properly converted to Java exceptions",
            "Review any Python-specific libraries that may need Java equivalents"
        ])
    elif conversion_type == "java_to_python":
        guidance["conversion_specific_notes"].extend([
            "Review Java static typing converted to Python dynamic typing",
            "Check for Java interfaces and abstract classes converted to Python",
            "Verify that Java exceptions are properly converted to Python exceptions",
            "Review any Java-specific libraries that may need Python equivalents"
        ])
    elif conversion_type == "javascript_to_python":
        guidance["conversion_specific_notes"].extend([
            "Review JavaScript async/await converted to Python async/await",
            "Check for JavaScript promises converted to Python asyncio",
            "Verify that JavaScript objects are properly converted to Python dictionaries",
            "Review any JavaScript-specific libraries that may need Python equivalents"
        ])
    elif conversion_type == "typescript_to_python":
        guidance["conversion_specific_notes"].extend([
            "Review TypeScript type annotations removed for Python dynamic typing",
            "Check for TypeScript interfaces converted to Python classes or type hints",
            "Verify that TypeScript enums are properly converted to Python enums",
            "Review any TypeScript-specific features that may need Python equivalents"
        ])
    elif conversion_type == "java_to_javascript":
        guidance["conversion_specific_notes"].extend([
            "Review Java static typing converted to JavaScript dynamic typing",
            "Check for Java interfaces and abstract classes converted to JavaScript",
            "Verify that Java exceptions are properly converted to JavaScript error handling",
            "Review any Java-specific libraries that may need JavaScript equivalents"
        ])
    elif conversion_type == "javascript_to_java":
        guidance["conversion_specific_notes"].extend([
            "Review JavaScript dynamic typing converted to Java static typing",
            "Check for JavaScript async/await converted to Java CompletableFuture",
            "Verify that JavaScript objects are properly converted to Java classes",
            "Review any JavaScript-specific libraries that may need Java equivalents"
        ])
    
    # Add AI-specific guidance
    if ai_used:
        guidance["conversion_specific_notes"].append(
            "AI-enhanced conversion may include additional optimizations and improvements"
        )
    
    # Add error-specific guidance
    if errors:
        guidance["conversion_specific_notes"].append(
            f"Manual review required for {len(errors)} files that had conversion errors"
        )
    
    return guidance

def extract_project(file_path, extract_dir):
    """Extract uploaded project archive"""
    try:
        if file_path.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        # Add support for other archive types as needed
        return True
    except Exception as e:
        print(f"Extraction error: {e}")
        return False

@app.route('/')
def index():
    """Main page with upload form"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and conversion"""
    if 'project_file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['project_file']
    conversion_type = request.form.get('conversion_type', 'c_to_python')
    use_ai = request.form.get('use_ai', 'true') == 'true'
    
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        session_dir = os.path.join(UPLOAD_FOLDER, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(session_dir, filename)
        file.save(file_path)
        
        # Extract project
        extract_dir = os.path.join(session_dir, 'extracted')
        os.makedirs(extract_dir, exist_ok=True)
        
        if not extract_project(file_path, extract_dir):
            flash('Failed to extract project archive')
            return redirect(request.url)
        
        # Find the main project directory (handle nested archives)
        project_dir = extract_dir
        while True:
            contents = os.listdir(project_dir)
            if len(contents) == 1 and os.path.isdir(os.path.join(project_dir, contents[0])):
                project_dir = os.path.join(project_dir, contents[0])
            else:
                break
        
        # Convert project
        try:
            converter = EnhancedCodeConverter(use_ai=use_ai, enable_phase2=True)
            target_dir = os.path.join(CONVERTED_FOLDER, session_id)
            
            results = converter.convert_project(project_dir, target_dir, conversion_type)
            print('DEBUG: phase2 in results:', 'phase2' in results)
            if 'phase2' not in results:
                print('DEBUG: results keys:', list(results.keys()))
            # Add Next Steps guidance to results
            results['next_steps'] = generate_next_steps_guidance(
                conversion_type, 
                use_ai, 
                results.get('files_converted', []), 
                results.get('errors', [])
            )
            
            # Store results for download
            results_file = os.path.join(session_dir, 'results.json')
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'results': results,
                'download_url': f'/download/{session_id}'
            })
            
        except Exception as e:
            print('DEBUG: Exception during conversion:', e)
            import traceback
            traceback.print_exc()
            flash(f'Conversion failed: {str(e)}')
            return jsonify({'success': False, 'error': str(e)})
    
    flash('Invalid file type')
    return redirect(request.url)

@app.route('/download/<session_id>')
def download_converted(session_id):
    """Download converted project"""
    converted_dir = os.path.join(CONVERTED_FOLDER, session_id)
    if not os.path.exists(converted_dir):
        flash('Converted project not found')
        return redirect(url_for('index'))
    
    # Create zip file
    zip_path = os.path.join(CONVERTED_FOLDER, f'{session_id}_converted.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(converted_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, converted_dir)
                zipf.write(file_path, arcname)
    
    return send_file(zip_path, as_attachment=True, download_name=f'converted_project_{session_id}.zip')

@app.route('/results/<session_id>')
def view_results(session_id):
    """View conversion results"""
    results_file = os.path.join(UPLOAD_FOLDER, session_id, 'results.json')
    if not os.path.exists(results_file):
        flash('Results not found')
        return redirect(url_for('index'))
    
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    return render_template('results.html', results=results, session_id=session_id)

@app.route('/api/convert', methods=['POST'])
def api_convert():
    """API endpoint for programmatic conversion"""
    data = request.get_json()
    
    if not data or 'source_dir' not in data or 'target_dir' not in data or 'conversion_type' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    try:
        converter = EnhancedCodeConverter(use_ai=data.get('use_ai', True), enable_phase2=True)
        results = converter.convert_project(
            data['source_dir'],
            data['target_dir'],
            data['conversion_type']
        )
        
        # Add Next Steps guidance to API results
        results['next_steps'] = generate_next_steps_guidance(
            data['conversion_type'],
            data.get('use_ai', True),
            results.get('files_converted', []),
            results.get('errors', [])
        )
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Add debug prints to see what's happening with imports
    print("DEBUG: Testing Phase 2 imports...")
    try:
        from enhanced_code_converter import EnhancedCodeConverter
        converter = EnhancedCodeConverter(enable_phase2=True)
        print("DEBUG: Phase 2 modules loaded successfully in web_interface.py")
    except Exception as e:
        print(f"DEBUG: Error loading Phase 2 modules: {e}")
        import traceback
        traceback.print_exc()
    
    app.run(debug=True, host='0.0.0.0', port=5001) 