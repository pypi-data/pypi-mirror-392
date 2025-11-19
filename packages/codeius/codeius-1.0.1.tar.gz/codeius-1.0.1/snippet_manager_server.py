"""
Snippet/Template Manager
Store, retrieve, and insert boilerplate snippets (local YAML/JSON/MD files). 
Handy for accelerating repetitive coding.
"""
from flask import Flask, request, jsonify
import os
import json
import yaml
from pathlib import Path

app = Flask(__name__)

class SnippetManager:
    def __init__(self, snippets_dir="snippets"):
        self.snippets_dir = Path(snippets_dir)
        self.snippets_dir.mkdir(exist_ok=True)
        self.snippet_files = {
            ".json": self.snippets_dir / "snippets.json",
            ".yaml": self.snippets_dir / "snippets.yaml",
            ".yml": self.snippets_dir / "snippets.yml"
        }
        
        # Initialize snippet files if they don't exist
        for ext, path in self.snippet_files.items():
            if not path.exists():
                if ext == ".json":
                    with open(path, 'w') as f:
                        json.dump({}, f, indent=2)
                elif ext in [".yaml", ".yml"]:
                    with open(path, 'w') as f:
                        yaml.dump({}, f)
    
    def save_snippet(self, key, content, description=""):
        """Save a snippet with the given key"""
        # First, load all existing snippets
        all_snippets = self.load_all_snippets()
        
        # Update or add the new snippet
        all_snippets[key] = {
            "content": content,
            "description": description,
            "last_updated": str(self.get_current_time())
        }
        
        # Save all snippets back to the JSON file
        with open(self.snippet_files[".json"], 'w') as f:
            json.dump(all_snippets, f, indent=2)
        
        return {"status": "success", "message": f"Snippet '{key}' saved successfully"}
    
    def get_snippet(self, key):
        """Retrieve a snippet by key"""
        all_snippets = self.load_all_snippets()
        
        if key in all_snippets:
            return all_snippets[key]["content"]
        else:
            return None
    
    def list_snippets(self):
        """List all available snippet keys"""
        all_snippets = self.load_all_snippets()
        return list(all_snippets.keys())
    
    def delete_snippet(self, key):
        """Delete a snippet by key"""
        all_snippets = self.load_all_snippets()
        
        if key in all_snippets:
            del all_snippets[key]
            with open(self.snippet_files[".json"], 'w') as f:
                json.dump(all_snippets, f, indent=2)
            return {"status": "success", "message": f"Snippet '{key}' deleted successfully"}
        else:
            return {"status": "error", "message": f"Snippet '{key}' not found"}
    
    def load_all_snippets(self):
        """Load snippets from all supported file formats"""
        # For now, we'll use just JSON as the primary format
        # In a more advanced version, we could merge snippets from all formats
        
        json_file = self.snippet_files[".json"]
        if json_file.exists():
            with open(json_file, 'r') as f:
                return json.load(f)
        else:
            return {}
    
    def get_current_time(self):
        """Get the current time as a string"""
        from datetime import datetime
        return datetime.now()

# Initialize the snippet manager
snippet_manager = SnippetManager()

@app.route('/snippet', methods=['POST'])
def snippet():
    """Handle snippet operations"""
    try:
        action = request.json.get('action', 'get')
        key = request.json.get('key', '')
        
        if action == 'get':
            content = snippet_manager.get_snippet(key)
            if content is not None:
                return jsonify({
                    'success': True,
                    'key': key,
                    'content': content
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'Snippet with key "{key}" not found'
                }), 404
        
        elif action == 'save':
            content = request.json.get('content', '')
            description = request.json.get('description', '')
            
            result = snippet_manager.save_snippet(key, content, description)
            if result["status"] == "success":
                return jsonify({
                    'success': True,
                    'message': result["message"]
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result["message"]
                }), 400
        
        elif action == 'delete':
            result = snippet_manager.delete_snippet(key)
            if result["status"] == "success":
                return jsonify({
                    'success': True,
                    'message': result["message"]
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result["message"]
                }), 400
        
        elif action == 'list':
            keys = snippet_manager.list_snippets()
            return jsonify({
                'success': True,
                'snippets': keys
            })
        
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown action: {action}'
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(port=10500)