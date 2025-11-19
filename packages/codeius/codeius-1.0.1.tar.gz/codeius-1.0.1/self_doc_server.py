"""
Self-Documenting Agent
Auto-update Markdown docs in your repo as code changes ("live" AUTHORS, CHANGELOG, README snippets)
"""
from flask import Flask, request, jsonify
import os
import re
import json
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

def update_authors(file_path, contributors):
    """Update the AUTHORS file with contributors"""
    try:
        with open(file_path, 'w') as f:
            f.write("# Project Contributors\n\n")
            f.write("This project wouldn't be possible without the contributions of:\n\n")
            for contributor in contributors:
                f.write(f"- {contributor}\n")
        return True
    except Exception as e:
        return str(e)

def update_changelog(file_path, changes):
    """Update the CHANGELOG file with recent changes"""
    try:
        # Read existing changelog if it exists
        existing_content = ""
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                existing_content = f.read()
        
        with open(file_path, 'w') as f:
            # Write header if this is a new file
            if not existing_content:
                f.write("# Changelog\n\n")
                f.write("All notable changes to this project will be documented in this file.\n\n")
            
            # Add new changes
            f.write(f"## [{datetime.now().strftime('%Y-%m-%d')}] - Auto-Generated Update\n\n")
            for change in changes:
                f.write(f"- {change}\n")
            
            # Add existing content after new changes
            f.write("\n")
            f.write(existing_content)
        
        return True
    except Exception as e:
        return str(e)

def update_readme_section(file_path, section_title, content):
    """Update a specific section in the README file"""
    try:
        # Read the existing file
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content_lines = f.readlines()
        else:
            content_lines = []
        
        # Find the section to update
        start_idx = -1
        end_idx = -1
        for i, line in enumerate(content_lines):
            if line.startswith(f"## {section_title}") or line.startswith(f"### {section_title}"):
                start_idx = i
                # Find the end of this section (next heading of same or higher level)
                for j in range(i+1, len(content_lines)):
                    next_line = content_lines[j]
                    if next_line.startswith("# "):
                        end_idx = j
                        break
                    elif next_line.startswith("## ") and start_idx >= 0:
                        end_idx = j
                        break
                    elif next_line.startswith("### ") and start_idx >= 0 and end_idx == -1:
                        if content_lines[i].startswith("## "):
                            end_idx = j
                            break
                if end_idx == -1:  # If no next section, go to end
                    end_idx = len(content_lines)
                break
        
        # Modify the content
        if start_idx != -1 and end_idx != -1:
            # Replace the section
            new_content = content_lines[:start_idx+1]
            new_content.append(f"\n{content}\n")
            new_content.extend(content_lines[end_idx:])
            content_lines = new_content
        else:
            # If section doesn't exist, add it at the end
            content_lines.append(f"\n## {section_title}\n")
            content_lines.append(f"\n{content}\n")
        
        # Write back to file
        with open(file_path, 'w') as f:
            f.writelines(content_lines)
        
        return True
    except Exception as e:
        return str(e)

@app.route('/update_docs', methods=['POST'])
def update_docs():
    """Update documentation based on code changes"""
    try:
        action = request.json.get('action', '')
        params = request.json.get('params', {})
        
        if action == 'update_authors':
            contributors = params.get('contributors', [])
            file_path = params.get('file_path', 'AUTHORS.md')
            success = update_authors(file_path, contributors)
            if success is True:
                return jsonify({'success': True, 'message': f'AUTHORS file updated at {file_path}'})
            else:
                return jsonify({'success': False, 'error': str(success)}), 500
        
        elif action == 'update_changelog':
            changes = params.get('changes', [])
            file_path = params.get('file_path', 'CHANGELOG.md')
            success = update_changelog(file_path, changes)
            if success is True:
                return jsonify({'success': True, 'message': f'CHANGELOG file updated at {file_path}'})
            else:
                return jsonify({'success': False, 'error': str(success)}), 500
        
        elif action == 'update_readme':
            section_title = params.get('section_title', '')
            content = params.get('content', '')
            file_path = params.get('file_path', 'README.md')
            success = update_readme_section(file_path, section_title, content)
            if success is True:
                return jsonify({'success': True, 'message': f'README section "{section_title}" updated at {file_path}'})
            else:
                return jsonify({'success': False, 'error': str(success)}), 500
        
        else:
            return jsonify({'error': f'Unknown action: {action}'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=10300)