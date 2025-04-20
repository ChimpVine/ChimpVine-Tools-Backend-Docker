from flask import Blueprint, request, jsonify
from utils.Learning.vocab import vocabulary_generation
from wordpress_api.token_verification import verify_token, use_token
from validation.input_validation import validate_string
from validation.load_tools import get_tool_by_name, load_tools_from_json
import json

vocab_list_bp = Blueprint("vocab_list", __name__)

tools = load_tools_from_json("Tools.json")

@vocab_list_bp.route('/generate-vocab-list', methods=['POST'])
def generate_vocab_list():
    data = request.form or request.json

    # Extracting headers
    auth_token = request.headers.get('Authorization')
    site_url = request.headers.get('X-Site-Url')
    print(site_url, auth_token)
    
    # Check if the required headers are present
    if not auth_token:
        return jsonify({"error": "Missing 'Authorization' header"}), 400
    if not site_url:
        return jsonify({"error": "Missing 'X-Site-Url' header"}), 400

    # Extracting data from the request
    grade_level = data.get('grade_level')
    subject = data.get('subject')
    topic = data.get('topic')
    num_words = data.get('num_words')
    difficulty_level = data.get('difficulty_level')
    print(grade_level,subject,topic,num_words, difficulty_level)

    # Validating required fields
    if not all([grade_level, subject, topic, num_words, difficulty_level]):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Validate 'theme' field
    valid, error = validate_string(subject, "Subject", min_length=3, max_length=50)
    if not valid:
        return jsonify({"error": error}), 400
    
    # Validate 'theme' field
    valid, error = validate_string(topic, "Topic", min_length=3, max_length=50)
    if not valid:
        return jsonify({"error": error}), 400

    # Convert and Validate 'number_of_words'
    try:
        num_words = int(num_words) 
        if num_words < 1 or num_words > 50:
            raise ValueError
    except ValueError:
        return jsonify({'error': "'Number of words' must be an integer between 1 and 50."}), 400
    
    # Get the "Lesson Planner" tool details
    tool = get_tool_by_name(tools, "Vocab List Generator")
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
            # If the token is valid, generate vocabulary list
            result = vocabulary_generation(grade_level, subject, topic, num_words, difficulty_level)
             # After generating the vocabulary list, return the result
             
            if 'error' in result:
                return jsonify(result), 400
            
            # Ensure proper JSON format
            if isinstance(result, str):
                result = json.loads(result)
            
            response = jsonify(result)
            response.status_code = 200 
            # Call use_token() after sending a successful response
            use_token(auth_token, site_url,Tool_ID,Token)
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