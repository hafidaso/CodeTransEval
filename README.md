# Code Project Converter

**Simple and Fast Code Translation Tool**  
*Convert projects between C, Python, JavaScript, and Java*

## 🚀 Overview

Code Project Converter is a lightweight tool that translates code projects between different programming languages. It supports converting C projects to Python, Python to JavaScript, and Python to Java.

## ✨ Features

- **Multi-file Project Support**: Convert entire projects, not just single files
- **Web Interface**: Easy-to-use web interface for uploading and converting projects
- **Multiple Language Support**: 8 language pairs including C, Python, JavaScript, TypeScript, and Java
- **Intelligent AI Model Selection**: Automatically selects the best AI model for each conversion type
- **AI-Powered Conversion**: Optional AI integration with fallback models and performance tracking
- **Project Structure Preservation**: Maintains directory structure and file organization
- **Automatic Project Files**: Generates appropriate project files (requirements.txt, package.json, pom.xml, etc.)
- **Fallback Conversion**: Basic conversion rules when AI is not available
- **Team Collaboration**: Basic project sharing, comments, and approval workflows
- **Git Integration**: Version control integration for conversion workflows

## 🛠️ Installation

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd codetranseval-benchmark
   
   # Create virtual environment
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Setup Gemma 3n (Optional but Recommended)**
   ```bash
   # Install AI dependencies
   pip install torch transformers accelerate kaggle
   
   # Setup Kaggle API (if using Kaggle-hosted models)
   mkdir ~/.kaggle
   # Download kaggle.json from https://www.kaggle.com/settings/account
   # Place it in ~/.kaggle/kaggle.json
   chmod 600 ~/.kaggle/kaggle.json
   
   # Accept Gemma 3n terms
   # Visit: https://www.kaggle.com/models/google/gemma-3n
   # Click "Accept" to agree to terms
   ```

3. **Run the Converter**
   ```bash
   # Simple way
   python run.py
   
   # Or traditional way
   python start_web_interface.py
   ```

4. **Access the Web Interface**
   - Open: http://localhost:5000 (opens automatically)
   - Upload your project ZIP file
   - Choose conversion type
   - Enable AI conversion (if setup)
   - Download converted project

## 📁 Supported Conversions

| Source Language | Target Language | Status |
|----------------|----------------|---------|
| C              | Python         | ✅ Stable |
| Python         | JavaScript     | ✅ Stable |
| Python         | Java           | ✅ Stable |
| Java           | Python         | ✅ New |
| JavaScript     | Python         | ✅ New |
| TypeScript     | Python         | ✅ New |
| Java           | JavaScript     | ✅ New |
| JavaScript     | Java           | ✅ New |

## 🎯 Usage Examples

### Web Interface
1. **Upload Project**: Drag and drop or select a ZIP file containing your project
2. **Choose Conversion**: Select the target language (C→Python, Python→JS, Python→Java)
3. **Convert**: Click convert and wait for processing
4. **Download**: Download the converted project as a ZIP file

### Programmatic Usage
```python
from enhanced_code_converter import EnhancedCodeConverter

# Initialize converter with AI support
converter = EnhancedCodeConverter(use_ai=True, model_name="gemma-3n-2b")

# Convert a project
results = converter.convert_project(
    source_dir="path/to/source/project",
    target_dir="path/to/output",
    conversion_type="c_to_python"
)

print(f"Files converted: {len(results['files_converted'])}")
print(f"AI used: {results['ai_used']}")
```

### AI Configuration
```python
# Use intelligent model selection (recommended)
converter = EnhancedCodeConverter(use_ai=True, auto_select_model=True)

# Use specific model
converter = EnhancedCodeConverter(use_ai=True, model_name="claude-3-sonnet")

# Use Kaggle-hosted models
converter = EnhancedCodeConverter(use_ai=True, use_kaggle=True)

# Disable AI (basic conversion only)
converter = EnhancedCodeConverter(use_ai=False)
```

### Team Collaboration
```python
from team_collaboration import get_team_collaboration

# Get team collaboration instance
team = get_team_collaboration()

# Create a user
user_id = team.create_user("john_doe", "john@example.com")

# Create a project
project_id = team.create_project(
    "My Conversion", "Converting Python to Java", 
    user_id, "python_to_java", "Python", "Java"
)

# Add comments
comment_id = team.add_comment(project_id, user_id, "main.py", "Great conversion!")

# Share project
team.share_project(project_id, "other_user_id")
```

### Git Integration
```python
from git_integration import get_git_integration

# Get Git integration instance
git = get_git_integration()

# Initialize repository
git.initialize_repository("./my_project")

# Create conversion workflow
git.create_conversion_workflow("./my_project", "python_to_java")

# Stage and commit changes
git.stage_conversion_changes("./my_project", "python_to_java")
```

## 📦 Sample Projects

The converter includes sample projects for testing:
- **C Project**: `sample_c_project.zip` (contains main.c, utils.c, utils.h)
- **Python Project**: Available in `sample_projects/python_project/`

## 🔧 Configuration

### Environment Variables
```bash
export FLASK_SECRET_KEY="your-secret-key"
export DATABASE_URL="sqlite:///instance/codetranseval.db"
```

### Supported File Extensions
- **C Projects**: `.c`, `.h`
- **Python Projects**: `.py`
- **JavaScript Projects**: `.js`
- **Java Projects**: `.java`

## 📊 Project Structure

```
templates/         # Web interface templates
static/           # Static web assets
sample_projects/  # Sample projects for testing
instance/         # Database and instance data
converted/        # Output directory (created automatically)
uploads/          # Temporary upload directory (created automatically)
```

## 🚀 API Endpoints

- **GET** `/` - Main web interface
- **POST** `/upload` - Upload and convert projects
- **GET** `/download/<session_id>` - Download converted projects
- **GET** `/results/<session_id>` - View conversion results
- **POST** `/api/convert` - Programmatic conversion API
- **GET** `/health` - Health check

## 📋 Next Steps Guidance

The converter automatically provides comprehensive guidance for what to do after conversion:

### What to do now:
1. **Download the converted project** - Get your converted code as a ZIP file
2. **Review the converted code** - Check for syntax errors and logic preservation
3. **Test the converted project** - Run with sample inputs and compare outputs
4. **Make manual adjustments if needed** - Fine-tune language-specific optimizations

### Important notes:
- **This is an automated conversion** - Always review the output
- **Manual review is recommended** - Check for edge cases and language-specific issues
- **Test thoroughly before production use** - Verify functionality and performance
- **Check for security implications** - Review input validation and data handling

### Detailed Guidance

#### How to Review Converted Code:
- Check for syntax errors in the target language
- Verify that all functions and logic are preserved
- Review variable names and data types
- Ensure proper error handling and exceptions
- Check for language-specific best practices

#### How to Test Converted Project:
- Run the converted code with sample inputs
- Compare output with the original program
- Test edge cases and error conditions
- Check for memory leaks or performance issues
- Verify all dependencies are properly included

#### Security Considerations:
- Review input validation and sanitization
- Check for potential injection vulnerabilities
- Verify secure handling of sensitive data
- Ensure proper authentication and authorization
- Review file and network access permissions

### Conversion-Specific Notes

The guidance adapts based on your conversion type:

- **C to Python**: Memory management, C-specific optimizations, struct conversions
- **Python to JavaScript**: Library equivalents, list comprehensions, exception handling
- **Python to Java**: Dynamic vs static typing, stream conversions, exception handling

### Accessing Next Steps

- **Web Interface**: Available in the results page with expandable sections
- **API Response**: Included in the `next_steps` field of conversion results
- **Programmatic Access**: Use the `generate_next_steps_guidance()` function

## 🔍 How It Works

1. **File Analysis**: Scans the uploaded project for source files
2. **Language Detection**: Identifies source language and target conversion
3. **AI Model Selection**: Intelligently selects the best AI model for the conversion type and complexity
4. **Code Conversion**: Converts each file using AI or basic language-specific rules
5. **Project Generation**: Creates appropriate project files for target language
6. **Package Creation**: Bundles converted project into downloadable ZIP

## 🤖 AI Model Management

The converter includes an intelligent AI model selection system:

### Supported Models
- **Gemma 3n 2B**: Fast, cost-effective for simple conversions
- **Claude 3 Sonnet**: High quality for complex conversions
- **GPT-4**: Best quality for difficult conversions
- **CodeLlama 34B**: Good balance for general use

### Model Selection Criteria
- **Conversion Type**: Different models excel at different language pairs
- **Code Complexity**: Simple vs complex code requirements
- **Performance History**: Learning from past conversion success rates
- **Cost Constraints**: Budget-aware model selection
- **Speed Requirements**: Fast vs high-quality trade-offs

### Fallback System
- Automatic fallback to alternative models if primary model fails
- Performance tracking for continuous improvement
- Load balancing across available models

## 🛡️ Security

- **Sandboxed Execution**: Safe code processing environment
- **File Validation**: Checks file types and sizes
- **Temporary Storage**: Automatic cleanup of uploaded files
- **Input Sanitization**: Validates all user inputs

## 📈 Performance

- **Fast Processing**: Optimized for quick project conversion
- **Memory Efficient**: Minimal memory footprint
- **Concurrent Support**: Handles multiple users
- **Scalable**: Easy to deploy and scale

## 🤝 Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

- **Issues**: Report bugs and feature requests
- **Documentation**: Check the code comments for detailed usage
- **Examples**: Use the sample projects as reference

---

**Code Project Converter** - Simple, fast, and reliable code translation. 🚀 