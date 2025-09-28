from flask import Flask, request, jsonify
import requests
import os
import subprocess
import json
import re
from datetime import datetime
from flask_cors import CORS
from github import Github
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# ✅ Allow only your frontend domain
CORS(app, resources={r"/*": {"origins": "https://psi-vibe-coder.onrender.com"}}, supports_credentials=True)

# ✅ Ensure preflight OPTIONS requests work
@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response

# ---------- CONFIGURATION ----------
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
USERNAME = "Goodn6138"
LOCAL_PATH = "/tmp/my_project"

# Initialize OpenRouter Client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def extract_repo_name_from_description(description: str) -> str:
    """Extract repo name from description if specified, otherwise generate one"""
    if not description:
        return generate_repo_name("auto-generated-project")
    
    patterns = [
        r'repo\s*name:\s*["\']?([^"\'\s\.]+)["\']?',
        r'repository:\s*["\']?([^"\'\s\.]+)["\']?',
        r'project:\s*["\']?([^"\'\s\.]+)["\']?',
        r'name:\s*["\']?([^"\'\s\.]+)["\']?',
        r'call\s+it\s+["\']?([^"\'\s\.]+)["\']?',
    ]

    for pattern in patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            repo_name = match.group(1).lower().replace('_', '-')
            repo_name = re.sub(r'[^a-z0-9\-]', '', repo_name)
            if repo_name and len(repo_name) >= 3:
                return repo_name

    return generate_repo_name(description)

def generate_repo_name(description: str) -> str:
    """Generate a unique repo name from description"""
    words = re.findall(r'\b[a-z]{3,15}\b', description.lower())
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    filtered_words = [w for w in words if w not in stop_words]

    if filtered_words:
        key_words = filtered_words[:3]
        base_name = '-'.join(key_words)
    else:
        base_name = re.sub(r'[^a-z0-9]', '-', description.lower()[:15]).strip('-')

    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    return f"{base_name}-{timestamp}"

def generate_repo_structure(code_snippet: str, extra_description: str = ""):
    """Ask OpenRouter to generate a repo structure"""
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b:cerebras",
        messages=[{
            "role": "user",
            "content": f"""Generate a full GitHub repo as JSON.

Inputs:
- Code snippet:
{code_snippet}

- Additional description / requirements:
{extra_description}

Rules:
- Return ONLY valid JSON.
- JSON format: {{ "files": [ {{ "path": "filename.ext", "content": "file content" }} ] }}.
- Must include:
   1. index.html (basic frontend).
   2. app.py (Flask backend).
   3. requirements.txt (at least flask).
   4. README.md (must summarize everything, including the extra description).
- Integrate the provided code snippet inside the appropriate file.
- You MUST also follow any additional instructions provided in the description above.
"""
        }],
        max_tokens=2500
    )
    return completion.choices[0].message.content.strip()

def create_repo(description: str, repo_name: str = "colab-generated-repo"):
    """Create GitHub repo"""
    g = Github(GITHUB_TOKEN)
    user = g.get_user()
    repo_name = sanitize_repo_name(repo_name)

    try:
        user.get_repo(repo_name)
        import random
        repo_name = f"{repo_name}-{random.randint(1000, 9999)}"
    except:
        pass

    repo = user.create_repo(repo_name, description=description, private=False)
    return repo.clone_url, repo_name

def sanitize_repo_name(name: str) -> str:
    """Sanitize repo name to meet GitHub requirements"""
    name = re.sub(r'[^a-zA-Z0-9._-]', '-', name)
    name = name.strip('.-_')
    name = name.lower()
    return name[:100]

def write_files_from_json(json_str: str):
    """Parse JSON and write files locally"""
    os.makedirs(LOCAL_PATH, exist_ok=True)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"Raw response: {json_str}")
        raise

    for file in data["files"]:
        file_path = os.path.join(LOCAL_PATH, file["path"])
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file["content"])
        print(f"📁 Created: {file_path}")

def upload_files(repo_url):
    """Push local files to GitHub"""
    original_dir = os.getcwd()

    try:
        os.chdir(LOCAL_PATH)

        if not os.path.exists(".git"):
            subprocess.run(["git", "init"], check=True)

        subprocess.run(["git", "config", "--global", "user.email", "colab@example.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "Colab Bot"], check=True)

        result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True)
        if result.returncode == 0:
            subprocess.run(["git", "remote", "remove", "origin"], check=True)

        auth_repo_url = repo_url.replace("https://", f"https://{GITHUB_TOKEN}@")
        subprocess.run(["git", "remote", "add", "origin", auth_repo_url], check=True)

        subprocess.run(["git", "add", "."], check=True)

        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        if result.stdout.strip():
            subprocess.run(["git", "commit", "-m", "Initial commit from Colab"], check=True)
            subprocess.run(["git", "branch", "-M", "main"], check=True)
            subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
            print("✅ Successfully pushed to GitHub")
        else:
            print("⚠️ No changes to commit")

    finally:
        os.chdir(original_dir)

def create_project_repo(code_snippet: str, extra_description: str = "", repo_name: str = None):
    """Pipeline: generate repo → write files → push to GitHub"""
    try:
        if repo_name is None:
            repo_name = extract_repo_name_from_description(extra_description)
        else:
            repo_name = sanitize_repo_name(repo_name)

        print("⚡ Generating repo structure with OpenRouter...")
        repo_json = generate_repo_structure(code_snippet, extra_description)

        print("⚡ Writing files locally...")
        write_files_from_json(repo_json)

        print("⚡ Creating GitHub repo...")
        repo_url, final_repo_name = create_repo(extra_description or "Auto-generated repo from code snippet", repo_name)

        print("⚡ Uploading files to GitHub...")
        upload_files(repo_url)

        print(f"🚀 Done! Repo pushed: {repo_url}")
        return {"success": True, "repo_url": repo_url, "repo_name": final_repo_name}

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}

def run_python_code(code: str):
    """Send Python code to Piston API and return stdout/stderr."""
    url = "https://emkc.org/api/v2/piston/execute"
    payload = {
        "language": "python3",
        "version": "3.10.0",
        "files": [{"name": "main.py", "content": code}],
    }
    response = requests.post(url, json=payload)
    result = response.json()
    return result["run"]["stdout"], result["run"]["stderr"]

# ✅ This endpoint matches your frontend expectation
@app.route("/run-code", methods=["POST"])
def run_code():
    try:
        data = request.get_json()
        code = data.get("code", "")

        if not code:
            return jsonify({
                "success": False,
                "error": "No code provided",
                "results": "Error: No code provided",
            }), 400

        stdout, stderr = run_python_code(code)

        if stderr:
            results = f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
        else:
            results = stdout if stdout else "Code executed successfully (no output)"

        return jsonify({
            "success": True, 
            "results": results, 
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "results": f"Error: {str(e)}",
        }), 500

# ✅ NEW: This endpoint matches your frontend's "Generate Code with GPT" button
@app.route("/generate-code", methods=["POST"])
def generate_code():
    """Generate code based on description and create GitHub repo"""
    try:
        data = request.get_json()
        description = data.get("description", "")
        
        if not description:
            return jsonify({
                "success": False,
                "error": "No description provided"
            }), 400

        # Generate a simple code snippet based on description
        prompt = f"Generate a Python code snippet for: {description}. Return only the code without explanations."
        
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b:cerebras",
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=500
        )
        
        generated_code = completion.choices[0].message.content.strip()
        
        # Create GitHub repo with the generated code
        repo_result = create_project_repo(generated_code, description)
        
        if repo_result["success"]:
            # Format folder structure for display
            folder_structure = f"""
📁 {repo_result['repo_name']}
├── 📄 index.html (Frontend)
├── 📄 app.py (Flask Backend)
├── 📄 requirements.txt
└── 📄 README.md

🔗 Repository: {repo_result['repo_url']}
            """.strip()
            
            return jsonify({
                "success": True,
                "generatedCode": generated_code,
                "folderStructure": folder_structure,
                "renderUrl": repo_result["repo_url"].replace(".git", ""),  # GitHub URL instead of Render
                "repoUrl": repo_result["repo_url"]
            })
        else:
            return jsonify({
                "success": False,
                "error": repo_result.get("error", "Failed to create repository")
            }), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ✅ NEW: Endpoint to create repo from existing code
@app.route("/create-repo", methods=["POST"])
def create_repo_endpoint():
    """Create GitHub repository from existing code"""
    try:
        data = request.get_json()
        code = data.get("code", "")
        description = data.get("description", "")
        repo_name = data.get("repo_name", "")

        if not code:
            return jsonify({
                "success": False,
                "error": "No code provided"
            }), 400

        repo_name_param = repo_name if repo_name else None
        result = create_project_repo(code, description, repo_name_param)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "repo_url": result["repo_url"],
                "repo_name": result["repo_name"],
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Unknown error occurred")
            }), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Flask Backend with GitHub Integration"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
