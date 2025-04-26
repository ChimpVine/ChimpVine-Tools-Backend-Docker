from flask import Blueprint, request, jsonify
import json
import re
from utils.Summarizer.youtube import YT_summary_generation
from wordpress_api.token_verification import verify_token, use_token
from validation.load_tools import get_tool_by_name, load_tools_from_json

YT_summary_bp = Blueprint("YT_summary", __name__)

tools = load_tools_from_json("Tools.json")

@YT_summary_bp.route('/YT_summary', methods=['POST'])
def get_response():
    try:
        # Extract headers
        auth_token = request.headers.get('Authorization')
        site_url = request.headers.get('X-Site-Url')
        print(site_url, auth_token)

        # Check if the required headers are present
        if not auth_token:
            return jsonify({'error': "Missing 'Authorization' header"}), 400
        if not site_url:
            return jsonify({'error': "Missing 'X-Site-Url' header"}), 400

        # Get the topic input from the user
        topic = request.json.get('topic', '').strip()

        # Validate input
        if not topic:
            return jsonify({"error": "Video Transcript cannot be empty"}), 400
        if not re.search(r'[a-zA-Z]', topic):
            return jsonify({"error": "Video Transcript cannot be pure symbols or spaces"}), 400

        # Get the "YouTube Summarizer" tool details
        tool = get_tool_by_name(tools, "YT Summarizer")
        if not tool:
            return jsonify({"error": "Tool not found"}), 500

        Tool_ID = tool.get('Tool_ID')
        Token = tool.get('Token')
        print(f"Tool ID: {Tool_ID}, Token Index: {Token}")

        # Verify token
        token_verification = verify_token(auth_token, site_url, Tool_ID, Token)
        if token_verification.get('status') == 'success':
            # Generate summary
            response_text = YT_summary_generation(topic)
            
            # Ensure proper JSON format
            if isinstance(response_text, str):
                response_text = json.loads(response_text)

            # Basic check in case response is None
            if response_text is None:
                return jsonify({'error': 'No valid response from YT_summary_generation'}), 500

            # Call use_token only after successful response
            use_token(auth_token, site_url, Tool_ID, Token)

            return response_text
        else:
            print(token_verification)
            status_code = token_verification.get('code', 400)
            return jsonify({'error': token_verification.get('message', 'Token verification failed')}), status_code

    except Exception as e:
        print("Error occurred:", str(e))
        return jsonify({"error": str(e)}), 500
