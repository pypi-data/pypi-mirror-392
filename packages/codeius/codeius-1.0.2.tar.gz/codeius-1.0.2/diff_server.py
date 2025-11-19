"""
File/Directory Diff Tool
Compare content of two files or directories using Python's difflib
"""
from flask import Flask, request, jsonify
import difflib
import os
import filecmp

app = Flask(__name__)

def get_file_content(filepath):
    """Read and return content of a file safely"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read().splitlines()
    except Exception:
        return []

def compare_files(file1, file2):
    """Compare two files and return the differences"""
    content1 = get_file_content(file1)
    content2 = get_file_content(file2)
    
    diff = list(difflib.unified_diff(
        content1,
        content2,
        fromfile=file1,
        tofile=file2,
        lineterm=''
    ))
    
    return {
        'type': 'file',
        'same': content1 == content2,
        'diff': diff
    }

def compare_directories(dir1, dir2):
    """Compare two directories and return the differences"""
    comparison = filecmp.dircmp(dir1, dir2)
    
    result = {
        'type': 'directory',
        'same': comparison.diff_files == [],
        'diff_files': comparison.diff_files,
        'only_in_first': comparison.left_only,
        'only_in_second': comparison.right_only
    }
    
    # Also show file-level diffs for differing files
    if result['diff_files']:
        result['file_diffs'] = {}
        for filename in result['diff_files']:
            file1 = os.path.join(dir1, filename)
            file2 = os.path.join(dir2, filename)
            content1 = get_file_content(file1)
            content2 = get_file_content(file2)
            
            diff = list(difflib.unified_diff(
                content1,
                content2,
                fromfile=file1,
                tofile=file2,
                lineterm=''
            ))
            result['file_diffs'][filename] = diff
    
    return result

@app.route('/diff', methods=['POST'])
def diff():
    file1 = request.json.get('file1', '')
    file2 = request.json.get('file2', '')
    
    if not file1 or not file2:
        return jsonify({'error': 'Both file paths are required'}), 400
    
    # Check if paths exist
    if not os.path.exists(file1) or not os.path.exists(file2):
        return jsonify({'error': 'One or both files/directories do not exist'}), 400
    
    try:
        # Determine if comparing files or directories
        if os.path.isfile(file1) and os.path.isfile(file2):
            result = compare_files(file1, file2)
        elif os.path.isdir(file1) and os.path.isdir(file2):
            result = compare_directories(file1, file2)
        else:
            return jsonify({'error': 'Both paths must be of the same type (file or directory)'}), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=10000)