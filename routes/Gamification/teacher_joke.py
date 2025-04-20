from flask import Blueprint, request, jsonify
from utils.Gamification.teacher_joke import generate_joke
from wordpress_api.token_verification import verify_token, use_token
from validation.input_validation import validate_string
from validation.load_tools import get_tool_by_name, load_tools_from_json
import json

teacher_joke_bp = Blueprint("teacher_joke", __name__)

tools = load_tools_from_json("Tools.json")

@teacher_joke_bp.route('/teacher_joke', methods=['POST'])
def teacher_joke_api():
    """API endpoint to generate teacher jokes."""
    try:
        # Extract headers
        auth_token = request.headers.get('Authorization')
        site_url = request.headers.get('X-Site-Url')

        if not auth_token or not site_url:
            return jsonify({"error": "Missing headers"}), 400

        # Extract data
        data = request.get_json() or request.form
        topic = data.get('topic')
        number_of_jokes = data.get('number_of_jokes')

        # Validate required fields
        if not all([topic, number_of_jokes]):
            return jsonify({"error": "Missing required fields: topic, number of jokes"}), 400

        # Validate topic
        valid, error = validate_string(topic, "Topic", 3, 50)
        if not valid:
            return jsonify({"error": error}), 400

        # Convert and validate number of jokes
        try:
            number_of_jokes = int(number_of_jokes)
            if number_of_jokes < 1 or number_of_jokes > 50:
                raise ValueError
        except ValueError:
            return jsonify({"error": "Number of jokes must be an integer between 1 and 50"}), 400

        # Load and verify tool
        tool = get_tool_by_name(tools, "Teacher joke")
        if not tool:
            return jsonify({"error": "Tool not found"}), 500

        Tool_ID, Token = tool["Tool_ID"], tool["Token"]

        # Verify token
        token_verification = verify_token(auth_token, site_url, Tool_ID, Token)
        if token_verification.get("status") != "success":
            return jsonify({"error": token_verification.get("message")}), token_verification.get("code", 400)

        # Generate jokes
        response = generate_joke(topic, number_of_jokes)

        if response is None:
            return jsonify({"error": "Failed to generate Teacher joke"}), 500
        
        # Ensure proper JSON format
        if isinstance(response, str):
            result = json.loads(response)

        if isinstance(response, dict) and 'error' in response:
            return jsonify(response), 400

        # Use token after successful response
        use_token(auth_token, site_url, Tool_ID, Token)

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500