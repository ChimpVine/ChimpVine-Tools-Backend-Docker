# routes/Gamification/make_the_word.py

from flask import Blueprint, request, jsonify
import json
from utils.Gamification.make_the_word import generate_make_the_word
from wordpress_api.token_verification import verify_token, use_token
from validation.input_validation import validate_string
from validation.load_tools import get_tool_by_name, load_tools_from_json

make_the_word_bp = Blueprint("make_the_word", __name__)

tools = load_tools_from_json("Tools.json")

@make_the_word_bp.route('/make_the_word', methods=['POST'])
def make_the_word_api():
    """API endpoint to generate 'Make the Word' game."""
    try:
        # Extract headers
        auth_token = request.headers.get('Authorization')
        site_url = request.headers.get('X-Site-Url')

        if not auth_token or not site_url:
            return jsonify({"error": "Missing headers"}), 400

        # Extract data
        data = request.get_json()
        theme = data.get('theme')
        difficulty_level = data.get('difficulty_level')
        number_of_words = data.get('number_of_words')

        # Validate required fields
        if not all([theme, difficulty_level, number_of_words]):
            return jsonify({"error": "Missing required field(s)"}), 400

        # Validate theme
        valid, error = validate_string(theme, "Theme", 3, 50)
        if not valid:
            return jsonify({"error": error}), 400

        # Convert and validate number of words
        try:
            number_of_words = int(number_of_words)
            if number_of_words < 1 or number_of_words > 50:
                raise ValueError
        except ValueError:
            return jsonify({"error": "Number of words must be an integer between 1 and 50"}), 400

        # Load and verify tool
        tool = get_tool_by_name(tools, "Make the Word")
        if not tool:
            return jsonify({"error": "Tool not found"}), 500

        Tool_ID, Token = tool["Tool_ID"], tool["Token"]

        # Verify token
        token_verification = verify_token(auth_token, site_url, Tool_ID, Token)
        if token_verification.get("status") != "success":
            return jsonify({"error": token_verification.get("message")}), token_verification.get("code", 400)

        # Generate Make the Word game
        response = generate_make_the_word(theme, difficulty_level, number_of_words)

        # Clean and parse response if needed
        if isinstance(response, str):
            response = response.replace("```", "").replace("json", "").replace("\n", "").replace("\\", "")
            response = json.loads(response)

        if response is None:
            return jsonify({"error": "Failed to generate make the word game"}), 500

        if isinstance(response, dict) and 'error' in response:
            # Remove any partial data if error occurred
            response.pop('letters', None)
            response.pop('words', None)
            return jsonify(response), 400
        
        # Ensure proper JSON format
        if isinstance(response, str):
            response = json.loads(response)

        # Use token after successful response
        use_token(auth_token, site_url, Tool_ID, Token)

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500