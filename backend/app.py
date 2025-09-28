from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication
CORS(app, resources={r"/api/*": {"origins": [ "https://psi-vibe-coder.onrender.com"]}}# # replace with your actual Render frontend URL ]}})

def run_python_code(code: str):
    url = "https://emkc.org/api/v2/piston/execute"
    payload = {
        "language": "python3",
        "version": "3.10.0",
        "files": [
            {"name": "main.py", "content": code}
        ]
    }
    response = requests.post(url, json=payload)
    result = response.json()
    return result["run"]["stdout"], result["run"]["stderr"]

# POST /api/run-code
@app.route('/api/run-code', methods=['POST'])
def run_code():
    try:
        data = request.get_json()
        code = data.get('code', '')
        
        if not code:
            return jsonify({
                'success': False,
                'error': 'No code provided',
                'results': 'Error: No code provided'
            }), 400
        
        # Execute the code using your existing function
        stdout, stderr = run_python_code(code)
        
        # Combine stdout and stderr for display
        if stderr:
            results = f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
        else:
            results = stdout if stdout else "Code executed successfully (no output)"
        
        return jsonify({
            'success': True,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'results': f'Error: {str(e)}'
        }), 500

