from flask import Blueprint, request, jsonify
from utils.Summarizer.text_summarizer import summary_generation
from wordpress_api.token_verification import verify_token, use_token
from validation.load_tools import get_tool_by_name, load_tools_from_json
import re
import json

text_summarizer_bp = Blueprint("text_summarizer", __name__)

tools = load_tools_from_json("Tools.json")

@text_summarizer_bp.route('/text_summarizer', methods=['POST'])
def text_summarizer_API():
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
    data = request.get_json() or request.form
    text = data.get('text')
    summary_format = data.get('summary_format')

    # Validate required fields
    if not all([text, summary_format]):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check for special characters (excluding basic punctuation)
    if re.search(r'[^A-Za-z0-9\s.,!?\'"-]', text):
        return jsonify({'error': 'Invalid characters detected. Please remove special symbols like #, $.'}), 400

    # Check word count limit and ensure there is at least one word  
    word_count = len(text.split())
    if word_count == 0:
        return jsonify({'error': 'Text cannot be empty. Please enter some words.'}), 400
    elif word_count > 1000:
        return jsonify({'error': 'Exceeded word limit. Please enter 1000 words only.'}), 400
    
    # Get the "Lesson Planner" tool details
    tool = get_tool_by_name(tools, "Text Summarizer")
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
            # Generate summary
            response = summary_generation(text, summary_format)

            if response is None:
                return jsonify({'error': 'No valid response from summary_generation'}), 500
            
            # Ensure proper JSON format
            if isinstance(result, str):
                response = json.loads(response)

            if 'error' in response:
                return jsonify(response), 400
            
            # Prepare and return the summary response
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
