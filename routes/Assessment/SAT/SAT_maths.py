# routes/Gamification/make_the_word.py
from flask import Blueprint, request, jsonify
from utils.Assessment.SAT.SAT_maths import generate_math_quiz
from wordpress_api.token_verification import verify_token, use_token
from validation.input_validation import validate_string
from validation.load_tools import get_tool_by_name, load_tools_from_json
import json

SAT_maths_bp = Blueprint("SAT_maths", __name__)

tools = load_tools_from_json("Tools.json")

@SAT_maths_bp.route('/SAT_maths', methods=['POST'])
def SAT_maths_API():
    if request.method == 'POST':
        # Extract headers
        auth_token = request.headers.get('Authorization')
        site_url = request.headers.get('X-Site-Url')
        print(site_url, auth_token)

        # Check if the required headers are present
        if not auth_token:
            return jsonify({'error': "Missing 'Authorization' header"}), 400
        if not site_url:
            return jsonify({'error': "Missing 'X-Site-Url' header"}), 400

        data = request.get_json()
        topic = data.get('topic')
        difficulty = data.get('difficulty')

        # Ensure all question counts are present and valid integers
        part1_qs = data.get('No-Calculator Multiple Choice')
        part2_qs = data.get('No-Calculator Open Response')
        part3_qs = data.get('Calculator Multiple Choice')
        part4_qs = data.get('Calculator Open Response')
        print(topic, difficulty, part1_qs, part2_qs, part3_qs, part4_qs)

        try:
            # Convert to integers, defaulting to 0 if they are missing or invalid
            part1_qs = int(part1_qs)
            part2_qs = int(part2_qs)
            part3_qs = int(part3_qs)
            part4_qs = int(part4_qs)
        except (ValueError, TypeError):
            return jsonify({"error": "Number of questions must be integers."}), 400

        # Check for missing required fields but allow 0 as a valid value
        missing_fields = []
        
        if not topic:
            missing_fields.append("topic")
        if not difficulty:
            missing_fields.append("difficulty")
        if part1_qs < 0:
            missing_fields.append("No-Calculator Multiple Choice")
        if part2_qs < 0:
            missing_fields.append("No-Calculator Open Response")
        if part3_qs < 0:
            missing_fields.append("Calculator Multiple Choice")
        if part4_qs < 0:
            missing_fields.append("Calculator Open Response")

        if missing_fields:
            return jsonify({'error': f'Missing or invalid field(s): {", ".join(missing_fields)}'}), 400

        # Check if all question counts are zero
        if part1_qs == 0 and part2_qs == 0 and part3_qs == 0 and part4_qs == 0:
            return jsonify({"error": "At least one question count must be greater than 0."}), 400
        
                # Validate 'theme' field
        valid, error = validate_string(topic, "Topic", min_length=3, max_length=50)
        if not valid:
            return jsonify({"error": error}), 400
        
        valid, error = validate_string(difficulty, "Difficulty", min_length=3, max_length=50)
        if not valid:
            return jsonify({"error": error}), 400
        
        # Get the "Lesson Planner" tool details
        tool = get_tool_by_name(tools, "SAT maths")
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
                response = generate_math_quiz(topic, part1_qs, part2_qs, part3_qs, part4_qs, difficulty)
                if response is None:
                    return jsonify({'error': 'Failed to generate SAT math quiz'}), 500
                
                # Check if the response contains an error key
                if 'error' in response:
                    return jsonify(response), 400
                
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