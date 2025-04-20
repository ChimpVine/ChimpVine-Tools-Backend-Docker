from flask import Blueprint, request, jsonify
import json
from utils.Gamification.bingo import generate_bingo
from wordpress_api.token_verification import verify_token, use_token
from validation.input_validation import validate_string
from validation.load_tools import get_tool_by_name, load_tools_from_json

bingo_bp = Blueprint("bingo", __name__)

tools = load_tools_from_json("Tools.json")

@bingo_bp.route('/generate_bingo', methods=['POST'])
def generate_bingo_cards():
    data = request.get_json()
    # Extract headers
    auth_token = request.headers.get('Authorization')
    site_url = request.headers.get('X-Site-Url')
    print(site_url, auth_token)

    # Check if the required headers are present
    if not auth_token:
        return jsonify({'error': "Missing 'Authorization' header"}), 400
    if not site_url:
        return jsonify({'error': "Missing 'X-Site-Url' header"}), 400

    topic = data.get("topic")
    num_students = data.get("num_students")

    print(topic,num_students)
    # Validate the topic
    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    
    # Validate 'theme' field
    valid, error = validate_string(topic, "Topic", min_length=3, max_length=50)
    if not valid:
        return jsonify({"error": error}), 400

    # Validate the number of students
    try:
        num_students = int(num_students)
        if num_students < 1 and num_students < 20:
            return jsonify({"error": "Number of students must be at least 1"}), 400
    except ValueError:
        return jsonify({"error": "Invalid number of students"}), 400

    
    # Get the "Bingo" tool details
    tool = get_tool_by_name(tools, "Bingo")
    if not tool:
        return jsonify({"error": "Tool not found"}), 500

    Tool_ID = tool.get('Tool_ID')
    Token = tool.get('Token')
    print(f"Tool ID: {Tool_ID}, Token Index: {Token}")

    # Verify tokens before proceeding
    try:
        token_verification = verify_token(auth_token, site_url,Tool_ID,Token)

        # Check if the token verification was successful
        if token_verification.get('status') == 'success':
            # Generate SAT maths quiz
            response = generate_bingo(topic, num_students)
            if response is None:
                return jsonify({'error': 'Failed to generate SAT math quiz'}), 500
            
            # Check if the response contains an error key
            if 'error' in response:
                return jsonify(response), 400
             
            # Ensure proper JSON format
            if isinstance(response, str):
                response = json.loads(response)

            result = jsonify(response)
            result.status_code = 200

            # Use the token if everything is good
            if result.status_code == 200:
                use_token(auth_token, site_url, Tool_ID, Token)

            return result
        else:
            print(token_verification)
            # Return error response based on token verification
            status_code = token_verification.get('code', 400)  # Default to 400 if not present
            return jsonify({'error': token_verification.get('message', 'Token verification failed')}), status_code

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({'error': str(e)}), 500
