from flask import Blueprint, request, jsonify
import json
from utils.Gamification.fun_maths import math_problem_generation
from wordpress_api.token_verification import verify_token, use_token
from validation.input_validation import validate_string
from validation.load_tools import get_tool_by_name, load_tools_from_json

fun_maths_bp = Blueprint("fun_maths", __name__)

tools = load_tools_from_json("Tools.json")

@fun_maths_bp.route('/fun_maths', methods=['POST'])
def generate_fun_math_API():
    # Extract headers
    auth_token = request.headers.get('Authorization')
    site_url = request.headers.get('X-Site-Url')
    print(site_url, auth_token)

    # Check if the required headers are present
    if not auth_token:
        return jsonify({"error": "Missing 'Authorization' header"}), 400
    if not site_url:
        return jsonify({"error": "Missing 'X-Site-Url' header"}), 400

    data = request.form or request.json
    grade_level = data.get('grade_level')
    math_topic = data.get('math_topic')
    interest = data.get('interest')

    if not all([grade_level, math_topic, interest]):
        return jsonify({"error": "Please provide grade_level, math_topic, and interest."}), 400
    
     # Validate 'grade_level' (grade levels are integers from 1 to 12)
    try:
        grade_level = int(grade_level)
        if grade_level < 1 or grade_level > 12:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Invalid grade_level. It must be an integer between 1 and 12."}), 400

    # Validate 'math_topic' field (Non-gibberish and reasonable length)
    valid, error = validate_string(math_topic, "Math topic", min_length=3, max_length=50)
    if not valid:
        return jsonify({"error": error}), 400

    # Validate 'interest' field (Non-gibberish and reasonable length)
    valid, error = validate_string(interest, "Interest", min_length=3, max_length=50)
    if not valid:
        return jsonify({"error": error}), 400

    # Get the "Lesson Planner" tool details
    tool = get_tool_by_name(tools, "Social Story")
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
            # Generate social story
            response = math_problem_generation(grade_level, math_topic, interest)
            # Check if the response contains an error key
            if 'error' in response:
                return jsonify(response), 400
            
            # Ensure proper JSON format
            if isinstance(response, str):
                response = json.loads(response)

            # Prepare the response
            response = jsonify(response)
            
            
            response.status_code = 200
        
            # Call use_token() only if the status code is 200
            if response.status_code == 200:
                use_token(auth_token, site_url,Tool_ID,Token)

            # Return the result
            return response

        else:
            # Print the verification response and return its status and message
            print(token_verification)
            # Extract status and message from token_verification
            status_code = token_verification.get('code', 400)  # Default to 400 if not present
            print(status_code)
            return jsonify({'error': token_verification.get('message', 'Token verification failed')}), status_code

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500