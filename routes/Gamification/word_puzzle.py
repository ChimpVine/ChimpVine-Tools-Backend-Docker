# routes/Gamification/word_puzzle.py

from flask import Blueprint, request, jsonify
import json
from utils.Gamification.Word_puzzle import Word_puzzle
from wordpress_api.token_verification import verify_token, use_token
from validation.input_validation import validate_string
from validation.load_tools import get_tool_by_name, load_tools_from_json

word_puzzle_bp = Blueprint("word_puzzle", __name__)

tools = load_tools_from_json("Tools.json")

@word_puzzle_bp.route('/word_puzzle', methods=['POST'])
def word_puzzle_api():
    """API endpoint to generate a word puzzle."""
    try:
        # Extract headers
        auth_token = request.headers.get('Authorization')
        site_url = request.headers.get('X-Site-Url')

        if not auth_token or not site_url:
            return jsonify({"error": "Missing headers"}), 400

        # Extract data
        data = request.get_json() or request.form
        topic = data.get('topic')
        numberofword = data.get('numberofword')
        difficulty_level = data.get('difficulty_level')

        # Validate required fields
        if not all([topic, numberofword, difficulty_level]):
            return jsonify({"error": "Missing required fields"}), 400

        # Validate topic
        valid, error = validate_string(topic, "Topic", 3, 50)
        if not valid:
            return jsonify({"error": error}), 400

        # Convert and validate number of words
        try:
            numberofword = int(numberofword)
            if numberofword < 1 or numberofword > 50:
                raise ValueError
        except ValueError:
            return jsonify({"error": "Number of words must be an integer between 1 and 50"}), 400

        # Load and verify tool
        tool = get_tool_by_name(tools, "Word Puzzle")
        if not tool:
            return jsonify({"error": "Tool not found"}), 500

        Tool_ID, Token = tool["Tool_ID"], tool["Token"]

        # Verify token
        token_verification = verify_token(auth_token, site_url, Tool_ID, Token)
        if token_verification.get("status") != "success":
            return jsonify({"error": token_verification.get("message")}), token_verification.get("code", 400)

        # Generate word puzzle
        result = Word_puzzle(topic, numberofword, difficulty_level)
                    
        # Ensure proper JSON format
        if isinstance(result, str):
            result = json.loads(result)

        if isinstance(result, dict) and 'error' in result:
            return jsonify(result), 400

        # Use token after successful response
        use_token(auth_token, site_url, Tool_ID, Token)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500