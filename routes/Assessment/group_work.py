from flask import Blueprint, request, jsonify
from utils.Assessment.group_work import generate_group_work
from wordpress_api.token_verification import verify_token, use_token
from validation.input_validation import validate_string
from validation.load_tools import get_tool_by_name, load_tools_from_json
import json

group_work_bp = Blueprint("group_work", __name__)

tools = load_tools_from_json("Tools.json")

@group_work_bp.route('/group_work', methods=['POST'])
def Group_work_API():
    # Extract headers
    auth_token = request.headers.get('Authorization')
    site_url = request.headers.get('X-Site-Url')
    print(site_url, auth_token)

    # Check if the required headers are present
    if not auth_token:
        return jsonify({"error": "Missing 'Authorization' header"}), 400
    if not site_url:
        return jsonify({"error": "Missing 'X-Site-Url' header"}), 400

    # Extract data from request body
    data = request.form or request.json
    subject = data.get('subject')
    grade = data.get('grade')
    topic = data.get('topic')
    learning_objective = data.get('learning_objective')
    group_size = data.get('group_size')

    # Validate required fields
    if not all([subject, grade, topic, learning_objective, group_size]):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Validate 'Subject' field
    valid, error = validate_string(subject, "Subject", min_length=3, max_length=50)
    if not valid:
        return jsonify({"error": error}), 400
    
    # Validate 'Topic' field
    valid, error = validate_string(topic, "Topic", min_length=3, max_length=50)
    if not valid:
        return jsonify({"error": error}), 400
    
    # Validate 'Learning Objective' field
    valid, error = validate_string(learning_objective, "Learning Objective", min_length=3, max_length=500)
    if not valid:
        return jsonify({"error": error}), 400
    
    # Convert and Validate 'group_size'
    try:
        group_size = int(group_size)  # Convert to integer
        if group_size < 1 or group_size > 50:
            raise ValueError
    except ValueError:
        return jsonify({'error': "'Group size' must be an integer between 1 and 50."}), 400
    
    
    # Get the "Lesson Planner" tool details
    tool = get_tool_by_name(tools, "Group Work")
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
            # Generate group work activity
            result = generate_group_work(subject, grade, topic, learning_objective, group_size)

            if 'error' in result:
                return jsonify(result), 400
                        
            # Ensure proper JSON format
            if isinstance(result, str):
                response = json.loads(result)

            # Prepare the response
            response = jsonify(result)
            response.status_code = 200
            
            # Call use_token() only if the status code is 200
            if response.status_code == 200:
                use_token(auth_token, site_url,Tool_ID,Token)

            # Return the result
            return result

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