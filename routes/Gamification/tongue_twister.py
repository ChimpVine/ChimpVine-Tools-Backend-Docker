from flask import Blueprint, request, jsonify
import json
from utils.Gamification.twist import Tongue_Twister
from wordpress_api.token_verification import verify_token, use_token
from validation.input_validation import validate_string
from validation.load_tools import get_tool_by_name, load_tools_from_json

tongue_twisters_bp = Blueprint("generate_tongue_twisters", __name__)

tools = load_tools_from_json("Tools.json")

@tongue_twisters_bp.route('/generate-tongue-twisters', methods=['POST'])
def generate_tongue_twisters():
    # Extract headers
    auth_token = request.headers.get('Authorization')
    site_url = request.headers.get('X-Site-Url')
    print(site_url, auth_token)

    # Check if the required headers are present
    if not auth_token:
        return jsonify({"error": "Missing 'Authorization' header"}), 400
    if not site_url:
        return jsonify({"error": "Missing 'X-Site-Url' header"}), 400

    # Extract form data and file (supports both form and JSON inputs)
    data = request.form or request.json
    topic = data.get('topic')
    number_of_twisters = data.get('number_of_twisters')

    # Validate required fields
    if not topic or not number_of_twisters:
        return jsonify({"error": "Please provide both 'topic' and 'number_of_twisters'"}), 400
    
    # Validate 'theme' field
    valid, error = validate_string(topic, "Topic", min_length=3, max_length=50)
    if not valid:
        return jsonify({"error": error}), 400

    # Convert and Validate 'number_of_words'
    try:
        number_of_twisters = int(number_of_twisters) 
        if number_of_twisters < 1 or number_of_twisters > 50:
            raise ValueError
    except ValueError:
        return jsonify({'error': "'Number of twisters' must be an integer between 1 and 50."}), 400
        
    # Get the "Lesson Planner" tool details
    tool = get_tool_by_name(tools, "Tongue Twister")
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
            # Generate tongue twisters
            result = Tongue_Twister(topic, number_of_twisters)
            
            # Ensure proper JSON format
            if isinstance(result, str):
                result = json.loads(result)

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
   
   