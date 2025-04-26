from flask import Blueprint, request, jsonify
from utils.Planner.sel_planner import sel_generation
from wordpress_api.token_verification import verify_token, use_token
from validation.input_validation import validate_string
from validation.load_tools import get_tool_by_name, load_tools_from_json
import json

sel_plan_bp = Blueprint("sel_plan", __name__)

tools = load_tools_from_json("Tools.json")

@sel_plan_bp.route('/generate_sel_plan', methods=['POST'])
def generate_sel_plan_API():
    # Extract headers
    auth_token = request.headers.get('Authorization')
    site_url = request.headers.get('X-Site-Url')
    print(site_url, auth_token)

    # Check if the required headers are present
    if not auth_token:
        return jsonify({'error': "Missing 'Authorization' header"}), 400
    if not site_url:
        return jsonify({'error': "Missing 'X-Site-Url' header"}), 400

    # Extract data from request
    data = request.get_json()
    grade = data.get('grade')
    sel_topic = data.get('sel_topic')
    learning_objectives = data.get('learning_objectives')
    duration = data.get('duration')
    
    # Validate 'topic' field
    valid, error = validate_string(sel_topic, "Topic", min_length=3, max_length=50)
    if not valid:
        return jsonify({"error": error}), 400
    
    # Validate 'topic' field
    valid, error = validate_string(learning_objectives, "Learning Objectives", min_length=3, max_length=500)
    if not valid:
        return jsonify({"error": error}), 400
    
    # Get the "Lesson Planner" tool details
    tool = get_tool_by_name(tools, "SEL Generator")
    if not tool:
        return jsonify({"error": "Tool not found"}), 500

    Tool_ID = tool.get('Tool_ID')
    Token = tool.get('Token')
    print(f"Tool ID: {Tool_ID}, Token Index: {Token}")
    # Validate the length of learning objectives
    if len(learning_objectives.split()) > 250:
        return jsonify({'error': 'Learning objectives must not exceed 250 words'}), 400

    # Verify tokens before proceeding
    try:
        token_verification = verify_token(auth_token, site_url,Tool_ID,Token)

        # Check if the token verification was successful
        if token_verification.get('status') == 'success':
            # Generate SEL plan
            response = sel_generation(grade, sel_topic, learning_objectives, duration)

            if response is None:
                return jsonify({'error': 'Failed to generate SEL plan'}), 500
            
            if 'error' in response:
                return jsonify(response), 400
            
            # Ensure proper JSON format
            if isinstance(result, str):
                result = json.loads(result)

            # Prepare and return the response
            result = jsonify(response)
            result.status_code = 200

            # Call use_token() only if the status code is 200
            if result.status_code == 200:
                use_token(auth_token, site_url,Tool_ID,Token)

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
        return jsonify({'error': str(e)}), 500
