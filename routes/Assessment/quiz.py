from flask import Blueprint, request, jsonify
import json
import time
from utils.Assessment.quiz import quiz_generator
from wordpress_api.token_verification import verify_token, use_token
from validation.input_validation import validate_string
from validation.load_tools import get_tool_by_name, load_tools_from_json

quiz_bp = Blueprint("quiz", __name__)

tools = load_tools_from_json("Tools.json")

@quiz_bp.route('/generate_quiz', methods=['POST', 'GET'])
def generate_quiz():
    """API endpoint to generate a quiz."""
    try:
        # Extract headers
        auth_token = request.headers.get('Authorization')
        site_url = request.headers.get('X-Site-Url')

        if not auth_token or not site_url:
            return jsonify({"error": "Missing headers"}), 400

        # Extract data based on request method
        if request.method == 'POST':
            data = request.form or request.json
        else:
            data = request.args

        topic = data.get('topic')
        language = data.get('language')
        subject = data.get('subject')
        number = data.get('number')
        difficulty = data.get('difficulty')

        # Validate required fields
        if not all([topic, language, subject, number, difficulty]):
            return jsonify({"error": "Missing required fields"}), 400

        # Validate topic and subject
        valid, error = validate_string(topic, "Topic", 3, 50)
        if not valid:
            return jsonify({"error": error}), 400
            
        valid, error = validate_string(subject, "Subject", 3, 50)
        if not valid:
            return jsonify({"error": error}), 400

        # Convert and validate number of questions
        try:
            number = int(number)
            if number < 1 or number > 50:
                raise ValueError
        except ValueError:
            return jsonify({"error": "Number of questions must be an integer between 1 and 50"}), 400

        # Load and verify tool
        tool = get_tool_by_name(tools, "Quiz")
        if not tool:
            return jsonify({"error": "Tool not found"}), 500

        Tool_ID, Token = tool["Tool_ID"], tool["Token"]

        # Verify token
        token_verification = verify_token(auth_token, site_url, Tool_ID, Token)
        if token_verification.get("status") != "success":
            return jsonify({"error": token_verification.get("message")}), token_verification.get("code", 400)

        # Generate quiz
        start_time = time.time()
        quiz = quiz_generator(topic, language, subject, number, difficulty)
        print(f"Quiz generation time: {time.time() - start_time} seconds")
                    
        # Ensure proper JSON format
        if isinstance(quiz, str):
            quiz = json.loads(quiz)

        if isinstance(quiz, dict) and 'error' in quiz:
            return jsonify(quiz), 400

        # Use token after successful response
        use_token(auth_token, site_url, Tool_ID, Token)

        return jsonify(quiz), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500