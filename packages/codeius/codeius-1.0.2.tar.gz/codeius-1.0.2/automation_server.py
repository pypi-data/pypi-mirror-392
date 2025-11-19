"""
Script/Form Automation Tool
Automates repetitive coding chores: batch rename variables, auto-generate project scaffolds, manage environment files with templates
"""
from flask import Flask, request, jsonify
import os
import shutil
import tempfile
from pathlib import Path

app = Flask(__name__)

@app.route('/scaffold', methods=['POST'])
def scaffold():
    """Generate project scaffolding based on templates"""
    try:
        template = request.json.get('template', 'basic')
        project_name = request.json.get('project_name', 'new_project')
        options = request.json.get('options', {})
        
        # Create project directory
        project_path = os.path.join(os.getcwd(), project_name)
        os.makedirs(project_path, exist_ok=True)
        
        # Generate basic project structure based on template
        if template == 'python':
            # Create basic Python project structure
            os.makedirs(os.path.join(project_path, 'src'), exist_ok=True)
            os.makedirs(os.path.join(project_path, 'tests'), exist_ok=True)
            os.makedirs(os.path.join(project_path, 'docs'), exist_ok=True)
            
            # Create basic files
            with open(os.path.join(project_path, 'README.md'), 'w') as f:
                f.write(f"# {project_name}\n\nYour new Python project.")
            
            with open(os.path.join(project_path, 'requirements.txt'), 'w') as f:
                f.write("# Add your dependencies here\n")
            
            with open(os.path.join(project_path, 'src', '__init__.py'), 'w') as f:
                f.write("# Project initialization\n")
            
            with open(os.path.join(project_path, '.gitignore'), 'w') as f:
                f.write("*.pyc\n__pycache__/\n.env\nvenv/\n")
        
        elif template == 'web':
            # Create basic web project structure
            os.makedirs(os.path.join(project_path, 'static'), exist_ok=True)
            os.makedirs(os.path.join(project_path, 'templates'), exist_ok=True)
            
            # Create basic files
            with open(os.path.join(project_path, 'index.html'), 'w') as f:
                f.write("<!DOCTYPE html>\n<html>\n<head>\n    <title>New Project</title>\n</head>\n<body>\n    <h1>Welcome</h1>\n</body>\n</html>")
            
            os.makedirs(os.path.join(project_path, 'static', 'css'), exist_ok=True)
            os.makedirs(os.path.join(project_path, 'static', 'js'), exist_ok=True)
            os.makedirs(os.path.join(project_path, 'static', 'img'), exist_ok=True)
        
        else:  # basic template
            # Create basic directory structure
            os.makedirs(os.path.join(project_path, 'src'), exist_ok=True)
            os.makedirs(os.path.join(project_path, 'docs'), exist_ok=True)
            
            # Create basic files
            with open(os.path.join(project_path, 'README.md'), 'w') as f:
                f.write(f"# {project_name}\n\nYour new project.")
        
        return jsonify({
            'success': True,
            'message': f'Project {project_name} created successfully',
            'path': project_path,
            'template': template
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/env', methods=['POST'])
def env():
    """Manage environment files with templates"""
    try:
        action = request.json.get('action', 'create')
        template = request.json.get('template', 'default')
        output_file = request.json.get('output_file', '.env')
        variables = request.json.get('variables', {})
        
        if action == 'create':
            # Create a new environment file
            with open(output_file, 'w') as f:
                f.write("# Environment variables\n")
                for key, value in variables.items():
                    f.write(f"{key}={value}\n")
            
            return jsonify({
                'success': True,
                'message': f'Environment file {output_file} created successfully',
                'path': os.path.abspath(output_file)
            })
        
        elif action == 'update':
            # Update an existing environment file
            if os.path.exists(output_file):
                # Read existing content to preserve other variables
                existing_vars = {}
                with open(output_file, 'r') as f:
                    for line in f:
                        if '=' in line and not line.strip().startswith('#'):
                            key, value = line.split('=', 1)
                            existing_vars[key.strip()] = value.strip()
                
                # Update with new variables
                existing_vars.update(variables)
                
                # Write back to file
                with open(output_file, 'w') as f:
                    f.write("# Environment variables\n")
                    for key, value in existing_vars.items():
                        f.write(f"{key}={value}\n")
                
                return jsonify({
                    'success': True,
                    'message': f'Environment file {output_file} updated successfully',
                    'path': os.path.abspath(output_file)
                })
            else:
                return jsonify({'error': f'Environment file {output_file} does not exist'}), 400
        else:
            return jsonify({'error': 'Invalid action. Use "create" or "update"'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/rename', methods=['POST'])
def rename():
    """Batch rename variables in files"""
    try:
        file_path = request.json.get('file_path', '')
        old_name = request.json.get('old_name', '')
        new_name = request.json.get('new_name', '')
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File does not exist'}), 400
        
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the old name with new name (simple replacement)
        # In a more sophisticated implementation, you would use AST parsing for accuracy
        import re
        # Use word boundaries to avoid partial matches
        new_content = re.sub(r'\b' + re.escape(old_name) + r'\b', new_name, content)
        
        # Write the updated content back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return jsonify({
            'success': True,
            'message': f'Variable renamed from {old_name} to {new_name} in {file_path}',
            'replacements': content.count(old_name)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=10100)