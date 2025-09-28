from flask import Flask, request, jsonify
import requests
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)

# ✅ Allow only your frontend domain
CORS(app, resources={r"/*": {"origins": "https://psi-vibe-coder.onrender.com"}}, supports_credentials=True)

# ✅ Ensure preflight OPTIONS requests work
@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response


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


@app.route("/run-code", methods=["POST"])
def run_code():
    try:
        data = request.get_json()
        code = data.get("code", "")

        if not code:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "No code provided",
                        "results": "Error: No code provided",
                    }
                ),
                400,
            )

        # Execute the code
        stdout, stderr = run_python_code(code)

        # Format results
        if stderr:
            results = f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
        else:
            results = stdout if stdout else "Code executed successfully (no output)"

        return jsonify(
            {"success": True, "results": results, "timestamp": datetime.now().isoformat()}
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "results": f"Error: {str(e)}",
                }
            ),
            500,
        )


if __name__ == "__main__":
    # Useful for local testing
    app.run(host="0.0.0.0", port=5000, debug=True)
from flask import Flask, request, jsonify
import requests
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)

# ✅ Allow only your frontend domain
CORS(app, resources={r"/*": {"origins": "https://psi-vibe-coder.onrender.com"}}, supports_credentials=True)

# ✅ Ensure preflight OPTIONS requests work
@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response


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


@app.route("/run-code", methods=["POST"])
def run_code():
    try:
        data = request.get_json()
        code = data.get("code", "")

        if not code:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "No code provided",
                        "results": "Error: No code provided",
                    }
                ),
                400,
            )

        # Execute the code
        stdout, stderr = run_python_code(code)

        # Format results
        if stderr:
            results = f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
        else:
            results = stdout if stdout else "Code executed successfully (no output)"

        return jsonify(
            {"success": True, "results": results, "timestamp": datetime.now().isoformat()}
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "results": f"Error: {str(e)}",
                }
            ),
            500,
        )


if __name__ == "__main__":
    # Useful for local testing
    app.run(host="0.0.0.0", port=5000, debug=True)
