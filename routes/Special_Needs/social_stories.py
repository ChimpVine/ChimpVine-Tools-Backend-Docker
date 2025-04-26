from flask import Blueprint, request, jsonify
from utils.Special_Needs.social_stories import social_stories
from wordpress_api.token_verification import verify_token, use_token
from validation.input_validation import validate_string
from validation.load_tools import get_tool_by_name, load_tools_from_json
import json

social_stories_bp = Blueprint("social_stories", __name__)

tools = load_tools_from_json("Tools.json")

@social_stories_bp.route('/Social_stories', methods=['POST'])
def Social_stories_API():
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
    child_name = data.get('child_name')
    child_age = data.get('child_age')
    scenario = data.get('scenario')
    behavior_challenge = data.get('behavior_challenge')
    ideal_behavior = data.get('ideal_behavior')

    # Validate required fields
    if not all([child_name, child_age, scenario, behavior_challenge, ideal_behavior]):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Validate 'Name' field
    valid, error = validate_string(child_name, "Child name", min_length=3, max_length=50)
    if not valid:
        return jsonify({"error": error}), 400
    
    # Convert and Validate 'number_of_jokes'
    try:
        child_age = int(child_age)  # Convert to integer
        if child_age < 1 or child_age > 18:
            raise ValueError
    except ValueError:
        return jsonify({'error': "'Child age' must be an integer between 1 and 18."}), 400
    
    # Validate 'Scenario' field
    valid, error = validate_string(scenario, "Scenario", min_length=3, max_length=500)
    if not valid:
        return jsonify({"error": error}), 400
    
    # Validate 'Behavior challenge' field
    valid, error = validate_string(behavior_challenge, "Behavior challenge", min_length=3, max_length=500)
    if not valid:
        return jsonify({"error": error}), 400
    
    # Validate 'Ideal behavior' field
    valid, error = validate_string(ideal_behavior, "Ideal behavior", min_length=3, max_length=500)
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
            result = social_stories(child_name, child_age, scenario, behavior_challenge, ideal_behavior)
            
            # Ensure proper JSON format
            if isinstance(result, str):
                result = json.loads(result)

            # Prepare the response
            response = jsonify(result)
            response.status_code = 200
            
            if 'error' in result:
                return jsonify(result), 400

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