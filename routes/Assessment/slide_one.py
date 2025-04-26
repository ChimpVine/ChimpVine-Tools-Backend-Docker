from flask import Blueprint, request, jsonify
import json
import time
from utils.Assessment.slide_one import first_slide
from wordpress_api.token_verification import verify_token, use_token
from validation.input_validation import validate_string
from validation.load_tools import get_tool_by_name, load_tools_from_json

slide_one_bp = Blueprint("slide_one", __name__)

tools = load_tools_from_json("Tools.json")

@slide_one_bp.route('/slide_one', methods=['POST'])
def slide_one_API():
    data = request.get_json() or request.form

    # Extract headers for token verification
    auth_token = request.headers.get('Authorization')
    site_url = request.headers.get('X-Site-Url')
    print(f"Grade: {data.get('grade')}, Topic: {data.get('topic')}, Site URL: {site_url}, Auth Token: {auth_token}")

    # Validate the presence of required headers
    if not auth_token:
        return jsonify({"error": "Missing 'Authorization' header"}), 400
    if not site_url:
        return jsonify({"error": "Missing 'X-Site-Url' header"}), 400

    # Extract data from request
    grade = data.get('grade')
    topic = data.get('topic')
    learning_objectives = data.get('learning_objectives')
    number_of_slides = data.get('number_of_slides')

    # Validate required fields
    if not all([grade, topic, learning_objectives, number_of_slides]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate 'math_topic' field (Non-gibberish and reasonable length)
    valid, error = validate_string(topic, "Topic", min_length=3, max_length=50)
    if not valid:
        return jsonify({"error": error}), 400

    # Validate 'interest' field (Non-gibberish and reasonable length)
    valid, error = validate_string(learning_objectives, "Learning objectives", min_length=3, max_length=50)
    if not valid:
        return jsonify({"error": error}), 400
    
    # Validate 'number of slides' (valid no.of slides are integers from 1 to 10)
    try:
        number_of_slides = int(number_of_slides)
        if number_of_slides < 1 or number_of_slides > 10:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Invalid number of slides. It must be an integer between 1 and 10."}), 400

    
    # Get the "Lesson Planner" tool details
    tool = get_tool_by_name(tools, "Slide Generator")
    if not tool:
        return jsonify({"error": "Tool not found"}), 500

    Tool_ID = tool.get('Tool_ID')
    Token = tool.get('Token')
    print(f"Tool ID: {Tool_ID}, Token Index: {Token}")
    try:
        # Verify token before generating slides
        token_verification = verify_token(auth_token, site_url,Tool_ID,Token)
        if token_verification.get('status') == 'success':
            # Generate slides using the slide_one function
            response = first_slide(grade, topic, learning_objectives, number_of_slides)

            # Check if the response is valid
            if response is None:
                return jsonify({'error': 'No valid response from first_slide'}), 500
            
            if 'error' in result:
                return jsonify(response), 400

            # Prepare the successful response
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
        # Log the exception for debugging
        print(f"Exception occurred: {e}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

